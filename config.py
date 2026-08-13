import os
from datetime import timedelta


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


class Config:
    """
    Base configuration for the Verbal Autopsy Outcome Dashboard.
    """

    # ==========================================================
    # APPLICATION
    # ==========================================================

    ENVIRONMENT = os.environ.get(
        "FLASK_ENV",
        os.environ.get(
            "APP_ENV",
            "development"
        )
    ).lower()

    IS_PRODUCTION = ENVIRONMENT == "production"


    # ==========================================================
    # SECURITY
    # ==========================================================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY"
    )

    if not SECRET_KEY:
        SECRET_KEY = (
            "presentation-session-secret-"
            "change-before-production"
        )


    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY"
    )

    if not JWT_SECRET_KEY:
        JWT_SECRET_KEY = (
            "presentation-jwt-secret-"
            "change-before-production"
        )


    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=15
    )

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=30
    )

    JWT_TOKEN_LOCATION = [
        "headers"
    ]

    JWT_HEADER_NAME = "Authorization"

    JWT_HEADER_TYPE = "Bearer"

    JWT_ALGORITHM = "HS256"


    # ==========================================================
    # DATABASE
    # ==========================================================
    #
    # PRESENTATION MODE:
    #
    # The MySQL credentials currently in .env are rejected by
    # the MySQL Server 8.0 installation on this computer.
    #
    # Therefore, the bundled SQLite database is used for the
    # presentation so the dashboard can run immediately.
    #
    # The MySQL URL can still be supplied through DATABASE_URL
    # when the credentials are correct.
    #
    # Set USE_MYSQL=true when the MySQL account is working.
    # ==========================================================

    DATABASE_URL = os.environ.get(
        "DATABASE_URL"
    )

    USE_MYSQL = (
        os.environ.get(
            "USE_MYSQL",
            "false"
        ).lower()
        == "true"
    )


    SQLITE_DATABASE_PATH = os.path.join(
        BASE_DIR,
        "verbal_autopsy.db"
    )


    if USE_MYSQL and DATABASE_URL:

        DATABASE_URI = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )

    else:

        DATABASE_URI = (
            "sqlite:///"
            + SQLITE_DATABASE_PATH
        )


    SQLALCHEMY_DATABASE_URI = DATABASE_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = False


    # ==========================================================
    # SESSION SECURITY
    # ==========================================================

    SESSION_COOKIE_SECURE = IS_PRODUCTION

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=24
    )


    # ==========================================================
    # JSON
    # ==========================================================

    JSON_SORT_KEYS = False


    # ==========================================================
    # FILE UPLOADS
    # ==========================================================

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    MAX_CONTENT_LENGTH = (
        50 * 1024 * 1024
    )


    ALLOWED_UPLOAD_EXTENSIONS = {
        "csv",
        "xlsx",
        "xls",
        "json"
    }