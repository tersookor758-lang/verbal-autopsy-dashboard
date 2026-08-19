"""
Administrator Blueprint

Handles:
- Administrator dashboard
- User management
- Account activation/deactivation
- Role management
- User deletion
"""

from flask import Blueprint


admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
)