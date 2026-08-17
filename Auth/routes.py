"""
Authentication Routes

Handles:
- User registration
- Login
- Logout
- Role-based authentication checks
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
from models import User
from extensions import db


# ==========================================================
# Registration
# ==========================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new dashboard user.

    Newly registered users:
        - receive the normal "user" role
        - are not verified
        - are active
        - must be approved by an administrator
          before they can log in
    """

    # ------------------------------------------------------
    # Already logged in
    # ------------------------------------------------------

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard.index")
        )

    # ------------------------------------------------------
    # Registration submission
    # ------------------------------------------------------

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # --------------------------------------------------
        # Required fields
        # --------------------------------------------------

        if not username or not email or not password:

            flash(
                "Username, email and password are required.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        # --------------------------------------------------
        # Password confirmation
        # --------------------------------------------------

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        # --------------------------------------------------
        # Check username
        # --------------------------------------------------

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            flash(
                "That username is already registered.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        # --------------------------------------------------
        # Check email
        # --------------------------------------------------

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "That email address is already registered.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        # --------------------------------------------------
        # Create user
        # --------------------------------------------------

        user = User(
            username=username,
            email=email,

            # New registrations always start as
            # regular users.
            role="user",

            # Administrator approval required.
            is_verified=False,

            # Account exists but cannot log in until
            # approved.
            is_active=True,
        )

        user.set_password(
            password
        )

        db.session.add(
            user
        )

        db.session.commit()

        # --------------------------------------------------
        # Registration successful
        # --------------------------------------------------

        flash(
            "Registration successful. "
            "Your account is waiting for administrator approval.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # Display registration page
    # ------------------------------------------------------

    return render_template(
        "register.html"
    )


# ==========================================================
# Login
# ==========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Authenticate a user and start a Flask-Login session.
    """

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard.index")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            username=username
        ).first()

        # --------------------------------------------------
        # Credentials
        # --------------------------------------------------

        if not user or not user.check_password(password):

            flash(
                "Invalid username or password.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        # --------------------------------------------------
        # Account status
        # --------------------------------------------------

        if not user.is_active:

            flash(
                "Your account has been deactivated. "
                "Please contact an administrator.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        # --------------------------------------------------
        # Normalize role
        # --------------------------------------------------

        role = (
            user.role or ""
        ).strip().lower()

        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        if role in {
            "admin",
            "administrator",
        }:

            login_user(user)

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard.index")
            )

        # --------------------------------------------------
        # NON-ADMIN USERS MUST BE APPROVED
        # --------------------------------------------------

        if not user.is_verified:

            flash(
                "Your account has not yet been approved "
                "by an administrator.",
                "warning"
            )

            return render_template(
                "login.html"
            )

        # --------------------------------------------------
        # UPLOAD USER
        # --------------------------------------------------

        if role == "upload_user":

            login_user(user)

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard.index")
            )

        # --------------------------------------------------
        # REGULAR USER
        # --------------------------------------------------

        if role == "user":

            login_user(user)

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard.index")
            )

        # --------------------------------------------------
        # UNKNOWN ROLE
        # --------------------------------------------------

        flash(
            "Your account has an invalid role. "
            "Please contact an administrator.",
            "danger"
        )

        return render_template(
            "login.html"
        )

    return render_template(
        "login.html"
    )


# ==========================================================
# Logout
# ==========================================================

@auth_bp.route("/logout")
@login_required
def logout():
    """
    Log the current user out and return to login.
    """

    logout_user()

    flash(
        "You have been logged out successfully.",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )