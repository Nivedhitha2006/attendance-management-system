from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import csv
import io
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


db_path = os.path.join(BASE_DIR, 'attendance.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    def to_dict(self):
        return {'id': self.id, 'roll_no': self.roll_no, 'name': self.name}

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(16), nullable=False)  # 'Present' or 'Absent'
    student = db.relationship('Student', backref='attendances')
    def to_dict(self):
        return {'id': self.id, 'student_id': self.student_id, 'date': self.date.isoformat(), 'status': self.status}

# initialize DB with sample data if not present
# initialize DB with sample data if not present
# initialize DB with sample data if not present
with app.app_context():
    db.create_all()
    if Student.query.count() == 0:
        s1 = Student(roll_no='S001', name='Alice')
        s2 = Student(roll_no='S002', name='Bob')
        s3 = Student(roll_no='S003', name='Charlie')
        db.session.add_all([s1, s2, s3])
        db.session.commit()

# Routes - pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def students_page():
    return render_template('students.html')

@app.route('/attendance')
def attendance_page():
    return render_template('attendance.html')

# API endpoints
@app.route('/api/students', methods=['GET','POST'])
def api_students():
    if request.method == 'GET':
        students = Student.query.order_by(Student.roll_no).all()
        return jsonify([s.to_dict() for s in students])
    data = request.json or request.form
    roll_no = data.get('roll_no')
    name = data.get('name')
    if not roll_no or not name:
        return jsonify({'error':'roll_no and name required'}), 400
    if Student.query.filter_by(roll_no=roll_no).first():
        return jsonify({'error':'roll_no already exists'}), 400
    s = Student(roll_no=roll_no, name=name)
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201

@app.route('/api/attendance', methods=['GET','POST'])
def api_attendance():
    if request.method == 'GET':
        # optional filters: date (YYYY-MM-DD) or student_id
        date_str = request.args.get('date')
        student_id = request.args.get('student_id', type=int)
        q = Attendance.query
        if date_str:
            try:
                d = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error':'invalid date format, use YYYY-MM-DD'}), 400
            q = q.filter_by(date=d)
        if student_id:
            q = q.filter_by(student_id=student_id)
        records = q.order_by(Attendance.date.desc()).all()
        return jsonify([r.to_dict() for r in records])
    # POST -> mark attendance for a date (accepts JSON or form)
    data = request.json or request.form
    date_str = data.get('date')
    entries = data.get('entries')  # expected: list of {"student_id":.., "status":"Present"/"Absent"}
    if not date_str or not entries:
        return jsonify({'error':'date and entries required'}), 400
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error':'invalid date format, use YYYY-MM-DD'}), 400
    # remove existing for that date for the given student ids to avoid duplicates
    student_ids = [int(e['student_id']) for e in entries]
    Attendance.query.filter(Attendance.student_id.in_(student_ids), Attendance.date==d).delete(synchronize_session=False)
    for e in entries:
        a = Attendance(student_id=int(e['student_id']), date=d, status=e['status'])
        db.session.add(a)
    db.session.commit()
    return jsonify({'msg':'saved'}), 201

@app.route('/attendance/export')
def export_attendance():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error':'date param required (YYYY-MM-DD)'}), 400
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error':'invalid date format, use YYYY-MM-DD'}), 400
    records = Attendance.query.filter_by(date=d).join(Student).add_columns(Student.roll_no, Student.name, Attendance.status).all()
    # CSV
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['roll_no','name','date','status'])
    for rec in records:
        # rec is a tuple (Attendance, roll_no, name, status)
        cw.writerow([rec.roll_no, rec.name, d.isoformat(), rec.status])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=attendance_{d.isoformat()}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(debug=True)
