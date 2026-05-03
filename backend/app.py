# app.py
import os
import csv
import json
import re
from io import StringIO
from datetime import datetime as DateTime, date as Date, time as Time
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_caching import Cache
from flask_mail import Mail, Message
from celery import Celery
from celery.schedules import crontab

from disease_prediction.chat import start_chat, answer_question, predict_from_text
from Readmission.inference import predict_readmission, build_features_from_hms
from No_show.inference import predict_noshow, build_noshow_features_from_hms


# Initialize mail

# Import models from models.py (assumed to exist)
# models.py should define: db, User, DoctorProfile, PatientProfile, Appointment, Treatment
from models import db, User, DoctorProfile, PatientProfile, Appointment, Treatment,Department

# ---------------------------
# App & config
# ---------------------------
app = Flask(
    __name__,
    template_folder="templates",  # adjust if needed
    static_folder="../frontend",
    static_url_path="/static",
)
mail = Mail(app)
# --- Basic config (tweak for production) ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hospital.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "check_same_thread": False,
        "timeout": 30
    }
}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "change_this_to_a_real_secret"  # set a secure key
# Celery / Redis (adjust broker/backend if needed)
app.config["broker_url"] = "redis://localhost:6379/0"
app.config["result_backend"] = "redis://localhost:6379/0"
# Cache (optional)
app.config["CACHE_TYPE"] = "SimpleCache"  # or RedisCache in prod
app.config["CACHE_DEFAULT_TIMEOUT"] = 60
# Mail (configure for your provider)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "ahms84250@gmail.com"
app.config["MAIL_PASSWORD"] = "egyd qjxw hfzu ovfs"
app.config["MAIL_DEFAULT_SENDER"] = "ahms84250@gmail.com"

# init extensions
db.init_app(app)
jwt = JWTManager(app)
cache = Cache(app)
mail = Mail(app)
CORS(app)
def appointment_to_dict(a):
    """Return a JSON-serializable dict for an Appointment object."""
    return {
        "id": a.id,
        "patient_id": a.patient_id,
        "doctor_id": a.doctor_id,
        "doctor_name": a.doctor.username if getattr(a, "doctor", None) else None,
        "department_id": a.department_id,
        "department_name": a.department.name if getattr(a, "department", None) else None,
        # date as ISO yyyy-mm-dd (string)
        "date": a.date.isoformat() if a.date else None,
        # time as hh:mm:ss (string) — change format if you prefer e.g. "%I:%M %p"
        "time": a.time.strftime("%I:%M %p") if a.time else None,
        "status": a.status,
        "remarks": a.remarks,
    }

# ---------------------------
# Celery factory
# ---------------------------
def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        backend=flask_app.config.get("result_backend"),
        broker=flask_app.config.get("broker_url"),
    )
    celery.conf.update(flask_app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)
celery.conf.worker_enable_remote_control = True
celery.conf.task_send_sent_event = True
celery.conf.timezone = "Asia/Kolkata"
celery.conf.enable_utc = False
celery.conf.beat_max_loop_interval = 1

# Celery beat schedule (if you run celery beat)
celery.conf.beat_schedule = {
    "send-daily-reminder-12-30": {
        "task": "tasks.daily_reminder",
        #  "schedule": crontab()
        "schedule": crontab(hour=17, minute=53),
    },
    "monthly-doctor-activity": {
        "task": "tasks.monthly_doctor_activity",
        "schedule": crontab(hour=17, minute=53, day_of_month=30),
    }
}

# Ensure reports dir exists
REPORTS_DIR = os.path.join(app.root_path, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def initialize_database():
    """Create tables and default admin if not already created."""
    with app.app_context():
        db.create_all()
        ensure_patient_profile_columns()

        # Create default admin only if missing
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                username="admin@hms.com",
                password=generate_password_hash("admin123"),
                role="admin",
                approve=True,
                blocked=False,
            )
            db.session.add(admin)
            db.session.commit()

        # Ensure reports directory exists
        os.makedirs(REPORTS_DIR, exist_ok=True)


def ensure_patient_profile_columns():
    """Best-effort schema patch for existing SQLite DBs."""
    try:
        result = db.session.execute(text("PRAGMA table_info(patient_profiles)"))
        existing_columns = {row[1] for row in result.fetchall()}

        if "age" not in existing_columns:
            db.session.execute(text("ALTER TABLE patient_profiles ADD COLUMN age INTEGER"))

        if "gender" not in existing_columns:
            db.session.execute(text("ALTER TABLE patient_profiles ADD COLUMN gender VARCHAR(20) DEFAULT 'Unknown'"))

        db.session.commit()
    except Exception:
        db.session.rollback()

# ---------------------------
# Helpers
# ---------------------------
def is_admin_claims(claims):
    return claims.get("role") == "admin"


def is_doctor_claims(claims):
    return claims.get("role") == "doctor"


def is_patient_claims(claims):
    return claims.get("role") == "patient"


# ---------------------------
# Home
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------
# AUTH: register / login
# - NOTE: only patients self-register. Doctors are created by admin.
# ---------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    # Patient profile fields
    full_name = data.get("full_name")
    age = data.get("age")
    gender = data.get("gender", "Unknown")
    contact = data.get("contact")
    address = data.get("address")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    # Create User
    user = User(
        username=username,
        password=generate_password_hash(password),
        role=role,
        approve=True  # immediate approval
    )
    db.session.add(user)
    db.session.commit()

    # Create Patient Profile
    profile = PatientProfile(
        user_id=user.id,
        full_name=full_name,
        age=age,
        gender=gender,
        contact=contact,
        address=address,
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Registration successful!"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"category": "danger", "message": "username & password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"category": "danger", "message": "Bad username or password"}), 401

    if user.blocked:
        return jsonify({"category": "danger", "message": "Account blocked"}), 401

    # For doctors, admin must create them and profile may be created by admin
    redirect = None
    if user.role == "patient":
        profile = PatientProfile.query.filter_by(user_id=user.id).first()
        redirect = "patient_dashboard"
    elif user.role == "doctor":
        # doctors may be added by admin. If admin hasn't added doctor profile, redirect to doctor_profile (admin will usually add profile)
        profile = DoctorProfile.query.filter_by(user_id=user.id).first()
        # doctor accounts require admin approval to be active
        if not user.approve:
            return (
                jsonify(
                    {"category": "danger", "message": "Your doctor account is not approved yet."}
                ),
                401,
            )
        if user.blocked:
            return jsonify({"category": "danger", "message": "Your account is blocked."}), 401
        redirect = "doctor_profile" if not profile else "doctor_dashboard"
    elif user.role == "admin":
        redirect = "admin_dashboard"

    token = create_access_token(
        identity=user.username, additional_claims={"user_id": user.id, "role": user.role, "redirect": redirect}
    )
    return jsonify({"access_token": token}), 200


@app.route("/get-claims", methods=["GET"])
@jwt_required()
def get_claims():
    claims = get_jwt()
    return jsonify({"claims": claims}), 200

# ML
# @app.route("/predict", methods=["POST"])
# def predict_chatbot():
#     data = request.get_json()
#     response, status = chatbot_predict(data)
#     return jsonify(response), status

@app.route("/chat/start", methods=["GET"])
def start_chatbot():
    response = start_chat()
    return jsonify(response), 200


@app.route("/chat/answer", methods=["POST"])
def chat_answer():
    data = request.get_json() or {}
    user_answer = (data.get("answer") or "").strip()
    if not user_answer:
        return jsonify({"type": "error", "message": "Please enter symptoms or yes/no."}), 400

    # If user sends free text symptoms, run direct text prediction.
    if user_answer.lower() not in {"yes", "no"}:
        response = predict_from_text(user_answer)
    else:
        response = answer_question(user_answer)
    return jsonify(response), 200


@app.route("/readmission/predict", methods=["POST"])
@jwt_required()
def readmission_predict():
    data = request.get_json() or {}
    features = data.get("features", data)
    result = predict_readmission(features)
    if not result.get("ok"):
        return jsonify(result), 503
    return jsonify(result), 200



# ---------------------------
# ADMIN endpoints
# ---------------------------
@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"category": "danger", "message": "username & password required"}), 400

    user = User.query.filter_by(username=username, role="admin").first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"category": "danger", "message": "Bad username or password"}), 401
    token = create_access_token(identity=user.username, additional_claims={"admin_user_id": user.id, "role": "admin"})
    return jsonify({"access_token": token}), 200


@app.route("/admin/departments", methods=["GET", "POST"])
@jwt_required()
def admin_departments():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Admin only"}), 401

    # -----------------------------------------
    # GET → return all departments
    # -----------------------------------------
    if request.method == "GET":
        departments = Department.query.all()
        return jsonify([
            {
                "id": d.id,
                "name": d.name,
                "description": d.description
            }
            for d in departments
        ]), 200

    # -----------------------------------------
    # POST → add new department
    # -----------------------------------------
    data = request.get_json()
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()

    if not name:
        return jsonify({"message": "Department name required"}), 400

    # Check duplicate
    existing = Department.query.filter(
        func.lower(Department.name) == name.lower()
    ).first()

    if existing:
        return jsonify({"message": "Department already exists"}), 409

    new_dept = Department(name=name, description=description)
    db.session.add(new_dept)
    db.session.commit()

    return jsonify({"message": "Department added successfully"}), 201
@app.route("/admin/departments/<int:dept_id>", methods=["DELETE"])
@jwt_required()
def delete_department(dept_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Admin only"}), 401

    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({"message": "Department not found"}), 404

    db.session.delete(dept)
    db.session.commit()

    return jsonify({"message": "Department deleted"}), 200


@app.route("/admin/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401

    total_doctors = User.query.filter_by(role="doctor").count()
    total_patients = User.query.filter_by(role="patient").count()
    total_appointments = Appointment.query.count()
    upcoming = Appointment.query.filter(Appointment.date >= DateTime.now().date()).count()
    return jsonify(
        {
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming,
        }
    ), 200


# ----------------------------
# Admin: List or Create Doctors
# ----------------------------
@app.route("/admin/doctors", methods=["GET", "POST"])
@jwt_required()
def admin_doctors():
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401

    if request.method == "GET":
        doctors = User.query.filter_by(role="doctor").all()
        data = []
        for d in doctors:
            profile = DoctorProfile.query.filter_by(user_id=d.id).first()
            data.append({
                "id": d.id,
                "username": d.username,
                "approve": d.approve,
                "blocked": d.blocked,
                "specialization_id": profile.specialization_id if profile else None,
                "specialization_name": Department.query.get(profile.specialization_id).name if profile and profile.specialization_id else None,
                "experience": profile.experience if profile else None,
                "availability": profile.availability if profile else None
            })
        return jsonify(data), 200

    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password", "changeme123")
    specialization_id = data.get("specialization_id")
    experience = data.get("experience")
    availability = data.get("availability")

    if not username:
        return jsonify({"message": "Username required"}), 400
    if not specialization_id:
        return jsonify({"message": "Specialization required"}), 400
    if not Department.query.get(specialization_id):
        return jsonify({"message": "Invalid specialization ID"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    user = User(username=username, password=generate_password_hash(password), role="doctor", approve=data.get("approve", False), blocked=False)
    db.session.add(user)
    db.session.commit()

    profile = DoctorProfile(user_id=user.id, specialization_id=specialization_id, experience=experience, availability=availability)
    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Doctor created successfully"}), 201


@app.route("/admin/doctors/<int:user_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def admin_doctor_detail(user_id):
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401

    user = User.query.get_or_404(user_id)
    if user.role != "doctor":
        return jsonify({"message": "User is not a doctor"}), 400

    if request.method == "GET":
        profile = DoctorProfile.query.filter_by(user_id=user.id).first()
        return jsonify({"id": user.id, "username": user.username, "approve": user.approve, "blocked": user.blocked, "profile": profile.as_dict() if profile else None}), 200

    if request.method == "PUT":
        data = request.get_json() or {}
        user.approve = data.get("approve", user.approve)
        user.blocked = data.get("blocked", user.blocked)
        db.session.commit()
        return jsonify({"message": "updated"}), 200

    if request.method == "DELETE":
        prof = DoctorProfile.query.filter_by(user_id=user.id).first()
        if prof:
            db.session.delete(prof)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "deleted"}), 200


# Admin: create or update doctor profile
@app.route("/admin/doctors/<int:user_id>/profile", methods=["POST"])
@jwt_required()
def admin_doctor_profile(user_id):
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401

    user = User.query.get_or_404(user_id)
    if user.role != "doctor":
        return jsonify({"message": "User is not a doctor"}), 400

    data = request.get_json() or {}
    specialization_id = data.get("dept_id")
    experience = data.get("experience")
    availability = data.get("availability")

    # Find or create profile
    profile = DoctorProfile.query.filter_by(user_id=user_id).first()
    if profile:
        profile.specialization_id = specialization_id or profile.specialization_id
        profile.experience = experience or profile.experience
        profile.availability = availability or profile.availability
    else:
        profile = DoctorProfile(
            user_id=user_id,
            specialization_id=specialization_id,
            experience=experience,
            availability=availability
        )
        db.session.add(profile)

    db.session.commit()
    return jsonify({"message": "Doctor profile saved successfully"}), 200


@app.route("/admin/patients", methods=["GET"])
@jwt_required()
def admin_patients():
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401
    patients = User.query.filter_by(role="patient").all()
    return jsonify([{"id": p.id, "username": p.username,"blocked": p.blocked} for p in patients]), 200

@app.route("/admin/patient/<int:patient_id>", methods=["GET"])
@jwt_required()
def admin_get_patient_details(patient_id):
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401

    user = User.query.get(patient_id)
    profile = PatientProfile.query.filter_by(user_id=patient_id).first()

    if not user:
        return jsonify({"message": "Patient not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "blocked": user.blocked,
        "profile": profile.as_dict() if profile else None
    }), 200


@app.route("/admin/appointments", methods=["GET"])
@jwt_required()
def admin_appointments():
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401
    appts = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    result = []
    for a in appts:
        patient_profile = PatientProfile.query.filter_by(user_id=a.patient_id).first()
        prev_appt_count = (
            Appointment.query
            .filter(
                Appointment.patient_id == a.patient_id,
                Appointment.id != a.id,
                Appointment.date < a.date,
            )
            .count()
        )
        # HMS has no explicit "No-Show" status yet; use cancelled as proxy.
        prev_noshow_count = (
            Appointment.query
            .filter(
                Appointment.patient_id == a.patient_id,
                Appointment.id != a.id,
                Appointment.date < a.date,
                Appointment.status == "Cancelled",
            )
            .count()
        )

        no_show_risk = None
        if a.status == "Booked":
            noshow_features = build_noshow_features_from_hms(
                patient_profile,
                a.date,
                a.time,
                prev_appt_count,
                prev_noshow_count,
            )
            noshow_result = predict_noshow(noshow_features)
            if noshow_result.get("ok"):
                no_show_risk = {
                    "risk_label": noshow_result["risk_label"],
                    "risk_probability": noshow_result["risk_probability"],
                    "source": noshow_result.get("source"),
                }

        result.append({
            "id": a.id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": str(a.date),
            "time": str(a.time),
            "status": a.status,
            "remarks": a.remarks,
            "no_show_risk": no_show_risk,
        })
    return jsonify(result), 200


@app.route("/admin/block_user/<int:user_id>", methods=["POST"])
@jwt_required()
def admin_block_user(user_id):
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401
    data = request.get_json() or {}
    action = data.get("action")
    user = User.query.get_or_404(user_id)
    if action == "block":
        user.blocked = True
    elif action == "unblock":
        user.blocked = False
    elif action == "approve":
        user.approve = True
    elif action == "reject":
        user.approve = False
    else:
        return jsonify({"message": "invalid action"}), 400
    db.session.commit()
    return jsonify({"message": "done"}), 200


# Admin: trigger CSV export of appointments for a doctor
@app.route("/admin/export/<int:professional_id>", methods=["GET"])
@jwt_required()
def export_service_requests(professional_id):
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401
    task = export_professional_service_requests.delay(professional_id)
    return jsonify({"message": f"Export started for professional ID {professional_id}.", "task_id": task.id}), 202


@app.route("/admin/reports/list", methods=["GET"])
@jwt_required()
def list_reports():
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401
    os.makedirs(REPORTS_DIR, exist_ok=True)
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".csv")]
    return jsonify({"downloads": files}), 200


@app.route("/admin/reports/download/<filename>", methods=["GET"])
@jwt_required()
def download_report(filename):
    claims = get_jwt()
    if not is_admin_claims(claims):
        return jsonify({"message": "Admin only"}), 401
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)


# ---------------------------
# DOCTOR endpoints
# ---------------------------
@app.route("/doctor/profile", methods=["GET", "POST"])
@jwt_required()
def doctor_profile():
    claims = get_jwt()
    doctor_id = claims.get("user_id")

    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()

    # -------- GET --------
    if request.method == "GET":
        if not profile:
            return jsonify({"message": "no profile"}), 200

        return jsonify({
            "username": profile.user.username,
            "specialization_id": profile.specialization_id,
            "experience": profile.experience,
            "availability": profile.availability  # stored as JSON string
        }), 200

    # -------- POST --------
    data = request.get_json()
    specialization_id = data.get("specialization_id")
    experience = data.get("experience")
    availability = data.get("availability")  # JSON string from frontend

    if not profile:
        profile = DoctorProfile(
            user_id=doctor_id,
            specialization_id=specialization_id,
            experience=experience,
            availability=availability
        )
        db.session.add(profile)
    else:
        profile.specialization_id = specialization_id
        profile.experience = experience
        profile.availability = availability

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

# @app.route("/doctor/availability", methods=["GET", "POST"])
# @jwt_required()
# def doctor_availability():
#     claims = get_jwt()
#     doctor_id = claims.get("id")

#     profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
#     if not profile:
#         return jsonify({"message": "Doctor profile not found"}), 404

#     if request.method == "GET":
#         return jsonify({"availability": profile.availability}), 200

#     data = request.get_json()
#     availability = json.dumps(data.get("availability", {}))
#     profile.availability = availability
#     db.session.commit()
#     return jsonify({"message": "Availability updated successfully"}), 200


@app.route("/doctor/appointments", methods=["GET"])
@jwt_required()
def doctor_appointments():
    claims = get_jwt()
    if not is_doctor_claims(claims):
        return jsonify({"message": "Doctor only"}), 401

    doctor_id = claims["user_id"]

    appts = Appointment.query.filter_by(doctor_id=doctor_id)\
        .order_by(Appointment.date.asc(), Appointment.time.asc())\
        .all()

    result = []

    for a in appts:
        patient = User.query.filter_by(id=a.patient_id).first()
        # print(patient.username)
        patient_name = patient.username
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()
        readmission_risk = None

        if treatment and treatment.notes:
            match = re.search(
                r"Readmission risk:\s*(High|Low)\s*\((\d+(?:\.\d+)?)%\)",
                treatment.notes,
                re.IGNORECASE,
            )
            if match:
                risk_label = match.group(1).capitalize()
                risk_percentage = float(match.group(2))
                readmission_risk = {
                    "risk_label": risk_label,
                    "risk_probability": round(risk_percentage / 100, 4),
                }

        if not readmission_risk and a.status == "Completed":
            profile = PatientProfile.query.filter_by(user_id=a.patient_id).first()
            patient_treatments_count = (
                Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)
                .filter(Appointment.patient_id == a.patient_id)
                .count()
            )
            patient_appointments_count = (
                Appointment.query
                .filter(
                    Appointment.patient_id == a.patient_id,
                    Appointment.status != "Cancelled",
                )
                .count()
            )
            inferred_features = build_features_from_hms(
                profile,
                a,
                patient_treatments_count,
                patient_appointments_count,
            )
            risk_result = predict_readmission(inferred_features)
            if risk_result.get("ok"):
                readmission_risk = {
                    "risk_label": risk_result["risk_label"],
                    "risk_probability": risk_result["risk_probability"],
                }

        result.append({
            "id": a.id,
            "patient_name": patient_name,
            "patient_id": a.patient_id,
            "date": str(a.date),
            "time": str(a.time),
            "status": a.status,
            "remarks": a.remarks,
            "readmission_risk": readmission_risk,
        })

    return jsonify(result), 200

@app.route("/doctor/patients", methods=["GET"])
@jwt_required()
def doctor_patients():
    claims = get_jwt()
    if not is_doctor_claims(claims):
        return jsonify({"message": "Doctor only"}), 401

    doctor_id = claims["user_id"]

    # Get unique patient IDs from the doctor's appointments
    appts = Appointment.query.filter_by(doctor_id=doctor_id).all()
    patient_ids = set(a.patient_id for a in appts)

    patients = User.query.filter(User.id.in_(patient_ids)).all()

    return jsonify([{"id": p.id, "username": p.username} for p in patients]), 200


@app.route("/doctor/appointments/<int:appointment_id>/complete", methods=["POST"])
@jwt_required()
def doctor_complete_appointment(appointment_id):
    claims = get_jwt()
    if not is_doctor_claims(claims):
        return jsonify({"message": "Doctor only"}), 401
    doctor_id = claims["user_id"]
    appt = Appointment.query.get_or_404(appointment_id)
    if appt.doctor_id != doctor_id:
        return jsonify({"message": "Not your appointment"}), 401

    data = request.get_json() or {}
    diagnosis = data.get("diagnosis", "")
    prescription = data.get("prescription", "")
    notes = data.get("notes", "")
    readmission_features = data.get("readmission_features")

    appt.status = "Completed"
    db.session.commit()

    profile = PatientProfile.query.filter_by(user_id=appt.patient_id).first()
    previous_treatments_count = (
        Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.patient_id == appt.patient_id)
        .count()
    )
    patient_appointments_count = (
        Appointment.query
        .filter(
            Appointment.patient_id == appt.patient_id,
            Appointment.status != "Cancelled",
        )
        .count()
    )
    db_based_features = build_features_from_hms(
        profile,
        appt,
        previous_treatments_count,
        patient_appointments_count,
    )

    if readmission_features:
        # Age, gender and inpatient count always come from DB profile/history.
        for key, value in readmission_features.items():
            if key not in ("age", "gender", "number_inpatient"):
                db_based_features[key] = value
    readmission_features = db_based_features

    risk_result = predict_readmission(readmission_features)
    if risk_result.get("ok"):
        notes = (
            (notes + "\n\n" if notes else "")
            + f"Readmission risk: {risk_result['risk_label']} ({round(risk_result['risk_probability'] * 100, 2)}%)"
        )

    treatment = Treatment(appointment_id=appt.id, diagnosis=diagnosis, prescription=prescription, notes=notes)
    db.session.add(treatment)
    db.session.commit()

    # optional: notify patient by email if patient.username is an email
    try:
        patient_user = User.query.get(appt.patient_id)
        if patient_user and "@" in patient_user.username:
            msg = Message(subject="Your visit summary", recipients=[patient_user.username], body=f"Your appointment on {appt.date} with doctor id {appt.doctor_id} is completed.\nDiagnosis: {diagnosis}\nPrescription: {prescription}")
            mail.send(msg)
    except Exception:
        pass

    response = {"message": "Appointment completed and treatment saved"}
    if risk_result.get("ok"):
        response["readmission"] = {
            "risk_label": risk_result["risk_label"],
            "risk_probability": risk_result["risk_probability"],
            "features_used": risk_result["features_used"],
        }
    elif readmission_features:
        response["readmission"] = {"error": risk_result.get("message")}

    return jsonify(response), 200

