"""
Application extensions.

All Flask extensions are initialized here to avoid
circular imports across the application.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


# ==========================================================
# Database
# ==========================================================

db = SQLAlchemy()


# ==========================================================
# Login Manager
# ==========================================================

login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.login_message = (
    "Please log in to access this page."
)

login_manager.login_message_category = "warning"


# ==========================================================
# User Loader
# ==========================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Reload the user object from the session.
    """

    from models import User

    return User.query.get(int(user_id))