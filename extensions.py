"""
Application extensions.

Extensions are created here and initialized in app.py
to avoid circular imports.

Includes:
- SQLAlchemy
- Flask-Migrate
- Flask-Limiter
- Security logging
- Flask-Login
- Flask-JWT-Extended
- JWT error handlers
- Flask-Login user loader
"""

import logging

from flask import jsonify
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# ==========================================================
# Database
# ==========================================================

db = SQLAlchemy()


# ==========================================================
# Database Migrations
# ==========================================================

migrate = Migrate()


# ==========================================================
# Flask-Limiter
# ==========================================================

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
)


# ==========================================================
# Security Logger
# ==========================================================

security_logger = logging.getLogger(
    "security"
)

security_logger.setLevel(
    logging.INFO
)

if not security_logger.handlers:

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - SECURITY - "
        "%(levelname)s - %(message)s"
    )

    handler.setFormatter(
        formatter
    )

    security_logger.addHandler(
        handler
    )

security_logger.propagate = False


# ==========================================================
# Flask-Login
# ==========================================================

login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.login_message = (
    "Please log in to access this page."
)

login_manager.login_message_category = (
    "warning"
)


# ==========================================================
# Flask-JWT-Extended
# ==========================================================

jwt = JWTManager()


# ==========================================================
# JWT Error Response Helper
# ==========================================================

def jwt_error_response(
    message,
    status_code,
    error=None,
):
    """
    Return a consistent JSON response for JWT errors.
    """

    response = {
        "message": message,
    }

    if error:
        response["error"] = error

    return jsonify(
        response
    ), status_code


# ==========================================================
# Flask-Login User Loader
# ==========================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Reload the browser-session user for Flask-Login.
    """

    from models import User

    try:

        return db.session.get(
            User,
            int(user_id),
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


# ==========================================================
# JWT Error Handlers
# ==========================================================

@jwt.unauthorized_loader
def handle_missing_jwt(error):
    """
    Handle requests where no JWT was supplied.
    """

    return jwt_error_response(
        "Authorization header with a Bearer token is required.",
        401,
        error,
    )


@jwt.invalid_token_loader
def handle_invalid_jwt(error):
    """
    Handle malformed or invalid JWTs.
    """

    return jwt_error_response(
        "Invalid authorization token.",
        401,
        error,
    )


@jwt.expired_token_loader
def handle_expired_jwt(
    jwt_header,
    jwt_payload,
):
    """
    Handle expired JWT access tokens.
    """

    return jwt_error_response(
        "Authorization token has expired.",
        401,
    )


@jwt.revoked_token_loader
def handle_revoked_jwt(
    jwt_header,
    jwt_payload,
):
    """
    Handle revoked JWT access tokens.
    """

    return jwt_error_response(
        "Authorization token has been revoked.",
        401,
    )


@jwt.needs_fresh_token_loader
def handle_non_fresh_jwt(
    jwt_header,
    jwt_payload,
):
    """
    Handle endpoints that require a fresh JWT.
    """

    return jwt_error_response(
        "A fresh authorization token is required.",
        401,
    )


# ==========================================================
# JWT User Lookup Error
# ==========================================================

@jwt.user_lookup_error_loader
def handle_jwt_user_lookup_error(
    jwt_header,
    jwt_payload,
):
    """
    Handle a JWT whose associated user cannot be found.
    """

    return jwt_error_response(
        "The user associated with this authorization token "
        "could not be found.",
        401,
    )


# ==========================================================
# JWT Token Verification Error
# ==========================================================

@jwt.token_verification_failed_loader
def handle_jwt_token_verification_failed(
    jwt_header,
    jwt_payload,
):
    """
    Handle failed JWT token verification.
    """

    return jwt_error_response(
        "Authorization token verification failed.",
        401,
    )