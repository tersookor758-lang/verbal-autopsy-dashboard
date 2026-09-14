from datetime import datetime, timedelta
import hashlib
import secrets

from flask import current_app, request
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, Resource, fields

from api.api import api
from api.rbac import get_authenticated_user, role_required
from api.auth_security import (
    PasswordValidationError,
    log_failed_login,
    log_logout,
    log_revoked_token_reuse,
    log_successful_login,
    log_token_refresh,
    validate_password_strength,
)
from extensions import db, limiter
from models import RefreshToken, User


auth_ns = Namespace(
    "auth",
    description="Authentication and authorization operations",
)


# ==========================================================
# Swagger Models
# ==========================================================

login_request_model = api.model(
    "LoginRequest",
    {
        "username": fields.String(
            required=True,
            description="Username for the account.",
        ),
        "password": fields.String(
            required=True,
            description="Password for the account.",
        ),
    },
)

refresh_request_model = api.model(
    "RefreshRequest",
    {
        "refresh_token": fields.String(
            required=True,
            description="Refresh token issued during login or token refresh.",
        ),
    },
)

logout_request_model = api.model(
    "LogoutRequest",
    {
        "refresh_token": fields.String(
            required=True,
            description="Refresh token to revoke.",
        ),
    },
)

auth_user_model = api.model(
    "AuthUser",
    {
        "id": fields.Integer(
            required=True,
            description="User ID.",
        ),
        "username": fields.String(
            required=True,
            description="Username for the account.",
        ),
        "email": fields.String(
            required=True,
            description="User email address.",
        ),
        "role": fields.String(
            required=True,
            description="User role.",
        ),
    },
)

login_response_model = api.model(
    "LoginResponse",
    {
        "message": fields.String(
            required=True,
            description="Login status message.",
            example="Login successful.",
        ),
        "access_token": fields.String(
            required=True,
            description="JWT access token for Bearer authentication.",
        ),
        "refresh_token": fields.String(
            required=True,
            description="Opaque refresh token used to request a new access token.",
        ),
        "token_type": fields.String(
            required=True,
            description="Token type used in the Authorization header.",
            example="Bearer",
        ),
        "expires_in": fields.Integer(
            required=True,
            description="Access token lifetime in seconds.",
            example=900,
        ),
        "user": fields.Nested(
            auth_user_model,
            required=True,
            description="Authenticated user details.",
        ),
    },
)

token_response_model = api.model(
    "TokenResponse",
    {
        "message": fields.String(
            required=True,
            description="Token status message.",
        ),
        "access_token": fields.String(
            required=True,
            description="JWT access token for Bearer authentication.",
        ),
        "refresh_token": fields.String(
            required=True,
            description="Opaque refresh token used to request a new access token.",
        ),
        "token_type": fields.String(
            required=True,
            description="Token type used in the Authorization header.",
            example="Bearer",
        ),
        "expires_in": fields.Integer(
            required=True,
            description="Access token lifetime in seconds.",
            example=900,
        ),
    },
)

message_response_model = api.model(
    "AuthMessageResponse",
    {
        "message": fields.String(
            required=True,
            description="Response status message.",
        ),
    },
)


# ==========================================================
# Token Configuration
# ==========================================================

ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME = timedelta(days=30)

VALID_ROLES = {
    "user",
    "upload_user",
    "admin",
}


# ==========================================================
# Helper Functions
# ==========================================================

def error_response(message, status_code):
    """Return a consistent API error response."""
    return {
        "message": message,
    }, status_code


