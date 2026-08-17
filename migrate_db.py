"""
Database migration script.

Adds the authentication and security columns required by
the current User model without deleting existing data.
"""

from pathlib import Path
import sqlite3


# ==========================================================
# Database Location
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "verbal_autopsy.db"


# ==========================================================
# Migration
# ==========================================================

def migrate_database():

    print("=" * 60)
    print("VERBAL AUTOPSY DATABASE MIGRATION")
    print("=" * 60)

    print()
    print(f"Database: {DATABASE_PATH}")

    if not DATABASE_PATH.exists():

        print()
        print("ERROR: Database file was not found.")

        return False

    connection = None

    try:

        connection = sqlite3.connect(
            DATABASE_PATH
        )

        cursor = connection.cursor()

        # --------------------------------------------------
        # Get existing columns
        # --------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(users)"
        )

        existing_columns = {
            row[1]
            for row in cursor.fetchall()
        }

        print()
        print("Checking users table...")

        # --------------------------------------------------
        # is_verified
        # --------------------------------------------------

        if "is_verified" not in existing_columns:

            print(
                "Adding column: is_verified"
            )

            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN is_verified
                BOOLEAN DEFAULT 0
                """
            )

            print(
                "✓ is_verified added."
            )

        else:

            print(
                "✓ is_verified already exists."
            )

        # --------------------------------------------------
        # is_active
        # --------------------------------------------------

        if "is_active" not in existing_columns:

            print(
                "Adding column: is_active"
            )

            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN is_active
                BOOLEAN DEFAULT 1
                """
            )

            print(
                "✓ is_active added."
            )

        else:

            print(
                "✓ is_active already exists."
            )

        # --------------------------------------------------
        # last_login_at
        # --------------------------------------------------

        if "last_login_at" not in existing_columns:

            print(
                "Adding column: last_login_at"
            )

            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN last_login_at
                DATETIME
                """
            )

            print(
                "✓ last_login_at added."
            )

        else:

            print(
                "✓ last_login_at already exists."
            )

        # --------------------------------------------------
        # failed_login_attempts
        # --------------------------------------------------

        if "failed_login_attempts" not in existing_columns:

            print(
                "Adding column: failed_login_attempts"
            )

            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN failed_login_attempts
                INTEGER DEFAULT 0
                """
            )

            print(
                "✓ failed_login_attempts added."
            )

        else:

            print(
                "✓ failed_login_attempts already exists."
            )

        # --------------------------------------------------
        # last_failed_login_at
        # --------------------------------------------------

        if "last_failed_login_at" not in existing_columns:

            print(
                "Adding column: last_failed_login_at"
            )

            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN last_failed_login_at
                DATETIME
                """
            )

            print(
                "✓ last_failed_login_at added."
            )

        else:

            print(
                "✓ last_failed_login_at already exists."
            )

        # --------------------------------------------------
        # Existing accounts
        # --------------------------------------------------
        #
        # Existing users remain active.
        #
        # They are NOT automatically verified because
        # verification is supposed to be controlled by
        # the administrator.
        #
        # --------------------------------------------------

        if "is_active" not in existing_columns:

            cursor.execute(
                """
                UPDATE users
                SET is_active = 1
                WHERE is_active IS NULL
                """
            )

        # --------------------------------------------------
        # Save changes
        # --------------------------------------------------

        connection.commit()

        print()
        print("=" * 60)
        print("DATABASE MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)

        return True

    except Exception as error:

        if connection:

            connection.rollback()

        print()
        print("=" * 60)
        print("DATABASE MIGRATION FAILED")
        print("=" * 60)

        print()
        print(f"Error: {error}")

        return False

    finally:

        if connection:

            connection.close()


# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":

    success = migrate_database()

    if not success:

        raise SystemExit(1)