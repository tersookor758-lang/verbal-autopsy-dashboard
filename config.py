import os
from datetime import timedelta


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


class Config:
    """
    Base configuration for the
    Verbal Autopsy Outcome Dashboard.
    """

    # -----------------------------
    # Flask
    # -----------------------------

    ENVIRONMENT = os.environ.get(
        "FLASK_ENV",
        os.environ.get("APP_ENV", "development")
    ).lower()

    IS_PRODUCTION = ENVIRONMENT == "production"

    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY and not IS_PRODUCTION:

        SECRET_KEY = "dev-only-session-secret-change-me"


    # -----------------------------
    # JWT Authentication
    # -----------------------------

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    JWT_TOKEN_LOCATION = ["headers"]

    JWT_HEADER_NAME = "Authorization"

    JWT_HEADER_TYPE = "Bearer"

    JWT_ALGORITHM = "HS256"


    # -----------------------------
    # Database
    # -----------------------------

    DATABASE_URL = os.environ.get(
        "DATABASE_URL"
    )

    if DATABASE_URL:

        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )


    SQLALCHEMY_DATABASE_URI = (
        DATABASE_URL
        or "mysql+pymysql://tersoo:tersoo2007@localhost:3306/verbal_autopsy"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = False


    # -----------------------------
    # Session Cookies (Security)
    # -----------------------------

    SESSION_COOKIE_SECURE = IS_PRODUCTION

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)


    # -----------------------------

    JSON_SORT_KEYS = False


    # -----------------------------
    # File Uploads
    # -----------------------------

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    # Maximum upload size: 50 MB

    ALLOWED_UPLOAD_EXTENSIONS = {

        "csv",
        "xlsx",
        "xls",
        "json"

    }
