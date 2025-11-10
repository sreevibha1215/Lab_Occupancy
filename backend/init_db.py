import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = 'lab_occupancy.db'

def init_database():
    """Initialize database with schema and dummy data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS labs')
    cursor.execute('DROP TABLE IF EXISTS timetables')
    cursor.execute('DROP TABLE IF EXISTS reservations')
    
    # Create labs table
    cursor.execute('''
        CREATE TABLE labs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lab_number TEXT UNIQUE NOT NULL,
            building TEXT NOT NULL,
            floor INTEGER NOT NULL,
            capacity INTEGER NOT NULL,
            equipment TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Create timetables table (regular classes)
    cursor.execute('''
        CREATE TABLE timetables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL,
            date TEXT NOT NULL,
            session TEXT NOT NULL,
            class TEXT NOT NULL,
            section TEXT NOT NULL,
            batch TEXT NOT NULL,
            subject TEXT NOT NULL,
            faculty_name TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT
        )
    ''')
    
    # Create reservations table
    cursor.execute('''
        CREATE TABLE reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lab_number TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            num_participants INTEGER NOT NULL,
            purpose TEXT NOT NULL,
            description TEXT,
            user_email TEXT NOT NULL,
            user_name TEXT NOT NULL,
            priority_score REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (lab_number) REFERENCES labs(lab_number)
        )
    ''')
    
    print("✅ Database schema created")
    
    # Insert dummy labs data
    labs_data = [
        ('E401', 'Engineering Block', 4, 60, 'Computers, Projector, Whiteboard', 'active'),
        ('E402', 'Engineering Block', 4, 50, 'Computers, Projector', 'active'),
        ('E403', 'Engineering Block', 4, 45, 'Computers, Smart Board', 'active'),
        ('E301', 'Engineering Block', 3, 40, 'Computers, Projector', 'active'),
        ('E302', 'Engineering Block', 3, 40, 'Computers', 'active'),
        ('E201', 'Engineering Block', 2, 35, 'Computers, Projector', 'active'),
        ('E202', 'Engineering Block', 2, 30, 'Computers', 'active'),
        ('CS-Lab1', 'CS Block', 1, 55, 'High-end Workstations, Multiple Monitors', 'active'),
        ('CS-Lab2', 'CS Block', 1, 55, 'Workstations, Network Equipment', 'active'),
        ('CS-Lab3', 'CS Block', 2, 45, 'Computers, Server Rack', 'active'),
        ('ECE-Lab1', 'ECE Block', 1, 40, 'Oscilloscopes, Signal Generators', 'active'),
        ('ECE-Lab2', 'ECE Block', 1, 40, 'VLSI Equipment, Testing Boards', 'active'),
        ('Mech-Lab1', 'Mechanical Block', 1, 30, 'Workbenches, Tools', 'active'),
        ('Seminar-Hall', 'Main Building', 2, 100, 'Projector, Audio System, Stage', 'active'),
        ('Conference-Room', 'Admin Block', 3, 25, 'Video Conferencing, Whiteboard', 'active')
    ]
    
    cursor.executemany('''
        INSERT INTO labs (lab_number, building, floor, capacity, equipment, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', labs_data)
    
    print(f"✅ Inserted {len(labs_data)} labs")
    
    # Insert dummy timetable data (for next 30 days)
    timetables_data = []
    base_date = datetime.now().date()
    
    # Define regular class schedule
    class_schedule = [
        ('E401', 'morning', 'CSDS', 'A', '2022', 'Operating Systems', 'Dr. Madhuri', '09:00', '11:00'),
        ('E401', 'afternoon', 'CSE', 'B', '2023', 'Data Structures', 'Dr. Ramesh', '14:00', '16:00'),
        ('E402', 'morning', 'ECE', 'A', '2022', 'Digital Signal Processing', 'Dr. Kavitha', '09:00', '11:00'),
        ('E403', 'morning', 'IT', 'A', '2023', 'Database Management', 'Dr. Suresh', '09:00', '11:00'),
        ('E301', 'afternoon', 'CSE', 'C', '2024', 'Programming Fundamentals', 'Dr. Priya', '14:00', '16:00'),
        ('CS-Lab1', 'morning', 'CSDS', 'B', '2022', 'Machine Learning', 'Dr. Anil', '09:00', '12:00'),
        ('CS-Lab2', 'afternoon', 'CSE', 'A', '2023', 'Computer Networks', 'Dr. Vijay', '14:00', '17:00'),
        ('ECE-Lab1', 'morning', 'ECE', 'B', '2023', 'VLSI Design', 'Dr. Lakshmi', '09:00', '12:00'),
    ]
    
    # Generate schedule for next 30 days (weekdays only)
    for day_offset in range(30):
        current_date = base_date + timedelta(days=day_offset)
        
        # Skip weekends
        if current_date.weekday() >= 5:
            continue
        
        date_str = current_date.isoformat()
        
        # Add classes for this day
        for class_info in class_schedule:
            room, session, cls, section, batch, subject, faculty, start, end = class_info
            timetables_data.append((room, date_str, session, cls, section, batch, subject, faculty, start, end))
    
    cursor.executemany('''
        INSERT INTO timetables (room_number, date, session, class, section, batch, subject, faculty_name, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', timetables_data)
    
    print(f"✅ Inserted {len(timetables_data)} timetable entries")
    
    # Insert dummy reservations
    reservations_data = [
        # Approved reservations
        ('E202', (base_date + timedelta(days=2)).isoformat(), '14:00', '16:00', 25, 
         'workshop', 'Python programming workshop for beginners', 'student1@vnrvjiet.in', 
         'Rahul Kumar', 68.5, 'approved', datetime.now().isoformat()),
        
        ('Seminar-Hall', (base_date + timedelta(days=5)).isoformat(), '10:00', '13:00', 80,
         'event', 'Annual technical symposium - CodeFest 2025', 'event.coordinator@vnrvjiet.in',
         'Dr. Suresh Babu', 85.2, 'approved', datetime.now().isoformat()),
        
        ('Conference-Room', (base_date + timedelta(days=3)).isoformat(), '15:00', '17:00', 20,
         'meeting', 'Department faculty meeting to discuss curriculum updates', 'hod.cse@vnrvjiet.in',
         'Dr. Ramesh Kumar', 55.0, 'approved', datetime.now().isoformat()),
        
        ('CS-Lab3', (base_date + timedelta(days=7)).isoformat(), '09:00', '12:00', 40,
         'exam', 'Mid-term practical examination for Data Structures course', 'exam.cell@vnrvjiet.in',
         'Dr. Madhuri', 92.0, 'approved', datetime.now().isoformat()),
        
        # Pending reservations
        ('E301', (base_date + timedelta(days=10)).isoformat(), '16:00', '18:00', 30,
         'practice', 'Coding competition practice session for students', 'coding.club@vnrvjiet.in',
         'Priya Sharma', 48.0, 'pending', datetime.now().isoformat()),
        
        ('ECE-Lab2', (base_date + timedelta(days=8)).isoformat(), '14:00', '17:00', 35,
         'workshop', 'PCB design workshop with hands-on training', 'ece.society@vnrvjiet.in',
         'Kiran Reddy', 71.5, 'pending', datetime.now().isoformat()),
        
        # Historical completed reservations
        ('E201', (base_date - timedelta(days=5)).isoformat(), '14:00', '16:00', 28,
         'lecture', 'Guest lecture on Cloud Computing by industry expert', 'cs.dept@vnrvjiet.in',
         'Dr. Vijay', 62.0, 'approved', (datetime.now() - timedelta(days=6)).isoformat()),
        
        ('Seminar-Hall', (base_date - timedelta(days=10)).isoformat(), '10:00', '16:00', 150,
         'event', 'Intercollegiate hackathon - 24 hour coding event', 'hackathon@vnrvjiet.in',
         'Event Committee', 88.0, 'approved', (datetime.now() - timedelta(days=15)).isoformat()),
    ]
    
    cursor.executemany('''
        INSERT INTO reservations 
        (lab_number, date, start_time, end_time, num_participants, purpose, description, 
         user_email, user_name, priority_score, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', reservations_data)
    
    print(f"✅ Inserted {len(reservations_data)} reservations")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Database initialized successfully!")
    print(f"📁 Database file: {DB_PATH}")

if __name__ == '__main__':
    init_database()

