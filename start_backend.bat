@echo off
echo ================================
echo Starting Lab Reservation Backend
echo ================================
echo.

cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

if not exist "lab_occupancy.db" (
    echo Initializing database...
    python init_db.py
)

echo.
echo ================================
echo Starting Flask Server...
echo Backend will run on http://localhost:5000
echo ================================
echo.

python app.py

pause

