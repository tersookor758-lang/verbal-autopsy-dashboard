"""
Authentication Blueprint

Handles:
- Login
- Logout
- User Authentication
"""

from flask import Blueprint


auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="../templates",
)


# Import authentication routes after creating the blueprint.
#
# This is required so that the @auth_bp.route(...) decorators
# in auth/routes.py are executed and the routes are registered.
from . import routes