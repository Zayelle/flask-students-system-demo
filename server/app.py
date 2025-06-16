from flask import Flask, send_file, request, jsonify
from models import db, Student
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_prefixed_env()

db.init_app(app)
migration = Migrate(app, db)

@app.before_request
def beforerequest():
    authed = False
    if request.path.startswith("/uploads") and authed == False:
        return "Prouted route. you need to be logged in", 403


@app.route("/")
def home():
    return send_file("./static/index.html")

@app.route("/uploads/<string:filename>")
def uploads(filename):
    return send_file(f"./uploads/{filename}")

@app.route('/students', methods=['GET'])
def students():
    students = Student.query.all()
    students_data = [student.to_dict() for student in students]
    return jsonify(students_data), 200

@app.route('/students/<int:id>', methods=['GET'])
def students_id(id):
    student = Student.query.filter(Student.id == id).first()
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student.to_dict()), 200

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Name is required"}), 400
    student = Student(name=data['name'])
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201

@app.route('/courses', methods=['GET'])
def get_courses():
    from models import Course  # Ensure Course is imported
    courses = Course.query.all()
    courses_data = [course.to_dict() for course in courses]
    return jsonify(courses_data), 200

@app.route('/courses', methods=['POST'])
def create_course():
    from models import Course  # Ensure Course is imported
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Name is required"}), 400
    course = Course(name=data['name'])
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_dict()), 201

@app.route('/enrollments', methods=['POST'])
def enroll_student():
    from models import Enrollment, Student, Course  # Ensure models are imported
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not student_id or not course_id:
        return jsonify({"error": "student_id and course_id are required"}), 400

    student = Student.query.get(student_id)
    course = Course.query.get(course_id)

    if not student or not course:
        return jsonify({"error": "Student or Course not found"}), 404

        # Check if already enrolled
    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        return jsonify({"error": "Student already enrolled in this course"}), 400

    enrollment = Enrollment(student_id=student_id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify(enrollment.to_dict()), 201

@app.route('/enrollments', methods=['GET'])
def list_enrollments():
    from models import Enrollment  # Ensure Enrollment is imported
    enrollments = Enrollment.query.all()
    enrollments_data = [enrollment.to_dict() for enrollment in enrollments]
    return jsonify(enrollments_data), 200

@app.route('/enrollments/<int:id>', methods=['DELETE'])
def unenroll_student(id):
    from models import Enrollment  # Ensure Enrollment is imported
    enrollment = Enrollment.query.get(id)
    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({"message": "Student unenrolled successfully"}), 200

# MISSING MODULE psycopg2

