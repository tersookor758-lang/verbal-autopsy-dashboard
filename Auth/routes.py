"""
Authentication Routes

Handles:
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


# ==========================================================
# Login
# ==========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

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
        # Find user
        # --------------------------------------------------

        user = User.query.filter_by(
            username=username
        ).first()

        # --------------------------------------------------
        # Check username/password
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
        # Normalize role
        #
        # This allows existing accounts using
        # "Administrator" to continue working while the
        # system is being migrated to "admin".
        # --------------------------------------------------

        role = (
            user.role or ""
        ).strip().lower()

        # --------------------------------------------------
        # Check account status
        #
        # Admins can still be deactivated by the system,
        # so is_active applies to everyone.
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

        # ==================================================
        # ADMIN
        # ==================================================
        #
        # IMPORTANT:
        # Admins DO NOT require is_verified.
        #
        # We accept both:
        #
        #     admin
        #     Administrator
        #
        # because your existing database may still contain
        # the old role name.
        # ==================================================

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

        # ==================================================
        # UPLOAD USER
        # ==================================================

        if role == "upload_user":

            if not user.is_verified:

                flash(
                    "Your upload-user account has not yet "
                    "been approved by an administrator.",
                    "warning"
                )

                return render_template(
                    "login.html"
                )

            login_user(user)

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard.index")
            )

        # ==================================================
        # REGULAR USER
        # ==================================================

        if role == "user":

            login_user(user)

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard.index")
            )

        # ==================================================
        # UNKNOWN ROLE
        # ==================================================

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
# Logout
# ==========================================================

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )