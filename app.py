from flask import Flask

from config import Config
from extensions import db, login_manager, jwt

# Import models so SQLAlchemy knows about them
from models import User, VerbalAutopsy

# Blueprints
from dashboard import dashboard_bp
from api import api_bp
from auth import auth_bp


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