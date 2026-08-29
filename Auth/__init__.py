"""
Authentication Blueprint

Handles:
- Login
- Logout
- User Registration
"""

from flask import Blueprint


auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="../templates",
)


# Import routes after creating the blueprint so the
# route decorators are executed.
from . import routes