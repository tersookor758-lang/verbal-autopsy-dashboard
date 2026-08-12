from functools import wraps

from flask import g, current_app, request
from flask_jwt_extended.exceptions import (
    JWTExtendedException,
    NoAuthorizationError,
)
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from jwt import ExpiredSignatureError, PyJWTError

from extensions import db
from models import User
from api.auth_security import log_unauthorized_access, log_forbidden_access


def authorization_response(message, status_code):
    return {"message": message}, status_code


def get_authenticated_user():
    """
    Return the current database user for a verified JWT identity.
    
    Verifies JWT and retrieves the CURRENT user state from database
    to ensure role changes take effect immediately.
    """

    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        current_app.logger.warning(
            f"Invalid JWT identity format: {identity}"
        )
        return None

    user = db.session.get(User, user_id)
    
    if not user:
        current_app.logger.warning(
            f"User not found for JWT identity: {user_id}"
        )
        return None
    
    return user


def role_required(*allowed_roles):
    """
    Require a valid JWT and an authenticated user with one of the allowed roles.
    
    Verifies the user's CURRENT role from the database on each request,
    ensuring that role changes take effect immediately.

    Example:
        @role_required("Administrator")
        @role_required("Administrator", "Editor")
    """

    if not allowed_roles:
        raise ValueError("role_required requires at least one allowed role.")

    allowed_role_set = set(allowed_roles)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            ip_address = request.remote_addr
            endpoint = request.endpoint or "unknown"
            
            try:
                verify_jwt_in_request()
            except NoAuthorizationError:
                log_unauthorized_access(endpoint, "anonymous", ip_address)
                return authorization_response(
                    "Authorization header with a Bearer token is required.",
                    401,
                )
            except ExpiredSignatureError:
                return authorization_response(
                    "Authorization token has expired.",
                    401,
                )
            except (JWTExtendedException, PyJWTError):
                return authorization_response(
                    "Invalid authorization token.",
                    401,
                )

            user = get_authenticated_user()

            if user is None:
                log_unauthorized_access(endpoint, "unknown", ip_address)
                return authorization_response("Authentication is required.", 401)

            g.current_user = user

            if user.role not in allowed_role_set:
                log_forbidden_access(
                    endpoint,
                    user.username,
                    user.id,
                    ",".join(allowed_role_set),
                    user.role,
                    ip_address
                )
                current_app.logger.warning(
                    f"Permission denied: user {user.id} ({user.role}) "
                    f"attempted to access resource requiring {allowed_role_set}"
                )
                return authorization_response("Forbidden.", 403)

            return function(*args, **kwargs)

        return wrapper

    return decorator