# ✅ Get availability
# @app.route("/doctor/<int:doctor_id>/availability", methods=["GET"])
# @jwt_required()
# def get_doctor_availability(doctor_id):
#     profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
#     if not profile or not profile.availability:
#         return jsonify({"availability": []}), 200

#     availability_data = json.loads(profile.availability)
#     available_days = []

#     for date, available in availability_data.items():
#         if available:
#             slots = []
#             start_hour = 11
#             end_hour = 17
#             current = datetime.strptime(f"{date} {start_hour}:00", "%Y-%m-%d %H:%M")
#             while current.hour < end_hour:
#                 slot = current.strftime("%I:%M %p")
#                 existing = Appointment.query.filter_by(
#                     doctor_id=doctor_id,
#                     date=date,
#                     time=slot
#                 ).first()
#                 if existing and existing.status=="Booked":
#                     current += timedelta(minutes=30)
#                     continue
#                 slots.append(slot)
#                 current += timedelta(minutes=30)
#             available_days.append({"date": date, "slots": slots})

#     return jsonify({"availability": available_days}), 200

@app.route("/doctor/<int:doctor_id>/availability", methods=["GET"])
@jwt_required()
def get_doctor_availability(doctor_id):
    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
    
    if not profile or not profile.availability:
        return jsonify({"availability": []}), 200

    availability_data = json.loads(profile.availability)
    available_days = []

    for date_str, available in availability_data.items():
        if not available:
            continue

        slots = []
        start_hour = 11
        end_hour = 17

        # Convert date string → date object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        current = datetime.strptime(f"{date_str} {start_hour}:00", "%Y-%m-%d %H:%M")

        while current.hour < end_hour:
            slot_time = current.time()                 # proper time object
            slot_str = current.strftime("%I:%M %p")    # for display

            # Check if slot is booked
            existing = Appointment.query.filter_by(
                doctor_id=doctor_id,
                date=date_obj,
                time=slot_time
            ).first()

            # skip booked slots
            if existing :
                current += timedelta(minutes=30)
                continue

            # Add slot only if NOT booked
            slots.append(slot_str)
            current += timedelta(minutes=30)

        available_days.append({
            "date": date_str,
            "slots": slots
        })

    return jsonify({"availability": available_days}), 200


# ✅ Get already booked appointments
@app.route("/doctor/<int:doctor_id>/appointments", methods=["GET"])
@jwt_required()
def get_doctor_booked_appointments(doctor_id):
    # get appointments and include doctor / department via relationships if available
    appts = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    booked = [appointment_to_dict(a) for a in appts]
    return jsonify({"appointments": booked}), 200

@app.route("/appointments/book", methods=["POST"])
@jwt_required()
def book_appointment():
    claims = get_jwt()
    patient_id = claims.get("user_id")
    data = request.get_json()

    doctor_id = data.get("doctor_id")
    date_str = data.get("date")
    time_str = data.get("time")

    if not (doctor_id and date_str and time_str):
        return jsonify({"message": "Missing data"}), 400

    # Convert date string → date object
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format"}), 400

    # Convert "04:00 PM" → time object
    try:
        time_obj = datetime.strptime(time_str, "%I:%M %p").time()
    except ValueError:
        return jsonify({"message": "Invalid time format"}), 400

    # Check if slot already booked
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=date_obj,
        time=time_obj
    ).first()

    day=Appointment.query.filter_by(patient_id=patient_id,doctor_id=doctor_id,date=date_obj).first()
    if day and day.date== date_obj:
        print(day.date)
        print(date_obj)
        return jsonify({"message":"For this day slot already booked"}),400

    if existing and existing.status == "Booked":
        return jsonify({"message": "Slot already booked"}), 400

    # Create the new appointment
    new_appt = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        date=date_obj,
        time=time_obj,
        status="Booked"
    )
    db.session.add(new_appt)
    db.session.commit()

    # -----------------------------
    # 📧 SEND CONFIRMATION EMAIL
    # -----------------------------
    patient = db.session.get(User, patient_id)
    doctor = db.session.get(User, doctor_id)

    send_appointment_email(
    patient=patient,
    doctor=doctor,
    date_obj=date_obj,
    time_obj=time_obj,
    action="booked")

    return jsonify({"message": "Appointment booked successfully!"}), 201


# # Doctor: Get current availability
# @app.route("/doctor/availability", methods=["GET"])
# @jwt_required()
# def get_my_availability():
#     claims = get_jwt()
#     if claims["role"] != "doctor":
#         return jsonify({"message": "Unauthorized"}), 403

#     doctor = User.query.filter_by(id=claims["id"]).first()
#     profile = DoctorProfile.query.filter_by(user_id=doctor.id).first()

#     if not profile:
#         return jsonify({"message": "No profile found"}), 404

#     return jsonify({"availability": profile.availability or "{}"}), 200


# # Doctor: Update availability
# @app.route("/doctor/availability", methods=["POST"])
# @jwt_required()
# def update_my_availability():
#     claims = get_jwt()
#     if claims["role"] != "doctor":
#         return jsonify({"message": "Unauthorized"}), 403

#     data = request.get_json() or {}
#     availability = data.get("availability")

#     profile = DoctorProfile.query.filter_by(user_id=claims["id"]).first()
#     if not profile:
#         return jsonify({"message": "Profile not found"}), 404

#     profile.availability = availability
#     db.session.commit()

#     return jsonify({"message": "Availability updated successfully"}), 200

