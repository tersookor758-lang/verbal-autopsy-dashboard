"""
Production database initialization and connection check.

Production schema changes are managed through Flask-Migrate/Alembic.
This script verifies that the configured production database is reachable.

It deliberately does not call db.create_all() in production.
"""

from sqlalchemy import text

from app import app
from config import Config
from extensions import db


def initialize_database():
    """
    Verify that the configured production database is reachable.
    """

    if not Config.IS_PRODUCTION:
        raise RuntimeError(
            "init_db.py is intended for production use only. "
            "Set APP_ENV=production before running it."
        )

    print("=" * 70)
    print("VERBAL AUTOPSY OUTCOME DASHBOARD")
    print("PRODUCTION DATABASE CHECK")
    print("=" * 70)

    print()
    print("Environment: production")
    print("Database: MySQL")
    print()

    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            db.session.rollback()

        print("Production database connection: OK")
        print()
        print("Schema management: Flask-Migrate/Alembic")
        print()
        print("Database check completed successfully.")
        print("=" * 70)

        return True

    except Exception as error:
        print()
        print("DATABASE CHECK FAILED")
        print()
        print(f"Error: {error}")
        print("=" * 70)

        return False


if __name__ == "__main__":
    success = initialize_database()

    if not success:
        raise SystemExit(1)
