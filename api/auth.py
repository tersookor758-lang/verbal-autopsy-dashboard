from datetime import datetime, timedelta
import hashlib
import secrets

from flask import request, current_app
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, Resource, fields

from api.api import api
from api.rbac import get_authenticated_user, role_required
from api.auth_security import (
    validate_password_strength,
    PasswordValidationError,
    log_failed_login,
    log_successful_login,
    log_logout,
    log_token_refresh,
    log_revoked_token_reuse
)
from extensions import db, limiter
from models import RefreshToken, User


auth_ns = Namespace(
    "auth",
    description="Authentication and authorization operations",
)

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

ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME = timedelta(days=30)


def error_response(message, status_code):
    return {"message": message}, status_code


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }


def hash_refresh_token(token):
    """Hash a refresh token before storing or querying it."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_refresh_token(user_id):
    """Generate a refresh token and store only its hash."""
    raw_token = secrets.token_urlsafe(64)

    db.session.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.utcnow() + REFRESH_TOKEN_LIFETIME,
        )
    )

    return raw_token


def create_user_access_token(user):
    return create_access_token(
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role,
        },
        expires_delta=ACCESS_TOKEN_LIFETIME,
    )


def token_response(message, user, include_user=False):
    access_token = create_user_access_token(user)
    refresh_token = create_refresh_token(user.id)

    response = {
        "message": message,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": int(ACCESS_TOKEN_LIFETIME.total_seconds()),
    }

    if include_user:
        response["user"] = user_to_dict(user)

    return response


def get_refresh_token(raw_token):
    token_hash = hash_refresh_token(raw_token)
    return RefreshToken.query.filter_by(token_hash=token_hash).first()


@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_request_model, validate=False)
    @auth_ns.response(200, "Login successful.", login_response_model)
    @auth_ns.response(400, "Username and password are required.", message_response_model)
    @auth_ns.response(401, "Invalid username or password.", message_response_model)
    @auth_ns.response(429, "Too many login attempts. Please try again later.", message_response_model)
    @limiter.limit("5 per minute")
    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")
        ip_address = request.remote_addr

        if not username or not password:
            return error_response("Username and password are required.", 400)

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            # Log failed attempt
            log_failed_login(username, ip_address, "Invalid credentials")
            return error_response("Invalid username or password.", 401)

        # Successful login
        response = token_response("Login successful.", user, include_user=True)
        
        # Log successful login
        log_successful_login(username, ip_address, user.id)

        return response, 200


@auth_ns.route("/refresh")
class Refresh(Resource):
    @auth_ns.expect(refresh_request_model, validate=False)
    @auth_ns.response(200, "Token refreshed successfully.", token_response_model)
    @auth_ns.response(400, "Refresh token is required.", message_response_model)
    @auth_ns.response(401, "Refresh token is invalid, revoked, expired, or orphaned.", message_response_model)
    def post(self):
        data = request.get_json(silent=True) or {}
        raw_token = data.get("refresh_token", "").strip()
        ip_address = request.remote_addr

        if not raw_token:
            return error_response("Refresh token is required.", 400)

        refresh_token = get_refresh_token(raw_token)

        if not refresh_token:
            return error_response("Invalid refresh token.", 401)

        user = User.query.get(refresh_token.user_id)

        if not user:
            refresh_token.revoked = True
            db.session.commit()
            log_token_refresh(
                "unknown",
                refresh_token.user_id,
                success=False,
                reason="User not found"
            )
            return error_response("User associated with token was not found.", 401)

        if refresh_token.revoked:
            # Log attempt to reuse revoked token
            log_revoked_token_reuse(user.username, user.id, ip_address, "refresh")
            log_token_refresh(
                user.username,
                user.id,
                success=False,
                reason="Token already revoked"
            )
            return error_response("Refresh token has been revoked.", 401)

        if refresh_token.expires_at <= datetime.utcnow():
            refresh_token.revoked = True
            db.session.commit()
            log_token_refresh(
                user.username,
                user.id,
                success=False,
                reason="Token expired"
            )
            return error_response("Refresh token has expired.", 401)

        # Revoke old token and generate new one
        refresh_token.revoked = True
        response = token_response("Token refreshed successfully.", user)

        db.session.commit()

        # Log successful refresh
        log_token_refresh(user.username, user.id, success=True)

        return response, 200


@auth_ns.route("/logout")
class Logout(Resource):
    @auth_ns.expect(logout_request_model, validate=False)
    @auth_ns.response(200, "Logout successful.", message_response_model)
    @auth_ns.response(400, "Refresh token is required.", message_response_model)
    @auth_ns.response(401, "Invalid refresh token.", message_response_model)
    def post(self):
        data = request.get_json(silent=True) or {}
        raw_token = data.get("refresh_token", "").strip()
        ip_address = request.remote_addr

        if not raw_token:
            return error_response("Refresh token is required.", 400)

        refresh_token = get_refresh_token(raw_token)

        if not refresh_token:
            return error_response("Invalid refresh token.", 401)

        user = User.query.get(refresh_token.user_id)
        username = user.username if user else "unknown"

        refresh_token.revoked = True
        db.session.commit()

        # Log logout
        if user:
            log_logout(username, user.id, ip_address)

        return {"message": "Logout successful."}, 200


@auth_ns.route("/me")
class CurrentUser(Resource):
    @role_required("Administrator", "Editor", "Viewer")
    @auth_ns.response(200, "Current authenticated user.", auth_user_model)
    @auth_ns.response(401, "Missing or invalid Authorization header.", message_response_model)
    @auth_ns.response(403, "Forbidden.", message_response_model)
    @auth_ns.response(404, "User not found.", message_response_model)
    def get(self):
        user = get_authenticated_user()

        if not user:
            return error_response("User not found.", 404)

        return user_to_dict(user), 200


@auth_ns.route("/revoke-all")
class RevokeAllTokens(Resource):
    @role_required("Administrator", "Editor", "Viewer")
    @auth_ns.response(200, "All tokens revoked successfully.", message_response_model)
    @auth_ns.response(401, "Missing or invalid Authorization header.", message_response_model)
    @auth_ns.response(403, "Forbidden.", message_response_model)
    @auth_ns.response(404, "User not found.", message_response_model)
    @auth_ns.doc(
        description="Revoke all refresh tokens for the authenticated user. "
                    "Useful for logging out from all devices after a security incident."
    )
    def post(self):
        """Revoke all refresh tokens for the authenticated user."""
        user = get_authenticated_user()

        if not user:
            return error_response("User not found.", 404)

        # Revoke all refresh tokens for this user
        try:
            RefreshToken.query.filter_by(user_id=user.id).update({"revoked": True})
            db.session.commit()
            
            current_app.logger.info(
                f"All refresh tokens revoked for user {user.id} ({user.username})"
            )
            
            return {
                "message": "All tokens revoked successfully. Please log in again from all devices."
            }, 200
        except Exception as error:
            db.session.rollback()
            current_app.logger.exception(error)
            return error_response("Failed to revoke tokens.", 500)


api.add_namespace(auth_ns, path="/auth")