@app.route("/doctor/availability", methods=["GET", "POST"])
@jwt_required()
def doctor_availability():
    claims = get_jwt()
    # Use correct claim key for ID
    doctor_id = claims.get("user_id")  

    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
    if not profile:
        return jsonify({"message": "Doctor profile not found"}), 404

    # ✅ GET: return current availability
    if request.method == "GET":
        availability = json.loads(profile.availability) if profile.availability else {}
        return jsonify({"availability": availability}), 200

    # ✅ POST: update availability
    data = request.get_json() or {}
    availability = data.get("availability")
    if not availability:
        return jsonify({"message": "No availability data received"}), 400

    profile.availability = json.dumps(availability)
    db.session.commit()

    return jsonify({"message": "Availability updated successfully"}), 200


# ---------------------------
# PATIENT endpoints
# ---------------------------
@app.route("/patient/profile", methods=["GET", "POST"])
@jwt_required()
def patient_profile():
    claims = get_jwt()
    if not is_patient_claims(claims):
        return jsonify({"message": "Patient only"}), 401
    user_id = claims["user_id"]
    profile = PatientProfile.query.filter_by(user_id=user_id).first()
    if request.method == "GET":
        if not profile:
            return jsonify({"message": "no profile"}), 200
        return jsonify(profile.as_dict()), 200

    data = request.get_json() or {}
    full_name = data.get("full_name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")
    address = data.get("address")

    if profile:
        profile.full_name = full_name or profile.full_name
        profile.age = age or profile.age
        profile.gender = gender or profile.gender
        profile.contact = contact or profile.contact
        profile.address = address or profile.address
    else:
        profile = PatientProfile(
            user_id=user_id,
            full_name=full_name,
            age=age,
            gender=gender or "Unknown",
            contact=contact,
            address=address,
        )
        db.session.add(profile)
    db.session.commit()
    return jsonify({"message": "saved"}), 200


@app.route("/patient/dashboard", methods=["GET"])
@jwt_required()
def patient_dashboard():
    claims = get_jwt()
    if claims.get("role") != "patient":
        return jsonify({"message": "Unauthorized", "category": "danger"}), 403

    user_id = claims.get("user_id")
    patient = db.session.get(User, user_id)
    if not patient:
        return jsonify({"message": "Patient not found", "category": "danger"}), 404

    # Get all departments
    departments = Department.query.all()
    dept_list = [{"id": d.id, "name": d.name, "description": d.description} for d in departments]

    return jsonify({
        "message": "Dashboard loaded successfully",
        "category": "success",
        "patient": patient.username,
        "departments": dept_list
    }), 200

@app.route("/departments/<int:dept_id>", methods=["GET"])
@jwt_required()
def get_department_details(dept_id):
    # Get department info
    dept = db.session.get(Department, dept_id)
    if not dept:
        return jsonify({"message": "Department not found"}), 404

    # Get doctors who specialize in this department
    doctors = (
        db.session.query(User, DoctorProfile)
        .join(DoctorProfile, DoctorProfile.user_id == User.id)
        .filter(
            User.role == "doctor",
            User.approve == True,
            DoctorProfile.specialization_id == dept_id
        )
        .all()
    )

    doctor_list = []
    for user, profile in doctors:
        doctor_list.append({
            "id": user.id,
            "name": user.username,
            "experience": profile.experience,
        })

    return jsonify({
        "department": {
            "id": dept.id,
            "name": dept.name,
            "description": dept.description
        },
        "doctors": doctor_list
    }), 200


@app.route("/patient/reports/list", methods=["GET"])
@jwt_required()
def patient_reports_list():
    user_id = get_jwt_identity()
    claims = get_jwt()
    user_id = claims.get("user_id")   # THIS is the actual integer ID
    reports_folder = os.path.join(os.getcwd(), "reports")

    files = os.listdir(reports_folder)

    patient_files = [
        f for f in files
        if f.startswith(f"patient_{user_id}_")
    ]

    return jsonify({"downloads": patient_files})


@app.route("/patient/appointments", methods=["GET"])
@jwt_required()
def patient_appointments():
    claims = get_jwt()
    if claims.get("role") != "patient":
        return jsonify({"message": "Access restricted to patients only"}), 403

    user_id = claims.get("user_id")

    appts = Appointment.query.filter_by(patient_id=user_id)\
        .order_by(Appointment.date.desc(), Appointment.time.desc()).all()

    result = []
    for a in appts:
        result.append({
            "id": a.id,
            "date": str(a.date),
            "time": str(a.time),
            "status": a.status,
            "remarks": a.remarks,

            "doctor_username": a.doctor.username if a.doctor else "Unknown",
            "department": a.department.name if a.department else "Unknown",

            "can_cancel": a.status.lower() == "booked"
        })

    return jsonify(result), 200


@app.route("/patient/appointments/<int:appointment_id>/cancel", methods=["POST"])
@jwt_required()
def patient_cancel_appointment(appointment_id):
    claims = get_jwt()
    if not is_patient_claims(claims):
        return jsonify({"message": "Patient only"}), 401
    user_id = claims["user_id"]
    appt = Appointment.query.get_or_404(appointment_id)
    patient_id=appt.patient_id
    doctor_id=appt.doctor_id
    if appt.patient_id != user_id:
        return jsonify({"message": "Not your appointment"}), 401
    if appt.status != "Booked":
        return jsonify({"message": "Only booked appointments can be cancelled"}), 400
    patient = db.session.get(User, patient_id)
    doctor = db.session.get(User, doctor_id)
    appt.status = "Cancelled"
    db.session.commit()
    send_appointment_email(
    patient=patient,
    doctor=doctor,
    date_obj=appt.date,
    time_obj=appt.time,
    action="cancelled"
)

    return jsonify({"message": "cancelled"}), 200


@app.route("/patient/treatments", methods=["GET"])
@jwt_required()
def patient_treatments():
    claims = get_jwt()
    if not is_patient_claims(claims):
        return jsonify({"message": "Patient only"}), 401
    user_id = claims["user_id"]
    treatments = Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id).filter(Appointment.patient_id == user_id).all()
    out = []
    for t in treatments:
        appt = Appointment.query.get(t.appointment_id)
        out.append({"treatment_id": t.id, "appointment_id": t.appointment_id, "appointment_date": str(appt.date) if appt else None, "diagnosis": t.diagnosis, "prescription": t.prescription, "notes": t.notes})
    return jsonify(out), 200


@app.route("/patient/export_treatments", methods=["GET"])
@jwt_required()
def patient_export_treatments():
    claims = get_jwt()
    if not is_patient_claims(claims):
        return jsonify({"message": "Patient only"}), 401
    patient_id = claims["user_id"]
    task = export_treatments_csv.delay(patient_id)
    return jsonify({"task_id": task.id}), 202


@app.route("/patient/reports/download/<path:filename>", methods=["GET"])
@jwt_required()
def reports_download(filename):
    # allow admins or owner check in prod; for now keep minimal checks
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)

@app.route('/departments', methods=['GET'])
@jwt_required(optional=True)
def get_departments():
    departments = Department.query.all()
    return jsonify([{
        "id": d.id,
        "name": d.name, "description": d.description
    } for d in departments]), 200

@app.route("/patient/<int:patient_id>/history", methods=["GET"])
@jwt_required()
def get_patient_history(patient_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = claims.get("user_id")

    # ---------------------------
    # Access Control
    # ---------------------------
    if role == "patient":
        if user_id != patient_id:
            return jsonify({"message": "Patients may only view their own history"}), 403

    elif role == "doctor":
        # doctor can only see history of their own patients
        appt = Appointment.query.filter_by(doctor_id=user_id, patient_id=patient_id).first()
        if not appt:
            return jsonify({"message": "Doctor not assigned to this patient"}), 403

    elif role == "admin":
        pass  # admin can access any history
    else:
        return jsonify({"message": "Invalid role"}), 403

    # ---------------------------
    # Fetch complete history
    # ---------------------------
    treatments = (
        Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.patient_id == patient_id)
        .all()
    )

    patient_profile = PatientProfile.query.filter_by(user_id=patient_id).first()
    total_treatments_count = (
        Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.patient_id == patient_id)
        .count()
    )
    total_appointments_count = (
        Appointment.query
        .filter(
            Appointment.patient_id == patient_id,
            Appointment.status != "Cancelled",
        )
        .count()
    )

    history = []
    for t in treatments:
        appt = Appointment.query.get(t.appointment_id)
        doctor = User.query.get(appt.doctor_id) if appt else None
        inferred_features = build_features_from_hms(
            patient_profile,
            appt,
            total_treatments_count,
            total_appointments_count,
        )
        risk_result = predict_readmission(inferred_features)
        history.append({
            "date": str(appt.date) if appt else None,
            "time": str(appt.time) if appt else None,
            "doctor": doctor.username if doctor else "Unknown",
            "diagnosis": t.diagnosis,
            "prescription": t.prescription,
            "notes": t.notes,
            "readmission_risk": (
                {
                    "risk_label": risk_result["risk_label"],
                    "risk_probability": risk_result["risk_probability"],
                }
                if risk_result.get("ok")
                else None
            ),
        })

    return jsonify({"history": history}), 200

from sqlalchemy import and_
@app.route("/appointments/<int:appointment_id>/reschedule", methods=["POST"])
@jwt_required()
def reschedule_appointment(appointment_id):
    """
    Allows:
      - patient who owns the appointment
      - doctor assigned to the appointment
      - admin (any appointment)
    Body JSON:
      { "date": "YYYY-MM-DD", "time": "HH:MM AM/PM" }
    """
    claims = get_jwt()
    role = claims.get("role")
    user_id = claims.get("user_id")

    if role not in ("patient", "doctor", "admin"):
        return jsonify({"message": "Unauthorized"}), 401

    appt = Appointment.query.get_or_404(appointment_id)

    # --- Permission checks ---
    if role == "patient" and appt.patient_id != user_id:
        return jsonify({"message": "Not your appointment"}), 403
    if role == "doctor" and appt.doctor_id != user_id:
        return jsonify({"message": "Not your appointment"}), 403

    data = request.get_json() or {}
    new_date = data.get("date")
    new_time = data.get("time")

    if not new_date or not new_time:
        return jsonify({"message": "date and time required"}), 400

    # --- Parse date ---
    try:
        new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
    except:
        return jsonify({"message": "Invalid date format"}), 400

    # --- Parse time (12-hour format → time object) ---
    try:
        new_time_obj = datetime.strptime(new_time, "%I:%M %p").time()
    except:
        return jsonify({"message": "Invalid time format"}), 400

    # If same slot — no update needed
    if appt.date == new_date_obj and appt.time == new_time_obj:
        return jsonify({"message": "Already scheduled at that time"}), 200

    # --- Conflict Check ---
    conflict = Appointment.query.filter(
        Appointment.doctor_id == appt.doctor_id,
        Appointment.date == new_date_obj,
        Appointment.time == new_time_obj,
        Appointment.status == "Booked",
        Appointment.id != appt.id
    ).first()

    if conflict:
        return jsonify({"message": "Requested slot is already booked"}), 409

    # --- Update slot ---
    patient = User.query.get(appt.patient_id)
    doctor = User.query.get(appt.doctor_id)
    appt.date = new_date_obj
    appt.time = new_time_obj
    appt.status = "Booked"  # Keep same canonical status
    send_appointment_email(
    patient=patient,
    doctor=doctor,
    date_obj=new_date_obj,
    time_obj=new_time_obj,
    action="rescheduled"
)

    db.session.commit()
    return jsonify({
        "message": "Appointment rescheduled successfully",
        "appointment": {
            "id": appt.id,
            "date": str(appt.date),
            "time": appt.time.strftime("%H:%M:%S"),
            "status": appt.status
        }
    }), 200


# ---------------------------
# CELERY tasks
# ---------------------------



@celery.task(name="tasks.daily_reminder")
def daily_reminder():
    today = DateTime.now().date()
    appts = Appointment.query.filter_by(date=today, status="Booked").all()
    for a in appts:
        patient = User.query.get(a.patient_id)
        doctor = User.query.get(a.doctor_id)
        if patient and "@" in patient.username:
            try:
                msg = Message(subject="Appointment Reminder", recipients=[patient.username], body=f"Reminder: Appointment with Dr {doctor.username if doctor else 'N/A'} at {a.time} on {a.date}")
                mail.send(msg)
            except Exception:
                pass
    return "done"

@celery.task(name="tasks.monthly_doctor_activity")
def monthly_doctor_activity():
    now = DateTime.now()
    month = now.month
    year = now.year

    doctors = User.query.filter_by(role="doctor", approve=True).all()

    for d in doctors:
        appts = (
            Appointment.query
            .filter(
                Appointment.doctor_id == d.id,
                func.strftime("%m", Appointment.date) == f"{month:02d}"
            )
            .all()
        )

        rows = []
        completed = 0
        cancelled = 0

        for a in appts:
            patient = User.query.get(a.patient_id)
            treatment = Treatment.query.filter_by(appointment_id=a.id).first()

            if a.status.lower() == "completed":
                completed += 1
            if a.status.lower() == "cancelled":
                cancelled += 1

            rows.append({
                "date": str(a.date),
                "time": str(a.time),
                "patient": patient.username if patient else "-",
                "status": a.status,
                "diagnosis": treatment.diagnosis if treatment else "",
                "prescription": treatment.prescription if treatment else ""
            })

        summary = {
            "month": month,
            "year": year,
            "month_name": now.strftime("%B"),
            "total": len(appts),
            "completed": completed,
            "cancelled": cancelled,
        }

        # Generate PDF
        pdf_file = generate_monthly_report_pdf(d, rows, summary)

        # Email PDF to doctor
        if "@" in d.username:
            try:
                msg = Message(
                    subject=f"Monthly Activity Report — {now.strftime('%B %Y')}",
                    recipients=[d.username],
                    body="Please find attached your monthly activity report.",
                )
                with app.open_resource(pdf_file) as pdf:
                    msg.attach(os.path.basename(pdf_file), "application/pdf", pdf.read())
                mail.send(msg)
            except Exception as e:
                print("Email error:", e)

    return "monthly_reports_done"


@celery.task(name="tasks.export_treatments_csv")
def export_treatments_csv(patient_id):
    treatments = Treatment.query.join(Appointment).filter(Appointment.patient_id == patient_id).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["appointment_date", "doctor_username", "diagnosis", "prescription", "notes"])
    for t in treatments:
        appt = Appointment.query.get(t.appointment_id)
        doctor = User.query.get(appt.doctor_id) if appt else None
        writer.writerow([str(appt.date) if appt else "", doctor.username if doctor else "", t.diagnosis, t.prescription, t.notes])
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"patient_{patient_id}_treatments.csv")
    with open(path, "w", newline="") as f:
        f.write(output.getvalue())
    return path


@celery.task(name="tasks.export_professional_service_requests")
def export_professional_service_requests(professional_id):
    appts = Appointment.query.filter_by(doctor_id=professional_id).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["appointment_id", "patient_id", "date", "time", "status", "remarks"])
    for a in appts:
        writer.writerow([a.id, a.patient_id, str(a.date), str(a.time), a.status, a.remarks])
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"doctor_{professional_id}_appointments.csv")
    with open(path, "w", newline="") as f:
        f.write(output.getvalue())
    return path

def generate_monthly_report_pdf(doctor, rows, summary):
    month_name = summary["month_name"]
    year = summary["year"]

    # Render HTML template
    html = render_template(
        "monthly_report.html",
        doctor_name=doctor.username,
        rows=rows,
        month_name=month_name,
        year=year,
        total=summary["total"],
        completed=summary["completed"],
        cancelled=summary["cancelled"],
        generation_time=DateTime.now().strftime("%Y-%m-%d %H:%M")
    )

    # Save HTML report instead of PDF
    filename = f"doctor_{doctor.id}_report_{year}_{summary['month']:02d}.html"
    report_path = os.path.join(REPORTS_DIR, filename)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path

def send_appointment_email(patient, doctor, date_obj, time_obj, action):
    """
    action = 'booked' | 'cancelled' | 'rescheduled'
    """

    if not patient or "@" not in patient.username:
        return False  # invalid email

    time_str = time_obj.strftime("%I:%M %p")

    # ---------- Define messages ----------
    subjects = {
        "booked": "Appointment Confirmation",
        "cancelled": "Appointment Cancelled",
        "rescheduled": "Appointment Rescheduled"
    }

    bodies = {
        "booked": f"Your appointment with Dr {doctor.username} is booked on {date_obj} at {time_str}.",
        "cancelled": f"Your appointment with Dr {doctor.username} on {date_obj} at {time_str} has been cancelled.",
        "rescheduled": f"Your appointment with Dr {doctor.username} has been rescheduled to {date_obj} at {time_str}."
    }

    subject = subjects.get(action, "Appointment Update")
    body = bodies.get(action, "Your appointment has been updated.")

    # ---------- Send Email ----------
    try:
        msg = Message(
            subject=subject,
            recipients=[patient.username],
            body=body,
        )
        mail.send(msg)
        print("EMAIL SENT:", subject)
        return True

    except Exception as e:
        print("EMAIL FAILED:", e)
        return False


@app.route("/test-email")
def test_email():
    msg = Message(
        subject="Test Email",
        recipients=["aryabanda189a@gmail.com"],
        body="Email works!"
    )
    mail.send(msg)
    return {"message": "Email sent"}


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True,use_reloader=False)
