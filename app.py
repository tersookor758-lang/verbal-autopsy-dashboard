from flask import Flask

from config import Config
from extensions import db

# Import models so SQLAlchemy knows about them
# before db.create_all() is executed.
from models import VerbalAutopsy

# Blueprints
from dashboard import dashboard_bp
from api import api_bp


def create_app():
    """
    Application factory.

    Creates and configures the Flask application,
    initializes extensions, registers blueprints,
    and creates database tables.
    """

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    # Import routes after extensions are initialized
    import dashboard.routes
    import api.api
    import api.routes

    # Register blueprints
    app.register_blueprint(dashboard_bp)

    app.register_blueprint(
        api_bp,
        url_prefix="/api"
    )

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )