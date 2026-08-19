"""
Application configuration.

Supports:
- Local development with XAMPP/MySQL
- Production deployment
- Environment-based secrets
- Secure session configuration
- File upload configuration
"""

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
    # APPLICATION ENVIRONMENT
    # ==========================================================

    ENVIRONMENT = os.environ.get(
        "APP_ENV",
        os.environ.get(
            "FLASK_ENV",
            "development",
        ),
    ).lower()

    IS_PRODUCTION = ENVIRONMENT == "production"

    DEBUG = not IS_PRODUCTION

    TESTING = False


    # ==========================================================
    # SECURITY
    # ==========================================================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY"
    )

    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY"
    )

    # These values are allowed only during local development.
    # Production must provide real secrets through environment
    # variables.
    if not SECRET_KEY and not IS_PRODUCTION:
        SECRET_KEY = (
            "development-only-secret-"
            "change-this-before-production"
        )

    if not JWT_SECRET_KEY and not IS_PRODUCTION:
        JWT_SECRET_KEY = (
            "development-only-jwt-secret-"
            "change-this-before-production"
        )


    # ==========================================================
    # JWT
    # ==========================================================

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

    DATABASE_URL = os.environ.get(
        "DATABASE_URL"
    )

    USE_MYSQL = (
        os.environ.get(
            "USE_MYSQL",
            "false",
        ).lower()
        == "true"
    )

    SQLITE_DATABASE_PATH = os.path.join(
        BASE_DIR,
        "verbal_autopsy.db",
    )

    if USE_MYSQL and DATABASE_URL:

        DATABASE_URI = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1,
        )

    else:

        DATABASE_URI = (
            "sqlite:///"
            + SQLITE_DATABASE_PATH
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }


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
        "uploads",
    )

    MAX_CONTENT_LENGTH = (
        50 * 1024 * 1024
    )

    ALLOWED_UPLOAD_EXTENSIONS = {
        "csv",
        "xlsx",
        "xls",
        "json",
    }


    # ==========================================================
    # RATE LIMITING
    # ==========================================================
    #
    # Development:
    #     Uses Flask-Limiter's in-memory storage.
    #
    # Production:
    #     RATE_LIMIT_STORAGE_URI must be supplied.
    #
    # Example:
    #
    # RATE_LIMIT_STORAGE_URI=redis://localhost:6379/0
    #
    # or a managed Redis URL supplied by the hosting provider.
    # ==========================================================

    RATE_LIMIT_STORAGE_URI = os.environ.get(
        "RATE_LIMIT_STORAGE_URI"
    )


    # ==========================================================
    # CORS
    # ==========================================================

    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "",
    )

    if CORS_ORIGINS:
        CORS_ORIGINS = [
            origin.strip()
            for origin in CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    else:
        CORS_ORIGINS = "*"


    # ==========================================================
    # VALIDATE PRODUCTION CONFIGURATION
    # ==========================================================

    @classmethod
    def validate(cls):
        """
        Validate configuration required for production.
        """

        if not cls.IS_PRODUCTION:
            return

        if not cls.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY must be set in production."
            )

        if not cls.JWT_SECRET_KEY:
            raise RuntimeError(
                "JWT_SECRET_KEY must be set in production."
            )

        if cls.SECRET_KEY.startswith(
            "development-only-secret-"
        ):
            raise RuntimeError(
                "A real SECRET_KEY must be configured in production."
            )

        if cls.JWT_SECRET_KEY.startswith(
            "development-only-jwt-secret-"
        ):
            raise RuntimeError(
                "A real JWT_SECRET_KEY must be configured in production."
            )

        if not cls.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL must be set in production."
            )

        if not cls.USE_MYSQL:
            raise RuntimeError(
                "USE_MYSQL=true must be set in production."
            )

        if not cls.RATE_LIMIT_STORAGE_URI:
            raise RuntimeError(
                "RATE_LIMIT_STORAGE_URI must be set in production."
            )