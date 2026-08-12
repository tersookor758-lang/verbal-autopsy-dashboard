from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db


# ==========================================================
# User Model
# ==========================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        nullable=False,
        default="Viewer"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # -----------------------------
    # Password Methods
    # ------------------------------

    def set_password(self, password, validate=False):
        """
        Hash and set the password.
        
        Args:
            password (str): Plain text password
            validate (bool): If True, validate password strength before setting
            
        Raises:
            PasswordValidationError: If validate=True and password is weak
        """
        if validate:
            from api.auth_security import validate_password_strength
            validate_password_strength(password)
        
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    # -----------------------------
    # Representation
    # -----------------------------

    def __repr__(self):
        return f"<User {self.username}>"


# ==========================================================
# Refresh Token Model
# ==========================================================

class RefreshToken(db.Model):

    __tablename__ = "refresh_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    token_hash = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    revoked = db.Column(
        db.Boolean,
        default=False
    )

    user = db.relationship(
        "User",
        backref="refresh_tokens"
    )


# ==========================================================
# Verbal Autopsy Model
# ==========================================================

class VerbalAutopsy(db.Model):

    __tablename__ = "verbal_autopsy"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patientid = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    state_name = db.Column(
        db.String(100),
        nullable=True
    )

    lga_name = db.Column(
        db.String(100),
        nullable=True
    )

    facility_name = db.Column(
        db.String(100),
        nullable=True
    )

    datim_code = db.Column(
        db.String(100),
        nullable=False
    )

    age = db.Column(
        db.Integer,
        nullable=True
    )

    sex = db.Column(
        db.String(50),
        nullable=True
    )

    cause_of_death = db.Column(
        db.String(200),
        nullable=True
    )

    cause_list = db.Column(
        db.Integer,
        nullable=True
    )

    icd10 = db.Column(
        db.String(50),
        nullable=True
    )

    interviewer_name = db.Column(
        db.String(200),
        nullable=True
    )

    interview_year = db.Column(
        db.Integer,
        nullable=True
    )

    interview_month = db.Column(
        db.String(100),
        nullable=True
    )

    interview_day = db.Column(
        db.Integer,
        nullable=True
    )

    interview_time = db.Column(
        db.String(100),
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "patientid": self.patientid,
            "state_name": self.state_name,
            "lga_name": self.lga_name,
            "facility_name": self.facility_name,
            "datim_code": self.datim_code,
            "age": self.age,
            "sex": self.sex,
            "cause_of_death": self.cause_of_death,
            "cause_list": self.cause_list,
            "icd10": self.icd10,
            "interviewer_name": self.interviewer_name,
            "interview_year": self.interview_year,
            "interview_month": self.interview_month,
            "interview_day": self.interview_day,
            "interview_time": self.interview_time
        }

    def __repr__(self):
        return f"<VerbalAutopsy {self.patientid}>"