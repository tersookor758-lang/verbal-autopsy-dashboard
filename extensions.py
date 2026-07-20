"""
Application extensions.

All Flask extensions are initialized here to avoid
circular imports across the application.
"""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()