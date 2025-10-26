from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import json
from priority_scorer import PriorityScorer
from email_service import EmailService
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
priority_scorer = PriorityScorer()
email_service = EmailService()

DB_PATH = 'lab_occupancy.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"}), 200

@app.route('/api/labs', methods=['GET'])
def get_labs():
    """Get all available labs"""
    conn = get_db_connection()
    labs = conn.execute('SELECT * FROM labs WHERE status = "active"').fetchall()
    conn.close()
    
    return jsonify([dict(lab) for lab in labs]), 200

@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    """Check if a lab is available for a specific date and time"""
    data = request.json
    lab_number = data.get('lab_number')
    date = data.get('date')
    session = data.get('session')  # morning/afternoon/evening
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    conn = get_db_connection()
    
    # Check timetable (regular classes)
    timetable_query = '''
        SELECT * FROM timetables 
        WHERE room_number = ? AND date = ? AND session = ?
    '''
    timetable_conflict = conn.execute(timetable_query, (lab_number, date, session)).fetchone()
    
    # Check reservations
    reservation_query = '''
        SELECT * FROM reservations 
        WHERE lab_number = ? AND date = ? AND status IN ('approved', 'pending')
        AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
    '''
    reservation_conflict = conn.execute(
        reservation_query, 
        (lab_number, date, start_time, start_time, end_time, end_time)
    ).fetchone()
    
    conn.close()
    
    if timetable_conflict:
        return jsonify({
            "available": False,
            "reason": "occupied_by_class",
            "details": {
                "class": timetable_conflict['class'],
                "section": timetable_conflict['section'],
                "subject": timetable_conflict['subject'],
                "faculty_name": timetable_conflict['faculty_name']
            }
        }), 200
    
    if reservation_conflict:
        return jsonify({
            "available": False,
            "reason": "reserved",
            "details": {
                "purpose": reservation_conflict['purpose'],
                "reserved_by": reservation_conflict['user_email']
            }
        }), 200
    
    return jsonify({
        "available": True,
        "lab_number": lab_number,
        "date": date,
        "session": session
    }), 200

