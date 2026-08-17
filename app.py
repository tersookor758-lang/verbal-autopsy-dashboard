from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_cors import CORS

from config import Config

from extensions import (
    db,
    login_manager,
    jwt,
    limiter,
)

# Import models so SQLAlchemy knows about them
from models import (
    User,
    VerbalAutopsy,
    RefreshToken,
)

# Blueprints
from dashboard import dashboard_bp
from api import api_bp
from auth import auth_bp
from admin import admin_bp


# ==========================================================
# Security Configuration
# ==========================================================

def validate_security_config(app):
    """
    Fail fast when required security configuration is missing.
    """

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY must be set when running in production."
        )

    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable must be set."
        )


# ==========================================================
# Default Administrator
# ==========================================================

def create_default_admin():
    """
    Create the default administrator account if the database
    does not contain any users.

    Default administrator:
        Username: admin
        Password: admin123

    The account is automatically verified because the initial
    administrator must be able to access the system.

    Change the default password immediately in a real
    deployment.
    """

    # Never create a default account in production.
    if Config.IS_PRODUCTION:
        return

    # Only create the default administrator when there are
    # no users in the database.
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
        print("Verified : True")
        print("=" * 60)


# ==========================================================
# Application Factory
# ==========================================================

def create_app():
    """
    Application factory.

    Creates and configures the Flask application,
    initializes extensions, imports route modules,
    registers blueprints, and creates database tables.
    """

    app = Flask(__name__)

    # ------------------------------------------------------
    # Application Configuration
    # ------------------------------------------------------

    app.config.from_object(Config)

    # ------------------------------------------------------
    # Validate Security Configuration
    # ------------------------------------------------------

    validate_security_config(app)

    # ------------------------------------------------------
    # Initialize Extensions
    # ------------------------------------------------------

    db.init_app(app)

    login_manager.init_app(app)

    jwt.init_app(app)

    limiter.init_app(app)

    CORS(app)

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
        url_prefix="/api"
    )

    # ------------------------------------------------------
    # Register Admin Blueprint
    # ------------------------------------------------------

    app.register_blueprint(
        admin_bp
    )

    # ------------------------------------------------------
    # Database Initialization
    # ------------------------------------------------------

    with app.app_context():

        db.create_all()

        create_default_admin()

    return app


# ==========================================================
# Create Application
# ==========================================================

app = create_app()


# ==========================================================
# Development Server
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )