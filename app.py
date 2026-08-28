"""
Application entry point for the Verbal Autopsy Outcome Dashboard.
"""

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from config import Config
from extensions import db, migrate, login_manager, jwt, limiter
from models import User
from dashboard import dashboard_bp
from api import api_bp
from auth import auth_bp
from admin import admin_bp


def validate_security_config(app):
    """Validate required security configuration."""

    Config.validate()

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be configured.")

    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError("JWT_SECRET_KEY must be configured.")


def create_default_admin():
    """Create a development administrator account if no users exist."""

    if Config.IS_PRODUCTION:
        return

    if User.query.count() == 0:
        admin = User(
            username="admin",
            email="admin@example.com",
            role="admin",
            is_verified=True,
            is_active=True,
        )

        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        print("=" * 60)
        print("DEFAULT ADMIN ACCOUNT CREATED")
        print("Username : admin")
        print("Password : admin123")
        print("Role     : admin")
        print("Active   : True")
        print("=" * 60)
        print("IMPORTANT: This account is for development only.")
        print("=" * 60)


def create_app():
    """Application factory."""

    app = Flask(__name__)

    app.config.from_object(Config)

    validate_security_config(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)

    limiter_kwargs = {}

    if Config.RATE_LIMIT_STORAGE_URI:
        limiter_kwargs["storage_uri"] = Config.RATE_LIMIT_STORAGE_URI

    limiter.init_app(app, **limiter_kwargs)

    CORS(
        app,
        origins=Config.CORS_ORIGINS,
    )

    # Import route modules so their routes are attached to
    # the already-created blueprints before registration.
    import dashboard.routes
    import auth.routes
    import api.api
    import api.auth
    import api.routes
    import admin.routes

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/health", methods=["GET"])
    def health_check():
        """Return application and database health status."""

        try:
            db.session.execute(text("SELECT 1"))

            return jsonify(
                {
                    "status": "healthy",
                    "application": "Verbal Autopsy Outcome Dashboard",
                    "database": "connected",
                }
            ), 200

        except Exception:
            db.session.rollback()

            return jsonify(
                {
                    "status": "unhealthy",
                    "application": "Verbal Autopsy Outcome Dashboard",
                    "database": "unavailable",
                }
            ), 503

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