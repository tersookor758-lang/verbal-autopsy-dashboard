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
# Standard Authorization Response
# ==========================================================

def authorization_response(message, status_code):
    return {
        "message": message
    }, status_code


# ==========================================================
# JWT User Lookup
# ==========================================================

def get_authenticated_user():
    """
    Retrieve the database User associated with the JWT identity.

    The user's record is loaded from the database on every request.
    This is intentional because role, verification, and account
    status changes should take effect immediately.
    """

    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):

        current_app.logger.warning(
            "Invalid JWT identity format: %s",
            identity
        )

        return None

    user = db.session.get(
        User,
        user_id
    )

    if user is None:

        current_app.logger.warning(
            "No user found for JWT identity: %s",
            user_id
        )

        return None

    return user


# ==========================================================
# Flask-Login Session User Lookup
# ==========================================================

def get_session_user():
    """
    Retrieve the current Flask-Login user from the database.

    The database record is fetched again so that changes to:
        - role
        - verification
        - active status

    take effect immediately.
    """

    if not current_user.is_authenticated:
        return None

    user_id = getattr(
        current_user,
        "id",
        None
    )

    if user_id is None:
        return None

    return db.session.get(
        User,
        user_id
    )


# ==========================================================
# Account Verification / Status Check
# ==========================================================

def check_account_status(
    user,
    endpoint,
    ip_address
):
    """
    Verify that an authenticated account has been approved
    and is still active.

    This is separate from role authorization.
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

    # ------------------------------------------------------
    # Account must be verified by an administrator
    # ------------------------------------------------------

    if not user.is_verified:

        current_app.logger.warning(
            "Unverified user %s attempted to access %s",
            user.id,
            endpoint
        )

        return authorization_response(
            "Your account has not been verified by an administrator.",
            403
        )

    # ------------------------------------------------------
    # Account must still be active
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

    # Make the current database user available to the request.
    g.current_user = user

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
    Verify:
        1. The user exists.
        2. The user is verified.
        3. The user is active.
        4. The user has one of the required roles.
    """

    account_error = check_account_status(
        user,
        endpoint,
        ip_address
    )

    if account_error:
        return account_error

    # ------------------------------------------------------
    # Role normalization
    # ------------------------------------------------------

    role = (user.role or "").strip().lower()

    # ------------------------------------------------------
    # Backward compatibility with the old project roles.
    #
    # Old role -> New role
    #
    # Administrator -> admin
    # Editor        -> upload_user
    # Viewer        -> user
    #
    # This lets the API continue working safely while the
    # database is being migrated.
    # ------------------------------------------------------

    legacy_role_map = {
        "administrator": "admin",
        "editor": "upload_user",
        "viewer": "user",
    }

    normalized_role = legacy_role_map.get(
        role,
        role
    )

    normalized_allowed_roles = {
        legacy_role_map.get(
            str(allowed_role).strip().lower(),
            str(allowed_role).strip().lower()
        )
        for allowed_role in allowed_role_set
    }

    # ------------------------------------------------------
    # Enforce role
    # ------------------------------------------------------

    if normalized_role not in normalized_allowed_roles:

        log_forbidden_access(
            endpoint,
            user.username,
            user.id,
            ",".join(
                sorted(normalized_allowed_roles)
            ),
            normalized_role,
            ip_address
        )

        current_app.logger.warning(
            "Permission denied: user %s (%s) attempted "
            "to access %s requiring roles %s",
            user.id,
            normalized_role,
            endpoint,
            normalized_allowed_roles
        )

        return authorization_response(
            "You do not have permission to perform this action.",
            403
        )

    # ------------------------------------------------------
    # Expose normalized role to the request.
    #
    # This can be useful to other parts of the application.
    # ------------------------------------------------------

    g.current_user_role = normalized_role

    return None


# ==========================================================
# Role Required Decorator
# ==========================================================

def role_required(*allowed_roles):
    """
    Protect a route/resource using authentication,
    account verification, account status, and role checks.

    Example:

        @role_required("user", "upload_user", "admin")

    A user must:
        - be authenticated
        - have a verified account
        - have an active account
        - possess one of the allowed roles

    Authentication methods supported:

        1. Flask-Login session
           Used by the web dashboard.

        2. JWT Bearer token
           Used by Swagger and external API clients.
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
            # 1. Try Flask-Login session authentication
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
            #
            #    Try JWT authentication for Swagger/API clients.
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
                    "Invalid JWT attempted on endpoint %s",
                    endpoint
                )

                return authorization_response(
                    "Invalid authorization token.",
                    401
                )

            # ==================================================
            # 3. Retrieve JWT-associated database user
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