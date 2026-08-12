from datetime import datetime, timedelta
import hashlib
import secrets

from flask import request
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, Resource, fields

from api.api import api
from api.rbac import get_authenticated_user, role_required
from extensions import db
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
    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return error_response("Username and password are required.", 400)

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return error_response("Invalid username or password.", 401)

        response = token_response("Login successful.", user, include_user=True)
        db.session.commit()

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

        if not raw_token:
            return error_response("Refresh token is required.", 400)

        refresh_token = get_refresh_token(raw_token)

        if not refresh_token:
            return error_response("Invalid refresh token.", 401)

        if refresh_token.revoked:
            return error_response("Refresh token has been revoked.", 401)

        if refresh_token.expires_at <= datetime.utcnow():
            refresh_token.revoked = True
            db.session.commit()
            return error_response("Refresh token has expired.", 401)

        user = User.query.get(refresh_token.user_id)

        if not user:
            refresh_token.revoked = True
            db.session.commit()
            return error_response("User associated with token was not found.", 401)

        refresh_token.revoked = True
        response = token_response("Token refreshed successfully.", user)

        db.session.commit()

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

        if not raw_token:
            return error_response("Refresh token is required.", 400)

        refresh_token = get_refresh_token(raw_token)

        if not refresh_token:
            return error_response("Invalid refresh token.", 401)

        refresh_token.revoked = True
        db.session.commit()

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


api.add_namespace(auth_ns, path="/auth")
