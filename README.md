# Attendance Management (Flask + HTML/CSS/JS)

## Overview
Simple attendance management web app using Flask (Python) for the backend, SQLite for storage, and vanilla HTML/CSS/JS for the frontend.

Features:
- Add / list students
- Mark attendance for a date (Present / Absent)
- View attendance by date or by student
- Export attendance as CSV
- Simple, dependency-light stack

## Run locally (Linux / macOS / Windows PowerShell)
1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate     # Windows (PowerShell)
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize DB & run server:
   ```bash
   python app.py
   ```
   The server runs on http://127.0.0.1:5000

## Project structure
- app.py                 -> Flask backend (API + templates)
- requirements.txt
- templates/
    - layout.html
    - index.html
    - students.html
    - attendance.html
- static/
    - css/style.css
    - js/main.js

## Notes
- The app uses SQLite (file `attendance.db`) created automatically on first run.
- This is a simple educational starter project. For production:
  - Add authentication
  - Use migrations (Flask-Migrate / Alembic)
  - Use HTTPS and a production WSGI server
