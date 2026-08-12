import os


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

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        os.urandom(24)
    )


    # -----------------------------
    # JWT Authentication
    # -----------------------------

    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "change-this-jwt-secret-in-production"
    )

    JWT_TOKEN_LOCATION = ["headers"]

    JWT_HEADER_NAME = "Authorization"

    JWT_HEADER_TYPE = "Bearer"


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
    # JSON
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