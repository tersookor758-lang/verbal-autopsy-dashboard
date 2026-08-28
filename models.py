from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from extensions import db


# ==========================================================
# User Model
# ==========================================================

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    role = db.Column(
        db.String(50),
        nullable=False,
        default="user",
    )

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    # ======================================================
    # Password Methods
    # ======================================================

    def set_password(self, password, validate=False):
        """Hash and set the user's password."""

        if validate:
            from api.auth_security import validate_password_strength

            validate_password_strength(password)

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check a plain-text password against the stored hash."""

        return check_password_hash(
            self.password_hash,
            password,
        )

    # ======================================================
    # Role Helpers
    # ======================================================

    def is_admin(self):
        """Return True when the user is an administrator."""

        return self.role == "admin"

    def is_upload_user(self):
        """Return True when the user has upload permissions."""

        return self.role == "upload_user"

    def is_regular_user(self):
        """Return True when the user has normal user permissions."""

        return self.role == "user"

    def can_download(self):
        """Return True when the user's role permits downloads."""

        return self.role in {
            "user",
            "upload_user",
            "admin",
        }

    def can_upload(self):
        """Return True when the user's role permits uploads."""

        return self.role in {
            "upload_user",
            "admin",
        }

    def can_edit(self):
        """Return True when the user can edit records."""

        return self.role == "admin"

    def can_delete(self):
        """Return True when the user can delete records."""

        return self.role == "admin"

    def can_manage_users(self):
        """Return True when the user can manage other users."""

        return self.role == "admin"

    def can_access_dashboard(self):
        """Return True when the user's role permits dashboard access."""

        return self.role in {
            "user",
            "upload_user",
            "admin",
        }

    # ======================================================
    # Account Access
    # ======================================================

    def account_is_approved(self):
        """
        Return True only when the account is active and verified.
        """

        return (
            self.is_active is True
            and self.is_verified is True
        )

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self):
        return (
            f"<User {self.username} "
            f"role={self.role} "
            f"verified={self.is_verified} "
            f"active={self.is_active}>"
        )


# ==========================================================
# Refresh Token Model
# ==========================================================

class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    token_hash = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    revoked = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "refresh_tokens",
            cascade="all, delete-orphan",
        ),
    )


# ==========================================================
# Verbal Autopsy Model
# ==========================================================

class VerbalAutopsy(db.Model):
    __tablename__ = "verbal_autopsy"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    patientid = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    state_name = db.Column(
        db.String(100),
        nullable=True,
    )

    lga_name = db.Column(
        db.String(100),
        nullable=True,
    )

    facility_name = db.Column(
        db.String(100),
        nullable=True,
    )

    datim_code = db.Column(
        db.String(100),
        nullable=False,
    )

    age = db.Column(
        db.Integer,
        nullable=True,
    )

    sex = db.Column(
        db.String(50),
        nullable=True,
    )

    cause_of_death = db.Column(
        db.String(200),
        nullable=True,
    )

    cause_list = db.Column(
        db.Integer,
        nullable=True,
    )

    icd10 = db.Column(
        db.String(50),
        nullable=True,
    )

    interviewer_name = db.Column(
        db.String(200),
        nullable=True,
    )

    interview_year = db.Column(
        db.Integer,
        nullable=True,
    )

    interview_month = db.Column(
        db.String(100),
        nullable=True,
    )

    interview_day = db.Column(
        db.Integer,
        nullable=True,
    )

    interview_time = db.Column(
        db.String(100),
        nullable=True,
    )

    # ======================================================
    # Serialization
    # ======================================================

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
            "interview_time": self.interview_time,
        }

    def __repr__(self):
        return f"<VerbalAutopsy {self.patientid}>"