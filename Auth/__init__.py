from flask import Blueprint


def create_auth_blueprint():
    auth_bp = Blueprint(
        "auth",
        __name__,
        template_folder="../templates",
    )

    from .routes import register_auth_routes

    register_auth_routes(auth_bp)

    return auth_bp