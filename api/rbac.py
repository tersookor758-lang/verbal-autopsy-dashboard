from functools import wraps

from flask import g, current_app, request
from flask_login import current_user

from flask_jwt_extended.exceptions import (
    JWTExtendedException,
    NoAuthorizationError,
)
from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request,
)
from jwt import ExpiredSignatureError, PyJWTError

from extensions import db
from models import User
from api.auth_security import (
    log_unauthorized_access,
    log_forbidden_access,
)


def authorization_response(message, status_code):
    return {
        "message": message
    }, status_code


def get_authenticated_user():
    """
    Return the current database user for a verified JWT identity.

    The JWT identity contains the user's database ID.
    The user is retrieved from the database on every request
    so that role changes take effect immediately.
    """

    identity = get_jwt_identity()

    try:
        user_id = int(identity)

    except (TypeError, ValueError):

        current_app.logger.warning(
            f"Invalid JWT identity format: {identity}"
        )

        return None

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        current_app.logger.warning(
            f"User not found for JWT identity: {user_id}"
        )

        return None

    return user


def get_session_user():
    """
    Return the currently authenticated Flask-Login user.

    This allows users who are already logged into the web dashboard
    to access protected API endpoints without requiring a separate
    JWT token in the browser.

    JWT authentication is still supported for API clients and Swagger.
    """

    if current_user.is_authenticated:

        user_id = getattr(
            current_user,
            "id",
            None
        )

        if user_id is None:
            return None

        user = db.session.get(
            User,
            user_id
        )

        return user

    return None


def check_user_role(
    user,
    allowed_role_set,
    endpoint,
    ip_address
):
    """
    Check whether the authenticated user has permission
    to access the requested resource.
    """

    if user is None:

        log_unauthorized_access(
            endpoint,
            "unknown",
            ip_address
        )

        return authorization_response(
            "Authentication is required.",
            401
        )

    g.current_user = user

    if user.role not in allowed_role_set:

        log_forbidden_access(
            endpoint,
            user.username,
            user.id,
            ",".join(
                sorted(allowed_role_set)
            ),
            user.role,
            ip_address
        )

        current_app.logger.warning(
            f"Permission denied: user {user.id} "
            f"({user.role}) attempted to access "
            f"resource requiring {allowed_role_set}"
        )

        return authorization_response(
            "Forbidden.",
            403
        )

    return None


def role_required(*allowed_roles):
    """
    Require an authenticated user with one of the allowed roles.

    Authentication methods supported:

    1. Flask-Login session
       Used by the web dashboard.

    2. JWT Bearer token
       Used by Swagger and external API clients.

    The Flask-Login session is checked first because dashboard
    users are already authenticated through the normal web login.

    JWT authentication remains available when no Flask-Login
    session exists.
    """

    if not allowed_roles:

        raise ValueError(
            "role_required requires at least one allowed role."
        )

    allowed_role_set = set(
        allowed_roles
    )

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            ip_address = request.remote_addr
            endpoint = request.endpoint or "unknown"

            # ==================================================
            # 1. Try the normal Flask-Login dashboard session
            # ==================================================

            session_user = get_session_user()

            if session_user is not None:

                authorization_error = check_user_role(
                    session_user,
                    allowed_role_set,
                    endpoint,
                    ip_address
                )

                if authorization_error:

                    return authorization_error

                return function(
                    *args,
                    **kwargs
                )

            # ==================================================
            # 2. No Flask-Login session.
            #    Try JWT authentication for API clients.
            # ==================================================

            try:

                verify_jwt_in_request()

            except NoAuthorizationError:

                log_unauthorized_access(
                    endpoint,
                    "anonymous",
                    ip_address
                )

                return authorization_response(
                    "Authentication is required. "
                    "Log in to the dashboard or provide "
                    "a valid Bearer token.",
                    401
                )

            except ExpiredSignatureError:

                return authorization_response(
                    "Authorization token has expired.",
                    401
                )

            except (
                JWTExtendedException,
                PyJWTError
            ):

                return authorization_response(
                    "Invalid authorization token.",
                    401
                )

            # ==================================================
            # 3. Retrieve the user associated with the JWT
            # ==================================================

            jwt_user = get_authenticated_user()

            authorization_error = check_user_role(
                jwt_user,
                allowed_role_set,
                endpoint,
                ip_address
            )

            if authorization_error:

                return authorization_error

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator