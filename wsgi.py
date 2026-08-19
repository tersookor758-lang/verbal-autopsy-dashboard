"""
Production WSGI entry point.

Deployment servers such as Gunicorn use this module
to load the Flask application.
"""

from app import app


__all__ = ["app"]