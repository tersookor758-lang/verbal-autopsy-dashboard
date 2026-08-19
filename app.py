"""
Application entry point for the Verbal Autopsy Outcome Dashboard.
"""

from dotenv import load_dotenv

load_dotenv()


from flask import (
    Flask,
    jsonify,
)

from flask_cors import CORS
from sqlalchemy import text

from config import Config

from extensions import (
    db,
    migrate,
    login_manager,
    jwt,
    limiter,
)

from models import (
    User,
    VerbalAutopsy,
    RefreshToken,
)

from dashboard import dashboard_bp
from api import api_bp
from auth import auth_bp
from admin import admin_bp


# ==========================================================
# Security Configuration
# ==========================================================

def validate_security_config(app):
    """
    Validate security configuration.
    """

    Config.validate()

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY must be configured."
        )

    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError(
            "JWT_SECRET_KEY must be configured."
        )


# ==========================================================
# Default Administrator
# ==========================================================

def create_default_admin():
    """
    Create the development administrator account.

    This function is intentionally disabled in production.
    """

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

        admin.set_password(
            "admin123"
        )

        db.session.add(
            admin
        )

        db.session.commit()

        print("=" * 60)
        print("DEFAULT ADMIN ACCOUNT CREATED")
        print("Username : admin")
        print("Password : admin123")
        print("Role     : admin")
        print("Active   : True")
        print("=" * 60)
        print(
            "IMPORTANT: This account is for development only."
        )
        print("=" * 60)


# ==========================================================
# Application Factory
# ==========================================================

def create_app():
    """
    Application factory.
    """

    app = Flask(
        __name__
    )

    # ------------------------------------------------------
    # Configuration
    # ------------------------------------------------------

    app.config.from_object(
        Config
    )

    # ------------------------------------------------------
    # Security Validation
    # ------------------------------------------------------

    validate_security_config(
        app
    )

    # ------------------------------------------------------
    # Initialize Extensions
    # ------------------------------------------------------

    db.init_app(
        app
    )

    migrate.init_app(
        app,
        db,
    )

    login_manager.init_app(
        app
    )

    jwt.init_app(
        app
    )

    # ------------------------------------------------------
    # Flask-Limiter
    #
    # Development:
    #     In-memory storage is allowed.
    #
    # Production:
    #     RATE_LIMIT_STORAGE_URI must be configured.
    # ------------------------------------------------------

    limiter_kwargs = {}

    if Config.RATE_LIMIT_STORAGE_URI:

        limiter_kwargs[
            "storage_uri"
        ] = Config.RATE_LIMIT_STORAGE_URI

    limiter.init_app(
        app,
        **limiter_kwargs
    )

    # ------------------------------------------------------
    # CORS
    # ------------------------------------------------------

    CORS(
        app,
        origins=Config.CORS_ORIGINS,
    )

    # ------------------------------------------------------
    # Import Route Modules
    # ------------------------------------------------------

    import dashboard.routes
    import auth.routes
    import api.api
    import api.auth
    import api.routes
    import admin.routes

    # ------------------------------------------------------
    # Register Dashboard Blueprint
    # ------------------------------------------------------

    app.register_blueprint(
        dashboard_bp
    )

    # ------------------------------------------------------
    # Register Authentication Blueprint
    # ------------------------------------------------------

    app.register_blueprint(
        auth_bp
    )

    # ------------------------------------------------------
    # Register API Blueprint
    # ------------------------------------------------------

    app.register_blueprint(
        api_bp,
        url_prefix="/api",
    )

    # ------------------------------------------------------
    # Register Admin Blueprint
    # ------------------------------------------------------

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin",
    )

    # ------------------------------------------------------
    # Health Check
    # ------------------------------------------------------
    #
    # Used by deployment platforms and monitoring systems.
    #
    # The database is checked as well, so a successful response
    # means both Flask and the database connection are working.
    # ------------------------------------------------------

    @app.route(
        "/health",
        methods=["GET"],
    )
    def health_check():
        """
        Return application and database health status.
        """

        try:

            db.session.execute(
                text("SELECT 1")
            )

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

    # ------------------------------------------------------
    # Database Initialization
    # ------------------------------------------------------
    #
    # Development only.
    #
    # Production schema changes are handled by Flask-Migrate.
    # ------------------------------------------------------

    with app.app_context():

        if not Config.IS_PRODUCTION:

            db.create_all()

            create_default_admin()

    return app


# ==========================================================
# Application Instance
# ==========================================================

app = create_app()


# ==========================================================
# Development Entry Point
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=Config.DEBUG,
    )