def user_to_dict(user):
    """Convert a User model into a safe API response."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }


def hash_refresh_token(token):
    """Hash a refresh token before storing or querying it."""
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_refresh_token(user_id):
    """Generate an opaque refresh token and store only its hash."""
    raw_token = secrets.token_urlsafe(64)

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(raw_token),
        expires_at=datetime.utcnow() + REFRESH_TOKEN_LIFETIME,
    )

    db.session.add(refresh_token)

    return raw_token


def create_user_access_token(user):
    """Create a JWT access token for the authenticated user."""
    return create_access_token(
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role,
        },
        expires_delta=ACCESS_TOKEN_LIFETIME,
    )


def token_response(message, user, include_user=False):
    """Create a complete access-token and refresh-token response."""
    access_token = create_user_access_token(user)
    refresh_token = create_refresh_token(user.id)

    response = {
        "message": message,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": int(
            ACCESS_TOKEN_LIFETIME.total_seconds()
        ),
    }

    if include_user:
        response["user"] = user_to_dict(user)

    return response


def get_refresh_token(raw_token):
    """Find a refresh token by its stored hash."""
    token_hash = hash_refresh_token(raw_token)

    return RefreshToken.query.filter_by(
        token_hash=token_hash
    ).first()


def validate_user_role(user):
    """
    Validate the user's stored role.

    Authentication never changes a user's role.
    Roles are managed through the administrator system.
    """
    if user.role not in VALID_ROLES:
        current_app.logger.error(
            "User %s has an invalid role: %s",
            user.id,
            user.role,
        )

        return False

    return True


def account_can_authenticate(user):
    """
    Check whether the account is allowed to authenticate.

    Verification is an administrative account state.
    The active flag controls whether authentication is allowed.
    """
    if not user.is_active:
        return False

    if not validate_user_role(user):
        return False

    return True


# ==========================================================
# Login
# ==========================================================

@auth_ns.route("/login")
class Login(Resource):

    @auth_ns.expect(
        login_request_model,
        validate=False,
    )
    @auth_ns.response(
        200,
        "Login successful.",
        login_response_model,
    )
    @auth_ns.response(
        400,
        "Username and password are required.",
        message_response_model,
    )
    @auth_ns.response(
        401,
        "Invalid username or password.",
        message_response_model,
    )
    @auth_ns.response(
        403,
        "Account is inactive or has an invalid role.",
        message_response_model,
    )
    @auth_ns.response(
        429,
        "Too many login attempts.",
        message_response_model,
    )
    @limiter.limit("5 per minute")
    def post(self):
        """Authenticate a user and issue access and refresh tokens."""
        data = request.get_json(silent=True) or {}

        username = str(
            data.get("username", "")
        ).strip()

        password = data.get("password", "")

        ip_address = request.remote_addr

        if not username or not password:
            return error_response(
                "Username and password are required.",
                400,
            )

        user = User.query.filter_by(
            username=username
        ).first()

        if not user or not user.check_password(password):
            log_failed_login(
                username,
                ip_address,
                "Invalid credentials",
            )

            return error_response(
                "Invalid username or password.",
                401,
            )

        if not account_can_authenticate(user):
            current_app.logger.warning(
                "Authentication denied for user %s.",
                user.username,
            )

            return error_response(
                "Your account is inactive or has an invalid role configuration.",
                403,
            )

        response = token_response(
            "Login successful.",
            user,
            include_user=True,
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to create refresh token for user %s.",
                user.id,
            )

            return error_response(
                "Authentication could not be completed.",
                500,
            )

        log_successful_login(
            username,
            ip_address,
            user.id,
        )

        return response, 200


# ==========================================================
# Refresh Token
# ==========================================================

@auth_ns.route("/refresh")
class Refresh(Resource):

    @auth_ns.expect(
        refresh_request_model,
        validate=False,
    )
    @auth_ns.response(
        200,
        "Token refreshed successfully.",
        token_response_model,
    )
    @auth_ns.response(
        400,
        "Refresh token is required.",
        message_response_model,
    )
    @auth_ns.response(
        401,
        "Refresh token is invalid, revoked, expired, or orphaned.",
        message_response_model,
    )
    def post(self):
        """Rotate a refresh token and issue a new token pair."""
        data = request.get_json(silent=True) or {}

        raw_token = str(
            data.get("refresh_token", "")
        ).strip()

        ip_address = request.remote_addr

        if not raw_token:
            return error_response(
                "Refresh token is required.",
                400,
            )

        refresh_token = get_refresh_token(
            raw_token
        )

        if not refresh_token:
            return error_response(
                "Invalid refresh token.",
                401,
            )

        user = db.session.get(
            User,
            refresh_token.user_id,
        )

        if not user:
            try:
                refresh_token.revoked = True
                db.session.commit()
            except Exception:
                db.session.rollback()

            log_token_refresh(
                "unknown",
                refresh_token.user_id,
                success=False,
                reason="User not found",
            )

            return error_response(
                "User associated with this token was not found.",
                401,
            )

        if refresh_token.revoked:
            log_revoked_token_reuse(
                user.username,
                user.id,
                ip_address,
                "refresh",
            )

            log_token_refresh(
                user.username,
                user.id,
                success=False,
                reason="Token already revoked",
            )

            return error_response(
                "Refresh token has been revoked.",
                401,
            )

        if refresh_token.expires_at <= datetime.utcnow():
            try:
                refresh_token.revoked = True
                db.session.commit()
            except Exception:
                db.session.rollback()

            log_token_refresh(
                user.username,
                user.id,
                success=False,
                reason="Token expired",
            )

            return error_response(
                "Refresh token has expired.",
                401,
            )

        if not account_can_authenticate(user):
            return error_response(
                "Your account is inactive or has an invalid role configuration.",
                403,
            )

        try:
            refresh_token.revoked = True

            response = token_response(
                "Token refreshed successfully.",
                user,
            )

            db.session.commit()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to rotate refresh token for user %s.",
                user.id,
            )

            return error_response(
                "Token refresh could not be completed.",
                500,
            )

        log_token_refresh(
            user.username,
            user.id,
            success=True,
        )

        return response, 200


# ==========================================================
# Logout
# ==========================================================

@auth_ns.route("/logout")
class Logout(Resource):

    @auth_ns.expect(
        logout_request_model,
        validate=False,
    )
    @auth_ns.response(
        200,
        "Logout successful.",
        message_response_model,
    )
    @auth_ns.response(
        400,
        "Refresh token is required.",
        message_response_model,
    )
    @auth_ns.response(
        401,
        "Invalid refresh token.",
        message_response_model,
    )
    def post(self):
        """Revoke a refresh token."""
        data = request.get_json(silent=True) or {}

        raw_token = str(
            data.get("refresh_token", "")
        ).strip()

        ip_address = request.remote_addr

        if not raw_token:
            return error_response(
                "Refresh token is required.",
                400,
            )

        refresh_token = get_refresh_token(
            raw_token
        )

        if not refresh_token:
            return error_response(
                "Invalid refresh token.",
                401,
            )

        user = db.session.get(
            User,
            refresh_token.user_id,
        )

        username = (
            user.username
            if user
            else "unknown"
        )

        try:
            refresh_token.revoked = True
            db.session.commit()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to revoke refresh token.",
            )

            return error_response(
                "Logout could not be completed.",
                500,
            )

        if user:
            log_logout(
                username,
                user.id,
                ip_address,
            )

        return {
            "message": "Logout successful.",
        }, 200


# ==========================================================
# Current User
# ==========================================================

@auth_ns.route("/me")
class CurrentUser(Resource):

    @role_required(
        "admin",
        "upload_user",
        "user",
    )
    @auth_ns.response(
        200,
        "Current authenticated user.",
        auth_user_model,
    )
    @auth_ns.response(
        401,
        "Missing or invalid Authorization header.",
        message_response_model,
    )
    @auth_ns.response(
        403,
        "Forbidden.",
        message_response_model,
    )
    @auth_ns.response(
        404,
        "User not found.",
        message_response_model,
    )
    def get(self):
        """Return the currently authenticated user."""
        user = get_authenticated_user()

        if not user:
            return error_response(
                "User not found.",
                404,
            )

        return user_to_dict(user), 200


# ==========================================================
# Revoke All Refresh Tokens
# ==========================================================

@auth_ns.route("/revoke-all")
class RevokeAllTokens(Resource):

    @role_required(
        "admin",
        "upload_user",
        "user",
    )
    @auth_ns.response(
        200,
        "All tokens revoked successfully.",
        message_response_model,
    )
    @auth_ns.response(
        401,
        "Missing or invalid Authorization header.",
        message_response_model,
    )
    @auth_ns.response(
        403,
        "Forbidden.",
        message_response_model,
    )
    @auth_ns.response(
        404,
        "User not found.",
        message_response_model,
    )
    @auth_ns.doc(
        description=(
            "Revoke all refresh tokens for the authenticated user. "
            "Useful for logging out from all devices after a security incident."
        ),
    )
    def post(self):
        """Revoke all refresh tokens for the authenticated user."""
        user = get_authenticated_user()

        if not user:
            return error_response(
                "User not found.",
                404,
            )

        try:
            RefreshToken.query.filter_by(
                user_id=user.id
            ).update(
                {
                    "revoked": True,
                }
            )

            db.session.commit()

            current_app.logger.info(
                "All refresh tokens revoked for user %s (%s).",
                user.id,
                user.username,
            )

            return {
                "message": (
                    "All tokens revoked successfully. "
                    "Please log in again from all devices."
                ),
            }, 200

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to revoke all refresh tokens for user %s.",
                user.id,
            )

            return error_response(
                "Failed to revoke tokens.",
                500,
            )


# ==========================================================
# Password Validation Utility
# ==========================================================

def validate_password_for_auth(password):
    """
    Validate password strength using the project's
    authentication security rules.
    """
    try:
        validate_password_strength(password)
        return True, None

    except PasswordValidationError as error:
        return False, str(error)


# ==========================================================
# Register Namespace
# ==========================================================

api.add_namespace(
    auth_ns,
    path="/auth",
)