"""
Application entry point for the Verbal Autopsy Outcome Dashboard.
"""

import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text

from config import Config
from extensions import (
    db,
    migrate,
    login_manager,
    jwt,
    limiter,
)
from models import User

from dashboard import dashboard_bp
from api import api_bp
from Auth import create_auth_blueprint
from admin import admin_bp


csrf = CSRFProtect()


def validate_security_config(app):
    Config.validate()

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY must be configured."
        )

    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError(
            "JWT_SECRET_KEY must be configured."
        )


def create_default_admin():
    """
    Create a development-only administrator account when explicitly
    configured through environment variables.

    Production environments never create a default administrator.
    The administrator password must never be hard-coded in source code.
    """
    if Config.IS_PRODUCTION:
        return

    if User.query.count() > 0:
        return

    admin_password = os.getenv("DEV_ADMIN_PASSWORD")

    if not admin_password:
        print(
            "No development admin created. "
            "Set DEV_ADMIN_PASSWORD in the environment "
            "if a local admin account is required."
        )
        return

    if len(admin_password) < 12:
        raise RuntimeError(
            "DEV_ADMIN_PASSWORD must contain at least "
            "12 characters."
        )

    admin_email = os.getenv(
        "DEV_ADMIN_EMAIL",
        "admin@localhost",
    )

    admin = User(
        username="admin",
        email=admin_email,
        role="admin",
        is_verified=True,
        is_active=True,
    )

    admin.set_password(
        admin_password,
        validate=True,
    )

    db.session.add(admin)
    db.session.commit()

    print("Development admin account created.")
    print("Username: admin")


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    validate_security_config(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)

    csrf.init_app(app)

    limiter_kwargs = {}

    if Config.RATE_LIMIT_STORAGE_URI:
        limiter_kwargs["storage_uri"] = (
            Config.RATE_LIMIT_STORAGE_URI
        )

    limiter.init_app(
        app,
        **limiter_kwargs,
    )

    CORS(
        app,
        origins=Config.CORS_ORIGINS,
    )

    import dashboard.routes
    import api.api
    import api.auth
    import api.routes
    import admin.routes

    auth_bp = create_auth_blueprint()

    csrf.exempt(api_bp)

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        api_bp,
        url_prefix="/api",
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin",
    )

    @app.route("/health")
    def health_check():
        try:
            db.session.execute(
                text("SELECT 1")
            )

            return jsonify({
                "status": "healthy",
                "application": (
                    "Verbal Autopsy "
                    "Outcome Dashboard"
                ),
                "database": "connected",
            }), 200

        except Exception:
            db.session.rollback()

            return jsonify({
                "status": "unhealthy",
                "application": (
                    "Verbal Autopsy "
                    "Outcome Dashboard"
                ),
                "database": "unavailable",
            }), 503

    with app.app_context():
        if not Config.IS_PRODUCTION:
            db.create_all()
            create_default_admin()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=Config.DEBUG,
    )
