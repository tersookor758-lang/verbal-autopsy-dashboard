from flask import flash, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from api.auth_security import (
    PasswordValidationError,
    log_failed_login,
    log_logout,
    log_successful_login,
)
from extensions import db, limiter
from models import User


def login():
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

        ip_address = request.remote_addr

        if not username or not password:
            flash(
                "Username and password are required.",
                "danger",
            )

            log_failed_login(
                username or "unknown",
                ip_address,
                "Missing credentials",
            )

            return render_template(
                "login.html"
            )

        user = User.query.filter_by(
            username=username
        ).first()

        if (
            not user
            or not user.check_password(password)
        ):
            log_failed_login(
                username,
                ip_address,
                "Invalid credentials",
            )

            flash(
                "Invalid username or password.",
                "danger",
            )

            return render_template(
                "login.html"
            )

        if not user.is_verified:
            log_failed_login(
                username,
                ip_address,
                "Account not verified",
            )

            flash(
                "Your account is awaiting administrator approval.",
                "warning",
            )

            return render_template(
                "login.html"
            )

        if not user.is_active:
            log_failed_login(
                username,
                ip_address,
                "Account deactivated",
            )

            flash(
                "Your account has been deactivated. "
                "Please contact an administrator.",
                "danger",
            )

            return render_template(
                "login.html"
            )

        role = (
            user.role or ""
        ).strip().lower()

        if role not in {
            "user",
            "upload_user",
            "admin",
        }:
            log_failed_login(
                username,
                ip_address,
                "Invalid account role",
            )

            flash(
                "Your account has an invalid role. "
                "Please contact an administrator.",
                "danger",
            )

            return render_template(
                "login.html"
            )

        login_user(user)

        log_successful_login(
            username,
            ip_address,
            user.id,
        )

        flash(
            "Login successful.",
            "success",
        )

        return redirect(
            url_for("dashboard.index")
        )

    return render_template(
        "login.html"
    )


def signup():
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

        if (
            not username
            or not email
            or not password
        ):
            flash(
                "All required fields must be completed.",
                "danger",
            )

            return render_template(
                "signup.html"
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger",
            )

            return render_template(
                "signup.html"
            )

        if User.query.filter_by(
            username=username
        ).first():
            flash(
                "That username is already in use.",
                "danger",
            )

            return render_template(
                "signup.html"
            )

        if User.query.filter_by(
            email=email
        ).first():
            flash(
                "That email address is already registered.",
                "danger",
            )

            return render_template(
                "signup.html"
            )

        user = User(
            username=username,
            email=email,
            role="user",
            is_verified=False,
            is_active=False,
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

            return render_template(
                "signup.html"
            )

        db.session.add(user)

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            flash(
                "Registration could not be completed. Please try again.",
                "danger",
            )

            return render_template(
                "signup.html"
            )

        flash(
            "Registration successful. Your account is awaiting "
            "administrator approval.",
            "success",
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "signup.html"
    )


@login_required
def logout():
    username = (
        current_user.username
        if current_user.is_authenticated
        else "unknown"
    )

    user_id = (
        current_user.id
        if current_user.is_authenticated
        else None
    )

    ip_address = request.remote_addr

    logout_user()

    log_logout(
        username,
        user_id,
        ip_address,
    )

    flash(
        "You have been logged out successfully.",
        "info",
    )

    return redirect(
        url_for("auth.login")
    )


@limiter.limit("5 per minute")
def rate_limited_login():
    return login()


@limiter.limit("3 per hour")
def rate_limited_signup():
    return signup()


def register_auth_routes(auth_bp):
    auth_bp.add_url_rule(
        "/login",
        endpoint="login",
        view_func=rate_limited_login,
        methods=["GET", "POST"],
    )

    auth_bp.add_url_rule(
        "/signup",
        endpoint="signup",
        view_func=rate_limited_signup,
        methods=["GET", "POST"],
    )

    auth_bp.add_url_rule(
        "/logout",
        endpoint="logout",
        view_func=logout,
        methods=["GET"],
    )