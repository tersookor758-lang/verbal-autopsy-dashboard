"""
Authentication Routes

Handles:
- Login
- Logout
- User Registration
- Role-based authentication
"""

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from auth import auth_bp
from extensions import db
from models import User
from api.auth_security import PasswordValidationError


# ==========================================================
# Login
# ==========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an active user and start their session."""

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.index")
        )

    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        if not username or not password:
            flash(
                "Username and password are required.",
                "danger",
            )
            return render_template("login.html")

        user = User.query.filter_by(
            username=username
        ).first()

        if not user or not user.check_password(password):
            flash(
                "Invalid username or password.",
                "danger",
            )
            return render_template("login.html")

        if not user.is_active:
            flash(
                "Your account has been deactivated. "
                "Please contact an administrator.",
                "danger",
            )
            return render_template("login.html")

        role = (
            user.role or ""
        ).strip().lower()

        if role not in {
            "user",
            "upload_user",
            "admin",
            "administrator",
        }:
            flash(
                "Your account has an invalid role. "
                "Please contact an administrator.",
                "danger",
            )
            return render_template("login.html")

        login_user(user)

        flash(
            "Login successful.",
            "success",
        )

        return redirect(
            url_for("dashboard.index")
        )

    return render_template("login.html")


# ==========================================================
# Registration
# ==========================================================

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Register a new regular user.

    Public registration never grants upload or admin
    privileges.
    """

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.index")
        )

    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        email = request.form.get(
            "email",
            "",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        if not username or not email or not password:
            flash(
                "All required fields must be completed.",
                "danger",
            )
            return render_template("signup.html")

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger",
            )
            return render_template("signup.html")

        if User.query.filter_by(
            username=username
        ).first():

            flash(
                "That username is already in use.",
                "danger",
            )
            return render_template("signup.html")

        if User.query.filter_by(
            email=email
        ).first():

            flash(
                "That email address is already registered.",
                "danger",
            )
            return render_template("signup.html")

        user = User(
            username=username,
            email=email,
            role="user",
            is_verified=True,
            is_active=True,
        )

        try:
            user.set_password(
                password,
                validate=True,
            )

        except PasswordValidationError as error:
            flash(
                str(error),
                "danger",
            )
            return render_template("signup.html")

        db.session.add(user)

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            flash(
                "Registration could not be completed. "
                "Please try again.",
                "danger",
            )

            return render_template("signup.html")

        flash(
            "Registration successful. "
            "You can now log in to your account.",
            "success",
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template("signup.html")


# ==========================================================
# Logout
# ==========================================================

@auth_bp.route("/logout")
@login_required
def logout():
    """Log the current user out."""

    logout_user()

    flash(
        "You have been logged out successfully.",
        "info",
    )

    return redirect(
        url_for("auth.login")
    )