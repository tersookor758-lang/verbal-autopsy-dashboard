"""
Database migration script to add new columns for security hardening.

This script adds the required columns to the users table for tracking
login attempts without breaking existing data.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import text, inspect

load_dotenv()

from app import app, db


def add_column_if_not_exists(connection, table_name, column_name, column_definition):
    """
    Add a column to a table if it doesn't already exist.
    
    Args:
        connection: SQLAlchemy connection object
        table_name: Name of the table
        column_name: Name of the column to add
        column_definition: SQL definition of the column (e.g., "DATETIME NULL DEFAULT NULL")
    """
    inspector = inspect(connection)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    
    if column_name not in columns:
        print(f"Adding column '{column_name}' to table '{table_name}'...")
        try:
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            connection.execute(text(alter_sql))
            connection.commit()
            print(f"✓ Successfully added column '{column_name}'")
            return True
        except Exception as e:
            print(f"✗ Error adding column '{column_name}': {e}")
            return False
    else:
        print(f"✓ Column '{column_name}' already exists, skipping...")
        return True


def migrate_database():
    """Apply database migrations to add new security tracking columns."""
    
    print("=" * 60)
    print("Database Migration: Add Security Hardening Columns")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Get a connection to the database
            connection = db.engine.connect()
            
            print("\nAdding new columns to 'users' table...")
            
            # Add login tracking columns
            add_column_if_not_exists(
                connection,
                "users",
                "last_login_at",
                "DATETIME NULL DEFAULT NULL"
            )
            
            add_column_if_not_exists(
                connection,
                "users",
                "failed_login_attempts",
                "INTEGER DEFAULT 0"
            )
            
            add_column_if_not_exists(
                connection,
                "users",
                "last_failed_login_at",
                "DATETIME NULL DEFAULT NULL"
            )
            
            connection.close()
            
            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            print("=" * 60)
            return False


if __name__ == "__main__":
    success = migrate_database()
    exit(0 if success else 1)
