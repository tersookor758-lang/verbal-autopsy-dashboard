from datetime import datetime, timedelta
import hashlib
import secrets

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from extensions import db
from models import User, RefreshToken

from api.api import api


# ==========================================================
# Namespace
# ==========================================================

auth_ns = Namespace(
    "auth",
    description="Authentication and authorization operations"
)


# ==========================================================
# Helper: Hash Refresh Token
# ==========================================================

def hash_refresh_token(token):
    """
    Create a SHA-256 hash of a refresh token.

    The raw refresh token is never stored in the database.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ==========================================================
# LOGIN
# ==========================================================

@auth_ns.route("/login")
class Login(Resource):

    def post(self):

        data = request.get_json(
            silent=True
        ) or {}

        username = data.get(
            "username",
            ""
        ).strip()

        password = data.get(
            "password",
            ""
        )

        if not username or not password:

            return {
                "message": "Username and password are required."
            }, 400


        user = User.query.filter_by(
            username=username
        ).first()


        if not user or not user.check_password(password):

            return {
                "message": "Invalid username or password."
            }, 401


        # --------------------------------------------------
        # Create short-lived access token
        # --------------------------------------------------

        access_token = create_access_token(

            identity=str(user.id),

            additional_claims={
                "username": user.username,
                "role": user.role
            },

            expires_delta=timedelta(
                minutes=15
            )

        )


        # --------------------------------------------------
        # Create secure refresh token
        # --------------------------------------------------

        raw_refresh_token = secrets.token_urlsafe(
            64
        )


        refresh_token_hash = hash_refresh_token(
            raw_refresh_token
        )


        refresh_token = RefreshToken(

            user_id=user.id,

            token_hash=refresh_token_hash,

            expires_at=datetime.utcnow()
            + timedelta(days=30)

        )


        db.session.add(
            refresh_token
        )

        db.session.commit()


        return {

            "message": "Login successful.",

            "access_token": access_token,

            "refresh_token": raw_refresh_token,

            "token_type": "Bearer",

            "expires_in": 900,

            "user": {

                "id": user.id,

                "username": user.username,

                "email": user.email,

                "role": user.role

            }

        }, 200


# ==========================================================
# CURRENT USER
# ==========================================================

@auth_ns.route("/me")
class CurrentUser(Resource):

    @jwt_required()
    def get(self):

        user_id = get_jwt_identity()


        user = User.query.get(
            int(user_id)
        )


        if not user:

            return {
                "message": "User not found."
            }, 404


        return {

            "id": user.id,

            "username": user.username,

            "email": user.email,

            "role": user.role

        }, 200


# ==========================================================
# REGISTER AUTH NAMESPACE
# ==========================================================

api.add_namespace(
    auth_ns,
    path="/auth"
)