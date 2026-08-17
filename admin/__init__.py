"""
Administrator Blueprint

Handles:
- User management
- Account approval
- Account activation/deactivation
- Role management
"""

from flask import Blueprint


admin_bp = Blueprint(
    "admin",
    __name__,
)