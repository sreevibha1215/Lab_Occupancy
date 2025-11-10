# Lab Occupancy & Reservation System

A comprehensive lab management system with intelligent reservation handling, priority-based approval, and real-time availability checking.

## 🌟 Features

### Frontend Features
- **User Authentication**: Login system with admin/user roles
- **Check Lab Availability**: Real-time lab availability checking with time slots
- **Reserve Labs**: Comprehensive reservation form with:
  - Lab selection
  - Date and time range
  - Number of participants
  - Purpose and urgency level
  - Detailed description
- **My Reservations**: View, manage, and cancel reservations
- **Admin Dashboard**: Manage timetables and view all reservations
- **Responsive Design**: Beautiful glassmorphism UI with Framer Motion animations

### Backend Features
- **Intelligent Priority Scoring**:
  - Rule-based scoring for purpose categories
  - DistilBERT semantic analysis of descriptions
  - Participant count weighting
  - Urgency level consideration
- **Auto-Approval System**: High-priority requests automatically approved
- **Conflict Detection**: Checks for timetable and reservation conflicts
- **Alternative Suggestions**: Recommends alternative labs or time slots
- **Email Notifications**: Automated emails for approvals, rejections, and modifications
- **24-Hour Modification Rule**: Reservations can only be modified 24+ hours before

## 📁 Project Structure

```
Lab_Occupancy/
├── backend/
│   ├── app.py                 # Flask API with all routes
│   ├── priority_scorer.py     # Priority scoring with DistilBERT
│   ├── email_service.py       # Email notification service
│   ├── init_db.py             # Database initialization script
│   ├── requirements.txt       # Python dependencies
│   └── lab_occupancy.db       # SQLite database (created after init)
│
├── src/
│   ├── pages/
│   │   ├── Login.jsx          # Login page
│   │   ├── UserDashboard.jsx  # User dashboard
│   │   ├── CheckLab.jsx       # Lab availability checker
│   │   ├── ReserveLab.jsx     # Lab reservation form
│   │   ├── MyReservations.jsx # User reservations management
│   │   └── AdminDashboard.jsx # Admin timetable management
│   ├── components/
│   │   └── Navbar.jsx         # Navigation bar
│   └── App.jsx                # Main app with routing
│
└── package.json
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- pip

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
```

3. **Activate virtual environment**:
- Windows:
```bash
venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Initialize database with dummy data**:
```bash
python init_db.py
```

6. **Start Flask server**:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to project root**:
```bash
cd ..
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

## 📊 Database Schema

### Labs Table
- Lab details: number, building, floor, capacity, equipment
- 15 labs with various capacities (25-100 people)

### Timetables Table
- Regular class schedule for next 30 days
- Includes: room, date, session, class, section, subject, faculty

### Reservations Table
- All reservation requests with:
  - Lab details, time range, participants
  - Purpose, description, urgency
  - Priority score, status, timestamps

## 🎯 Priority Scoring System

The system uses a multi-factor scoring algorithm (0-100):

1. **Purpose Category** (0-40 points):
   - Emergency: 40
   - Exam: 35
   - Lecture: 30
   - Workshop: 28
   - Event: 25
   - Meeting: 20
   - Practice: 15
   - Other: 10

2. **Semantic Analysis** (0-30 points):
   - DistilBERT analyzes description text
   - Matches against high-priority keywords
   - Considers: urgency, importance, deadline terms

3. **Participants** (0-15 points):
   - 60+: 15 points
   - 40-59: 12 points
   - 25-39: 9 points
   - 15-24: 6 points
   - <15: 3 points

4. **Urgency Level** (0-15 points):
   - High: 15
   - Medium: 10
   - Normal: 5
   - Low: 0

### Auto-Approval Rules
- Score ≥ 75 + No conflicts = Auto-approved
- Score > existing + 20 points = Overrides lower priority
- Otherwise = Pending admin review

## 🔑 Login Credentials

### Admin
- Username: `admin`
- Password: `admin123`

### User
- Username: `user`
- Password: `user123`

## 📧 Email Notifications

The system sends emails for:
- ✅ Reservation approved
- ⏳ Reservation pending (with alternatives)
- ❌ Reservation rejected
- ✏️ Reservation modified
- 🚫 Reservation cancelled

*Note: Currently in testing mode (emails logged to console)*

## 🛠️ API Endpoints

### Public Endpoints
- `GET /api/health` - Health check
- `GET /api/labs` - Get all active labs
- `POST /api/check-availability` - Check lab availability
- `POST /api/suggest-alternatives` - Get alternative labs/times
- `POST /api/reserve-lab` - Submit reservation request
- `GET /api/reservations/:email` - Get user's reservations
- `PUT /api/reservations/:id` - Modify reservation
- `DELETE /api/reservations/:id` - Cancel reservation

### Admin Endpoints
- `GET /api/admin/reservations` - Get all reservations
- `POST /api/admin/approve-reservation/:id` - Manually approve

## 🎨 User Interface

### Pages
1. **Login** - Authentication portal
2. **User Dashboard** - Welcome screen with quick actions
3. **Check Lab Availability** - Real-time availability checker
4. **Reserve Lab** - Comprehensive reservation form
5. **My Reservations** - View and manage reservations
6. **Admin Dashboard** - Timetable management

### Features
- Glassmorphism design
- Framer Motion animations
- Responsive mobile layout
- Real-time validation
- Loading states
- Success/error notifications

## 📦 Dummy Data Included

- **15 Labs**: E401-E403, CS-Lab1-3, ECE-Lab1-2, etc.
- **Regular Classes**: 8 classes scheduled for weekdays
- **Sample Reservations**: Approved, pending, and historical
- **Next 30 Days**: Timetable populated for upcoming month

## 🧪 Testing the System

1. **Login as user** with credentials above
2. **Check availability** for E401 on a weekday morning (should be occupied)
3. **Reserve a lab**:
   - Try emergency purpose with urgent description
   - Should get high priority score
   - May be auto-approved if score ≥ 75
4. **View reservations** with your email
5. **Cancel reservation** (if > 24 hours away)

## 🔧 Configuration

### Backend Configuration
Edit `backend/email_service.py` to configure:
- SMTP server settings
- Sender email credentials
- Toggle testing_mode (True = log only, False = send emails)

### Frontend Configuration
Edit API_URL in each page to change backend endpoint:
```javascript
const API_URL = "http://localhost:5000/api";
```

## 🚨 Troubleshooting

### Backend Issues
- **Database error**: Run `python init_db.py` again
- **Import errors**: Ensure virtual environment is activated
- **Port conflict**: Change port in `app.py` (default 5000)

### Frontend Issues
- **API connection**: Verify backend is running
- **CORS errors**: Ensured by flask-cors, check backend logs
- **Build errors**: Clear node_modules, reinstall

### DistilBERT Issues
If DistilBERT fails to load:
- System falls back to keyword-based scoring
- Check internet connection (first download)
- May require ~500MB for model download

## 📝 Future Enhancements

- [ ] Real email integration (SMTP configuration)
- [ ] User registration system
- [ ] Calendar view for reservations
- [ ] Conflict resolution wizard
- [ ] SMS notifications
- [ ] QR code check-in system
- [ ] Analytics dashboard
- [ ] Export reports (PDF/Excel)
- [ ] Recurring reservations
- [ ] Equipment checkout system

## 👥 Authors

- VNRVJIET Lab Occupancy System Team

## 📄 License

This project is for educational purposes.

---

**Need Help?** Check the console logs for detailed error messages and API responses.

