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
    template_folder="../templates"
)