"""
Authentication Routes

Handles:
- Login
- Logout
- User Registration
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
from extensions import db
from models import User


# ==========================================================
# Login
# ==========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Authenticate a user and start a Flask-Login session.
    """

    # ------------------------------------------------------
    # Already logged in
    # ------------------------------------------------------

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.index")
        )

    # ------------------------------------------------------
    # Login submission
    # ------------------------------------------------------

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # --------------------------------------------------
        # Validate required fields
        # --------------------------------------------------

        if not username or not password:

            flash(
                "Username and password are required.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        # --------------------------------------------------
        # Find user
        # --------------------------------------------------

        user = User.query.filter_by(
            username=username
        ).first()

        # --------------------------------------------------
        # Check credentials
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
        # Check account status
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
        #
        # Administrators do not require approval.
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
        # ALL NON-ADMIN USERS MUST BE VERIFIED
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

    # ------------------------------------------------------
    # Display login page
    # ------------------------------------------------------

    return render_template(
        "login.html"
    )


# ==========================================================
# Registration
# ==========================================================

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Register a new user.

    New users can request:
        - user
        - upload_user

    Nobody can create an admin account through public
    registration.

    New accounts require administrator approval.
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

        requested_role = request.form.get(
            "role",
            "user"
        ).strip().lower()

        # --------------------------------------------------
        # Validate fields
        # --------------------------------------------------

        if not username or not email or not password:

            flash(
                "All required fields must be completed.",
                "danger"
            )

            return render_template(
                "signup.html"
            )

        # --------------------------------------------------
        # Confirm password
        # --------------------------------------------------

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return render_template(
                "signup.html"
            )

        # --------------------------------------------------
        # Only public roles are allowed
        #
        # Admin accounts must be created/managed by an
        # existing administrator.
        # --------------------------------------------------

        if requested_role not in {
            "user",
            "upload_user",
        }:

            requested_role = "user"

        # --------------------------------------------------
        # Check username
        # --------------------------------------------------

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            flash(
                "That username is already in use.",
                "danger"
            )

            return render_template(
                "signup.html"
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
                "signup.html"
            )

        # --------------------------------------------------
        # Create user
        # --------------------------------------------------

        user = User(
            username=username,
            email=email,
            role=requested_role,

            # New users must be approved by an administrator.
            is_verified=False,

            # Account is enabled but pending approval.
            is_active=True,
        )

        user.set_password(
            password,
            validate=True
        )

        db.session.add(user)
        db.session.commit()

        # --------------------------------------------------
        # Registration complete
        # --------------------------------------------------

        flash(
            "Registration successful. "
            "Your account is awaiting administrator approval.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # Display registration page
    # ------------------------------------------------------

    return render_template(
        "signup.html"
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