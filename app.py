from flask import Flask

from config import Config
from extensions import db, login_manager

# Import models so SQLAlchemy knows about them
# before db.create_all() is executed.
from models import User, VerbalAutopsy

# Blueprints
from dashboard import dashboard_bp
from api import api_bp
from auth import auth_bp


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

    # Dashboard
    app.register_blueprint(
        dashboard_bp
    )

    # Authentication
    app.register_blueprint(
        auth_bp
    )

    # REST API
    app.register_blueprint(
        api_bp,
        url_prefix="/api"
    )

    # ------------------------------------------
    # Create Database Tables
    # ------------------------------------------

    with app.app_context():

        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )