"""
Application configuration.

Supports:
- Local development with SQLite/MySQL
- Production deployment with MySQL
- Environment-based secrets
- Secure session configuration
- File upload configuration
- Persistent rate limiting
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
    ).strip().lower()

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

    # Development-only fallback secrets.
    #
    # These are deliberately unavailable in production.
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
        ).strip().lower()
        == "true"
    )

    SQLITE_DATABASE_PATH = os.path.join(
        BASE_DIR,
        "verbal_autopsy.db",
    )

    # ----------------------------------------------------------
    # Database URI selection
    # ----------------------------------------------------------

    if USE_MYSQL:

        if not DATABASE_URL:
            DATABASE_URI = None

        else:

            DATABASE_URI = DATABASE_URL.strip()

            # Normalize common MySQL URL formats.
            if DATABASE_URI.startswith(
                "mysql://"
            ):
                DATABASE_URI = DATABASE_URI.replace(
                    "mysql://",
                    "mysql+pymysql://",
                    1,
                )

            elif DATABASE_URI.startswith(
                "mysql+pymysql://"
            ):
                pass

            else:
                DATABASE_URI = DATABASE_URI

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

    RATE_LIMIT_STORAGE_URI = os.environ.get(
        "RATE_LIMIT_STORAGE_URI"
    )


    # ==========================================================
    # CORS
    # ==========================================================

    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "",
    ).strip()

    if CORS_ORIGINS:

        CORS_ORIGINS = [
            origin.strip()
            for origin in CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    else:

        # Wildcard CORS is acceptable for local development,
        # but production must explicitly define allowed origins.
        CORS_ORIGINS = "*"


    # ==========================================================
    # PRODUCTION VALIDATION
    # ==========================================================

    @classmethod
    def validate(cls):
        """
        Validate configuration required for production.
        """

        if not cls.IS_PRODUCTION:
            return


        # ------------------------------------------------------
        # Application secrets
        # ------------------------------------------------------

        if not cls.SECRET_KEY:

            raise RuntimeError(
                "SECRET_KEY must be set in production."
            )

        if cls.SECRET_KEY.startswith(
            "development-only-secret-"
        ):

            raise RuntimeError(
                "A real SECRET_KEY must be configured "
                "in production."
            )


        if not cls.JWT_SECRET_KEY:

            raise RuntimeError(
                "JWT_SECRET_KEY must be set in production."
            )

        if cls.JWT_SECRET_KEY.startswith(
            "development-only-jwt-secret-"
        ):

            raise RuntimeError(
                "A real JWT_SECRET_KEY must be configured "
                "in production."
            )


        # ------------------------------------------------------
        # Database
        # ------------------------------------------------------

        if not cls.DATABASE_URL:

            raise RuntimeError(
                "DATABASE_URL must be set in production."
            )

        if not cls.USE_MYSQL:

            raise RuntimeError(
                "USE_MYSQL=true must be set in production."
            )

        if not cls.SQLALCHEMY_DATABASE_URI:

            raise RuntimeError(
                "A valid production database URI "
                "must be configured."
            )


        # ------------------------------------------------------
        # Rate limiting
        # ------------------------------------------------------

        if not cls.RATE_LIMIT_STORAGE_URI:

            raise RuntimeError(
                "RATE_LIMIT_STORAGE_URI must be set "
                "in production."
            )


        # ------------------------------------------------------
        # CORS
        # ------------------------------------------------------

        if cls.CORS_ORIGINS == "*":

            raise RuntimeError(
                "CORS_ORIGINS must explicitly specify "
                "allowed production origins."
            )