@app.route('/api/suggest-alternatives', methods=['POST'])
def suggest_alternatives():
    """Suggest alternative labs or time slots"""
    data = request.json
    requested_lab = data.get('lab_number')
    date = data.get('date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    num_participants = int(data.get('num_participants', 30))
    
    conn = get_db_connection()
    
    # Get all labs that can accommodate the number of participants
    labs = conn.execute(
        'SELECT * FROM labs WHERE capacity >= ? AND status = "active"',
        (num_participants,)
    ).fetchall()
    
    alternatives = []
    
    for lab in labs:
        # Check if this lab is available at the requested time
        timetable_conflict = conn.execute(
            'SELECT * FROM timetables WHERE room_number = ? AND date = ?',
            (lab['lab_number'], date)
        ).fetchone()
        
        reservation_conflict = conn.execute(
            '''SELECT * FROM reservations 
               WHERE lab_number = ? AND date = ? AND status IN ('approved', 'pending')
               AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))''',
            (lab['lab_number'], date, start_time, start_time, end_time, end_time)
        ).fetchone()
        
        if not timetable_conflict and not reservation_conflict:
            alternatives.append({
                "lab_number": lab['lab_number'],
                "building": lab['building'],
                "floor": lab['floor'],
                "capacity": lab['capacity'],
                "equipment": lab['equipment'],
                "is_original": lab['lab_number'] == requested_lab
            })
    
    # If no alternatives in same slot, suggest different time slots for requested lab
    time_alternatives = []
    if len(alternatives) == 0:
        time_slots = [
            ("09:00", "11:00", "morning"),
            ("11:00", "13:00", "morning"),
            ("14:00", "16:00", "afternoon"),
            ("16:00", "18:00", "afternoon")
        ]
        
        for slot_start, slot_end, session in time_slots:
            if slot_start == start_time and slot_end == end_time:
                continue
            
            conflict = conn.execute(
                '''SELECT * FROM reservations 
                   WHERE lab_number = ? AND date = ? AND status IN ('approved', 'pending')
                   AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))''',
                (requested_lab, date, slot_start, slot_start, slot_end, slot_end)
            ).fetchone()
            
            if not conflict:
                time_alternatives.append({
                    "start_time": slot_start,
                    "end_time": slot_end,
                    "session": session
                })
    
    conn.close()
    
    return jsonify({
        "alternative_labs": alternatives[:5],  # Top 5 alternatives
        "alternative_times": time_alternatives[:3]  # Top 3 time slots
    }), 200

@app.route('/api/reserve-lab', methods=['POST'])
def reserve_lab():
    """Submit a lab reservation request"""
    data = request.json
    
    required_fields = ['lab_number', 'date', 'start_time', 'end_time', 
                      'num_participants', 'purpose', 'description', 'user_email', 'user_name']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Get lab capacity
    conn = get_db_connection()
    lab = conn.execute('SELECT capacity FROM labs WHERE lab_number = ?', (data['lab_number'],)).fetchone()
    
    if not lab:
        conn.close()
        return jsonify({"error": "Lab not found"}), 404
    
    lab_capacity = lab['capacity']
    
    # Calculate priority score with new fair system
    scoring_result = priority_scorer.calculate_priority(
        purpose=data['purpose'],
        description=data['description'],
        num_participants=int(data['num_participants']),
        lab_capacity=lab_capacity,
        urgency=data.get('urgency', 'normal'),
        user_email=data.get('user_email'),
        booking_date=data.get('date'),
        has_proof=data.get('has_proof', False),
        proof_type=data.get('proof_type'),
        user_role=data.get('user_role', 'student')
    )
    
    logger.info(f"Fair scoring result: {scoring_result}")
    
    # Check if auto-rejected
    if not scoring_result.get('accepted'):
        # Generate explanation
        explanation = priority_scorer.explain(scoring_result)
        
        # Get alternative suggestions
        alternatives = []
        try:
            # Suggest alternative labs or times
            alt_response = suggest_alternatives()
            alternatives = json.loads(alt_response[0].data) if alt_response else {}
        except:
            alternatives = {"alternative_labs": [], "alternative_times": []}
        
        conn.close()
        
        return jsonify({
            "success": False,
            "rejected": True,
            "score": scoring_result['score'],
            "breakdown": scoring_result['breakdown'],
            "flags": scoring_result['flags'],
            "reason": explanation.get('verdict', 'Score below minimum threshold'),
            "recommendations": explanation.get('recommendation', ''),
            "detailed_explanation": {
                "capacity_issue": explanation['breakdown_explanation'].get('capacity_match', ''),
                "authenticity_issue": explanation['breakdown_explanation'].get('authenticity', ''),
                "timing_issue": explanation['breakdown_explanation'].get('timing', ''),
                "fairness_issue": explanation['breakdown_explanation'].get('fairness', '')
            },
            "flags_detail": explanation.get('flags_explanation', ''),
            "alternatives": alternatives,
            "message": f"Unable to approve: {explanation.get('verdict', 'Score too low')}. See recommendations below."
        }), 400
    
    priority_score = scoring_result['score']
    
    # Check if slot is available
    conflict = conn.execute(
        '''SELECT * FROM reservations 
           WHERE lab_number = ? AND date = ? AND status IN ('approved', 'pending')
           AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))''',
        (data['lab_number'], data['date'], data['start_time'], 
         data['start_time'], data['end_time'], data['end_time'])
    ).fetchone()
    
    # Auto-approve if score >= 65 and no conflict
    status = 'pending'
    if priority_score >= 65 and not conflict:
        status = 'approved'
    elif conflict:
        # Check if current request has higher priority
        conflicting_score = conflict['priority_score']
        if priority_score > conflicting_score + 15:  # Significantly higher priority
            # Update conflicting reservation to rejected
            conn.execute(
                'UPDATE reservations SET status = "rejected" WHERE id = ?',
                (conflict['id'],)
            )
            conn.commit()
            status = 'approved'
            
            # Send rejection email to conflicting user
            email_service.send_rejection_email(
                conflict['user_email'],
                conflict['lab_number'],
                conflict['date'],
                conflict['start_time'],
                conflict['end_time'],
                "Higher priority request received"
            )
    
    # Insert reservation
    cursor = conn.execute(
        '''INSERT INTO reservations 
           (lab_number, date, start_time, end_time, num_participants, purpose, 
            description, user_email, user_name, priority_score, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['lab_number'], data['date'], data['start_time'], data['end_time'],
         int(data['num_participants']), data['purpose'], data['description'],
         data['user_email'], data['user_name'], priority_score, status,
         datetime.now().isoformat())
    )
    
    reservation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Send confirmation email
    if status == 'approved':
        email_service.send_approval_email(
            data['user_email'],
            data['lab_number'],
            data['date'],
            data['start_time'],
            data['end_time'],
            reservation_id
        )
    else:
        # Suggest alternatives
        alternatives_response = suggest_alternatives()
        alternatives = json.loads(alternatives_response[0].data)
        
        email_service.send_pending_email(
            data['user_email'],
            data['lab_number'],
            data['date'],
            data['start_time'],
            data['end_time'],
            alternatives
        )
    
    return jsonify({
        "success": True,
        "reservation_id": reservation_id,
        "status": status,
        "priority_score": priority_score,
        "breakdown": scoring_result['breakdown'],
        "flags": scoring_result['flags'],
        "message": f"Reservation {status}. Score: {priority_score}/100"
    }), 201

@app.route('/api/reservations/<user_email>', methods=['GET'])
def get_user_reservations(user_email):
    """Get all reservations for a user"""
    conn = get_db_connection()
    reservations = conn.execute(
        'SELECT * FROM reservations WHERE user_email = ? ORDER BY created_at DESC',
        (user_email,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(r) for r in reservations]), 200

@app.route('/api/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    """Modify a reservation (within constraints)"""
    data = request.json
    
    conn = get_db_connection()
    reservation = conn.execute(
        'SELECT * FROM reservations WHERE id = ?',
        (reservation_id,)
    ).fetchone()
    
    if not reservation:
        conn.close()
        return jsonify({"error": "Reservation not found"}), 404
    
    # Check if modification is allowed (e.g., at least 24 hours before)
    reservation_datetime = datetime.fromisoformat(f"{reservation['date']} {reservation['start_time']}")
    now = datetime.now()
    
    if reservation_datetime - now < timedelta(hours=24):
        conn.close()
        return jsonify({
            "error": "Cannot modify reservation less than 24 hours before scheduled time"
        }), 400
    
    # Update allowed fields
    allowed_fields = ['start_time', 'end_time', 'num_participants', 'description']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    
    if updates:
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [reservation_id]
        
        conn.execute(
            f'UPDATE reservations SET {set_clause}, status = "pending" WHERE id = ?',
            values
        )
        conn.commit()
        
        # Send modification email
        email_service.send_modification_email(
            reservation['user_email'],
            reservation['lab_number'],
            updates
        )
    
    conn.close()
    
    return jsonify({"success": True, "message": "Reservation updated"}), 200

@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def cancel_reservation(reservation_id):
    """Cancel a reservation"""
    conn = get_db_connection()
    reservation = conn.execute(
        'SELECT * FROM reservations WHERE id = ?',
        (reservation_id,)
    ).fetchone()
    
    if not reservation:
        conn.close()
        return jsonify({"error": "Reservation not found"}), 404
    
    # Update status to cancelled
    conn.execute(
        'UPDATE reservations SET status = "cancelled" WHERE id = ?',
        (reservation_id,)
    )
    conn.commit()
    conn.close()
    
    # Send cancellation email
    email_service.send_cancellation_email(
        reservation['user_email'],
        reservation['lab_number'],
        reservation['date'],
        reservation['start_time'],
        reservation['end_time']
    )
    
    return jsonify({"success": True, "message": "Reservation cancelled"}), 200

@app.route('/api/admin/reservations', methods=['GET'])
def get_all_reservations():
    """Get all reservations (admin view)"""
    status_filter = request.args.get('status')
    
    conn = get_db_connection()
    
    if status_filter:
        reservations = conn.execute(
            'SELECT * FROM reservations WHERE status = ? ORDER BY date, start_time',
            (status_filter,)
        ).fetchall()
    else:
        reservations = conn.execute(
            'SELECT * FROM reservations ORDER BY date, start_time'
        ).fetchall()
    
    conn.close()
    
    return jsonify([dict(r) for r in reservations]), 200

@app.route('/api/admin/approve-reservation/<int:reservation_id>', methods=['POST'])
def approve_reservation(reservation_id):
    """Admin manually approves a reservation"""
    conn = get_db_connection()
    
    reservation = conn.execute(
        'SELECT * FROM reservations WHERE id = ?',
        (reservation_id,)
    ).fetchone()
    
    if not reservation:
        conn.close()
        return jsonify({"error": "Reservation not found"}), 404
    
    conn.execute(
        'UPDATE reservations SET status = "approved" WHERE id = ?',
        (reservation_id,)
    )
    conn.commit()
    conn.close()
    
    # Send approval email
    email_service.send_approval_email(
        reservation['user_email'],
        reservation['lab_number'],
        reservation['date'],
        reservation['start_time'],
        reservation['end_time'],
        reservation_id
    )
    
    return jsonify({"success": True, "message": "Reservation approved"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

