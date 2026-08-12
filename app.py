from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, login_manager, jwt

# Import models so SQLAlchemy knows about them
from models import User, VerbalAutopsy

# Blueprints
from dashboard import dashboard_bp
from api import api_bp
from auth import auth_bp



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


def create_default_admin():
    """
    Creates the default administrator account
    if there are no users in the database.
    """

    if User.query.count() == 0:

        admin = User(
            username="admin",
            email="admin@example.com",
            role="Administrator"
        )

        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        print("=" * 60)
        print("DEFAULT ADMIN ACCOUNT CREATED")
        print("Username : admin")
        print("Password : admin123")
        print("=" * 60)


def create_app():
    """
    Application factory.

    Creates and configures the Flask application,
    initializes extensions,
    registers blueprints,
    and creates database tables.
    """

    app = Flask(__name__)

    app.config.from_object(Config)

    validate_security_config(app)

    # ------------------------------------------
    # Initialize Extensions
    # ------------------------------------------

    db.init_app(app)

    login_manager.init_app(app)

    jwt.init_app(app)

    # ------------------------------------------
    # Import Routes
    # ------------------------------------------

    import dashboard.routes
    import api.api
    import api.auth
    import api.routes
    import auth.routes

    # ------------------------------------------
    # Register Blueprints
    # ------------------------------------------

    app.register_blueprint(dashboard_bp)

    app.register_blueprint(auth_bp)

    app.register_blueprint(
        api_bp,
        url_prefix="/api"
    )

    # ------------------------------------------
    # Create Database Tables
    # ------------------------------------------

    with app.app_context():

        db.create_all()

        create_default_admin()

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )
