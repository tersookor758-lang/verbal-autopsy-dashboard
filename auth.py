
"""
Browser authentication for the Verbal Autopsy Outcome Dashboard.

Handles:
- Login
- Signup
- Logout
- Flask-Login browser sessions
- Password validation
- Account status checks
- Login rate limiting
"""

from urllib.parse import urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
)
from sqlalchemy.exc import IntegrityError

from extensions import db, limiter
from models import User


auth_bp = Blueprint(
    "auth",
    __name__,
)


def _is_safe_redirect_url(target):
    """Allow redirects only to local application URLs."""
    if not target:
        return False

    parsed = urlparse(target)

    return (
        not parsed.scheme
        and not parsed.netloc
        and target.startswith("/")
        and not target.startswith("//")
    )


def _get_safe_next_url():
    """Return a safe local next URL from the request."""
    next_url = request.args.get("next")

    if not next_url:
        next_url = request.form.get("next")

    if _is_safe_redirect_url(next_url):
        return next_url

    return None


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    """Authenticate a user and create a Flask-Login session."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    next_url = _get_safe_next_url()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash(
                "Username and password are required.",
                "danger",
            )
            return render_template(
                "login.html",
                next=next_url,
            )

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash(
                "Invalid username or password.",
                "danger",
            )
            return render_template(
                "login.html",
                next=next_url,
            )

        if not user.is_active:
            flash(
                "Your account has been deactivated. "
                "Please contact an administrator.",
                "danger",
            )
            return render_template(
                "login.html",
                next=next_url,
            )

        login_user(
            user,
            remember=True,
        )

        flash(
            "Login successful.",
            "success",
        )

        if next_url:
            return redirect(next_url)

        return redirect(url_for("dashboard.index"))

    return render_template(
        "login.html",
        next=next_url,
    )


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Create a regular user account."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            request.form.get("password_confirm", ""),
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

        if User.query.filter_by(username=username).first():
            flash(
                "That username is already in use.",
                "danger",
            )
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash(
                "That email address is already registered.",
                "danger",
            )
            return render_template("signup.html")

        user = User(
            username=username,
            email=email,
            role="user",
            is_verified=False,
            is_active=True,
        )

        try:
            user.set_password(
                password,
                validate=True,
            )

            db.session.add(user)
            db.session.commit()

        except (ValueError, TypeError) as exc:
            db.session.rollback()

            flash(
                str(exc),
                "danger",
            )
            return render_template("signup.html")

        except IntegrityError:
            db.session.rollback()

            flash(
                "Unable to create the account. "
                "The username or email may already exist.",
                "danger",
            )
            return render_template("signup.html")

        flash(
            "Account created successfully. "
            "You can now sign in.",
            "success",
        )

        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Log the current browser user out."""
    if current_user.is_authenticated:
        logout_user()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(url_for("auth.login"))


def create_auth_blueprint():
    """Return the browser authentication blueprint."""
    return auth_bp
