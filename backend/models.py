from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ===========================
# User Table (Admin/Doctor/Patient)
# ===========================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)  # email
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin / Doctor / Patient
    approve = db.Column(db.Boolean, default=False)  # doctor approved by admin
    blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}



# ===========================
# Department / Specialization
# ===========================
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))



# ===========================
# Doctor Profile
# ===========================
class DoctorProfile(db.Model):
    __tablename__ = 'doctor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    specialization_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    experience = db.Column(db.String(100))
    availability = db.Column(db.String(200))  # can store JSON for time slots

    # ✅ Relationships
    user = db.relationship('User', backref='doctor_profile', foreign_keys=[user_id])
    specialization = db.relationship('Department', foreign_keys=[specialization_id], backref='spec_doctors')

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "specialization_id": self.specialization_id,
            "experience": self.experience,
            "availability": self.availability,
        }

# ===========================
# Patient Profile
# ===========================
class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    full_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20), default="Unknown")
    contact = db.Column(db.String(15))
    address = db.Column(db.String(200))

    user = db.relationship('User', foreign_keys=[user_id])

    def as_dict(self):
        """Convert model to dictionary for JSON response"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "age": self.age,
            "gender": self.gender,
            "contact": self.contact,
            "address": self.address,
        }



# ===========================
# Appointment Table
# ===========================
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    status = db.Column(db.String(20), default="Booked")  # Booked/Completed/Cancelled
    remarks = db.Column(db.String(200))

    patient = db.relationship('User', foreign_keys=[patient_id], backref="patient_appointments")
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref="doctor_appointments")
    department = db.relationship('Department')

    def appointment_to_dict(appt):
        return {
            "id": appt.id,
            "patient_id": appt.patient_id,
            "doctor_id": appt.doctor_id,
            "department_id": appt.department_id,
            "date": appt.date.strftime("%Y-%m-%d") if appt.date else None,
            "time": appt.time.strftime("%H:%M") if appt.time else None,
            "status": appt.status,
            "remarks": appt.remarks,
        }


# ===========================
# Treatment Table
# ===========================
class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)

    appointment = db.relationship('Appointment')
