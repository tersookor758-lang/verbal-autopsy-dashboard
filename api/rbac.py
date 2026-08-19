from functools import wraps

from flask import current_app, g, request
from flask_login import current_user

from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request,
)
from flask_jwt_extended.exceptions import (
    JWTExtendedException,
    NoAuthorizationError,
)
from jwt import ExpiredSignatureError, PyJWTError

from api.auth_security import (
    log_forbidden_access,
    log_unauthorized_access,
)
from extensions import db
from models import User


# ==========================================================
# Authorization Response
# ==========================================================

def authorization_response(message, status_code):
    """Return a standard authorization error response."""

    return {"message": message}, status_code


# ==========================================================
# JWT User Lookup
# ==========================================================

def get_authenticated_user():
    """
    Load the database user associated with the JWT identity.

    The database is checked on every request so role and account
    changes made by an administrator take effect immediately.
    """

    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):

        current_app.logger.warning(
            "Invalid JWT identity: %s",
            identity
        )

        return None

    return db.session.get(User, user_id)


# ==========================================================
# Flask-Login User Lookup
# ==========================================================

def get_session_user():
    """
    Reload the currently logged-in user from the database.

    This ensures administrator changes to the account are
    reflected immediately.
    """

    if not current_user.is_authenticated:
        return None

    user_id = getattr(current_user, "id", None)

    if user_id is None:
        return None

    return db.session.get(User, user_id)


# ==========================================================
# Account Status Check
# ==========================================================

def check_account_status(user, endpoint, ip_address):
    """
    Check whether the authenticated user has an active account.

    Regular users are allowed without administrator approval.
    """

    if user is None:

        log_unauthorized_access(
            endpoint,
            "anonymous",
            ip_address
        )

        return authorization_response(
            "Authentication is required.",
            401
        )

    # ------------------------------------------------------
    # Inactive accounts cannot access the application.
    # ------------------------------------------------------

    if not user.is_active:

        current_app.logger.warning(
            "Inactive user %s attempted to access %s",
            user.id,
            endpoint
        )

        return authorization_response(
            "Your account has been deactivated.",
            403
        )

    return None


# ==========================================================
# Role Check
# ==========================================================

def check_user_role(
    user,
    allowed_role_set,
    endpoint,
    ip_address
):
    """
    Verify that the user is active and has an allowed role.

    Application roles:

        user
            Dashboard and download access.

        upload_user
            Dashboard, download and upload access.

        admin
            Full system access.
    """

    account_error = check_account_status(
        user,
        endpoint,
        ip_address
    )

    if account_error:
        return account_error

    # ------------------------------------------------------
    # Normalize the user's role.
    # ------------------------------------------------------

    role = (
        user.role or ""
    ).strip().lower()

    # ------------------------------------------------------
    # Normalize roles supplied to the decorator.
    # ------------------------------------------------------

    allowed_roles = {
        str(allowed_role).strip().lower()
        for allowed_role in allowed_role_set
    }

    # ------------------------------------------------------
    # Reject unknown roles.
    # ------------------------------------------------------

    if role not in {
        "user",
        "upload_user",
        "admin",
    }:

        current_app.logger.warning(
            "User %s has invalid role: %s",
            user.id,
            role
        )

        return authorization_response(
            "Your account has an invalid role. "
            "Please contact an administrator.",
            403
        )

    # ------------------------------------------------------
    # Enforce permission.
    # ------------------------------------------------------

    if role not in allowed_roles:

        log_forbidden_access(
            endpoint,
            user.username,
            user.id,
            ",".join(sorted(allowed_roles)),
            role,
            ip_address
        )

        return authorization_response(
            "You do not have permission to perform this action.",
            403
        )

    # Make the authenticated user and role available to
    # other parts of the current request.
    g.current_user = user
    g.current_user_role = role

    return None


# ==========================================================
# Role Required Decorator
# ==========================================================

def role_required(*allowed_roles):
    """
    Protect a route using authentication and role-based access.

    Supported authentication methods:

        Flask-Login
            Used by the web dashboard.

        JWT
            Used by Swagger and external API clients.
    """

    if not allowed_roles:
        raise ValueError(
            "role_required requires at least one allowed role."
        )

    allowed_role_set = set(allowed_roles)

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            ip_address = request.remote_addr
            endpoint = request.endpoint or "unknown"

            # ==================================================
            # 1. Flask-Login authentication
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

                return function(*args, **kwargs)

            # ==================================================
            # 2. JWT authentication
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

                current_app.logger.warning(
                    "Invalid JWT attempted on %s",
                    endpoint
                )

                return authorization_response(
                    "Invalid authorization token.",
                    401
                )

            # ==================================================
            # 3. Load JWT user and check permissions
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

            return function(*args, **kwargs)

        return wrapper

    return decorator