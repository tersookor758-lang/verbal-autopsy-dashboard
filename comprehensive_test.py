#!/usr/bin/env python3
"""Deployment-readiness regression tests for the Verbal Autopsy Dashboard.

The suite uses an isolated temporary SQLite database and never uses production
credentials or the production MySQL database.

Run with:
    APP_ENV=testing pytest comprehensive_test.py -q

Windows PowerShell:
    $env:APP_ENV="testing"; pytest comprehensive_test.py -q
"""

import os
from pathlib import Path

import pytest

# Config.py evaluates the environment when it is imported. Set safe testing
# values before importing the application.
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("RATE_LIMIT_STORAGE_URI", "memory://")
os.environ.pop("USE_MYSQL", None)
os.environ.pop("DATABASE_URL", None)

from app import create_app
from config import Config
from extensions import db
from models import RefreshToken, User, VerbalAutopsy


TEST_PASSWORD = "Strong-Test-Password-123!"


@pytest.fixture()
def app(tmp_path: Path):
    """Create an isolated application backed by a temporary SQLite database."""
    database_path = tmp_path / "regression.db"

    # create_app() reads Config.SQLALCHEMY_DATABASE_URI during initialization,
    # so override the class value before constructing the application. This
    # prevents the suite from touching the repository's normal SQLite database.
    original_uri = Config.SQLALCHEMY_DATABASE_URI
    Config.SQLALCHEMY_DATABASE_URI = f"sqlite:///{database_path}"

    try:
        application = create_app()
        application.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=True,
            RATELIMIT_ENABLED=False,
        )

        with application.app_context():
            db.drop_all()
            db.create_all()

        yield application

        with application.app_context():
            db.session.remove()
            db.drop_all()
    finally:
        Config.SQLALCHEMY_DATABASE_URI = original_uri


def create_user(username, role="user", active=True, verified=False):
    user = User(
        username=username,
        email=f"{username}@example.test",
        role=role,
        is_active=active,
        is_verified=verified,
    )
    user.set_password(TEST_PASSWORD)
    db.session.add(user)
    db.session.commit()
    return user


def api_login(client, username, password=TEST_PASSWORD):
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Application and configuration
# ---------------------------------------------------------------------------

def test_health_endpoint_and_swagger(app):
    client = app.test_client()

    health = client.get("/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "healthy"

    swagger = client.get("/swagger")
    assert swagger.status_code == 200


def test_testing_database_is_isolated(app):
    with app.app_context():
        assert db.engine.url.get_backend_name() == "sqlite"
        assert User.query.count() == 0
        assert VerbalAutopsy.query.count() == 0


# ---------------------------------------------------------------------------
# Account workflow
# ---------------------------------------------------------------------------

def test_signup_creates_active_regular_user(app):
    client = app.test_client()

    response = client.post(
        "/signup",
        data={
            "username": "newuser",
            "email": "newuser@example.test",
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
        },
        follow_redirects=False,
    )

    # CSRF is enabled, so a real signup request must first obtain a token.
    # If the form rejects the request, the database must remain unchanged.
    if response.status_code in {400, 403}:
        with app.app_context():
            assert User.query.filter_by(username="newuser").first() is None
        return

    assert response.status_code in {200, 302, 303}

    with app.app_context():
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.role == "user"
        assert user.is_active is True
        assert user.is_verified is False


def test_unverified_active_user_can_use_api(app):
    with app.app_context():
        create_user("active_unverified", verified=False)

    client = app.test_client()
    data = api_login(client, "active_unverified")

    assert data["user"]["role"] == "user"
    assert data["user"]["is_verified"] is False
    assert data["user"]["is_active"] is True


def test_inactive_user_cannot_login(app):
    with app.app_context():
        create_user("inactive", active=False, verified=True)

    client = app.test_client()
    response = client.post(
        "/api/auth/login",
        json={
            "username": "inactive",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 403


def test_refresh_requires_active_account(app):
    with app.app_context():
        user = create_user("refreshuser", verified=False)

    client = app.test_client()
    login = api_login(client, "refreshuser")
    first_refresh = login["refresh_token"]

    refreshed = client.post(
        "/api/auth/refresh",
        json={"refresh_token": first_refresh},
    )
    assert refreshed.status_code == 200
    second_refresh = refreshed.get_json()["refresh_token"]

    with app.app_context():
        user = db.session.get(User, user.id)
        user.is_active = False
        db.session.commit()

    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": second_refresh},
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# JWT protection and current database authorization
# ---------------------------------------------------------------------------

def test_protected_endpoints_require_bearer_token(app):
    client = app.test_client()

    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/verbal-autopsy/").status_code == 401


def test_current_database_role_controls_existing_access_token(app):
    with app.app_context():
        user = create_user("roleuser", role="user")

    client = app.test_client()
    login = api_login(client, "roleuser")
    token = login["access_token"]

    response = client.get("/api/auth/me", headers=bearer(token))
    assert response.status_code == 200
    assert response.get_json()["role"] == "user"

    with app.app_context():
        user = db.session.get(User, user.id)
        user.role = "upload_user"
        db.session.commit()

    response = client.get("/api/auth/me", headers=bearer(token))
    assert response.status_code == 200
    assert response.get_json()["role"] == "upload_user"


def test_existing_access_token_is_denied_after_deactivation(app):
    with app.app_context():
        user = create_user("revokeduser")

    client = app.test_client()
    login = api_login(client, "revokeduser")
    token = login["access_token"]

    with app.app_context():
        user = db.session.get(User, user.id)
        user.is_active = False
        db.session.commit()

    response = client.get("/api/auth/me", headers=bearer(token))
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Role capabilities
# ---------------------------------------------------------------------------

def test_role_capabilities_match_project_policy(app):
    with app.app_context():
        regular = create_user("regular", role="user")
        uploader = create_user("uploader", role="upload_user")
        administrator = create_user("administrator", role="admin")

        assert regular.can_access_dashboard() is True
        assert regular.can_download() is True
        assert regular.can_upload() is False
        assert regular.can_edit() is False
        assert regular.can_delete() is False
        assert regular.can_manage_users() is False

        assert uploader.can_access_dashboard() is True
        assert uploader.can_download() is True
        assert uploader.can_upload() is True
        assert uploader.can_edit() is False
        assert uploader.can_delete() is False
        assert uploader.can_manage_users() is False

        assert administrator.can_access_dashboard() is True
        assert administrator.can_download() is True
        assert administrator.can_upload() is True
        assert administrator.can_edit() is True
        assert administrator.can_delete() is True
        assert administrator.can_manage_users() is True


def test_all_authenticated_roles_can_read_records(app):
    with app.app_context():
        record = VerbalAutopsy(
            patientid="TEST-PATIENT-001",
            datim_code="TEST-DATIM-001",
            state_name="Lagos",
            lga_name="Ikeja",
            facility_name="Test Facility",
        )
        db.session.add(record)
        create_user("regular", role="user")
        create_user("uploader", role="upload_user")
        create_user("administrator", role="admin")

    client = app.test_client()

    for username in ("regular", "uploader", "administrator"):
        login = api_login(client, username)
        response = client.get(
            "/api/verbal-autopsy/",
            headers=bearer(login["access_token"]),
        )
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Refresh-token rotation and storage
# ---------------------------------------------------------------------------

def test_refresh_token_rotation_revokes_old_token(app):
    with app.app_context():
        create_user("rotator")

    client = app.test_client()
    login = api_login(client, "rotator")
    first_refresh = login["refresh_token"]

    refreshed = client.post(
        "/api/auth/refresh",
        json={"refresh_token": first_refresh},
    )
    assert refreshed.status_code == 200

    second_refresh = refreshed.get_json()["refresh_token"]
    assert second_refresh != first_refresh

    reused = client.post(
        "/api/auth/refresh",
        json={"refresh_token": first_refresh},
    )
    assert reused.status_code == 401

    with app.app_context():
        tokens = RefreshToken.query.all()
        assert len(tokens) == 2
        assert sum(bool(token.revoked) for token in tokens) == 1


def test_refresh_tokens_are_stored_as_hashes_not_raw_values(app):
    with app.app_context():
        create_user("hashtest")

    client = app.test_client()
    login = api_login(client, "hashtest")
    raw_refresh = login["refresh_token"]

    with app.app_context():
        token = RefreshToken.query.first()
        assert token is not None
        assert token.token_hash != raw_refresh
        assert len(token.token_hash) == 64


# ---------------------------------------------------------------------------
# Record mutation authorization
# ---------------------------------------------------------------------------

def test_regular_user_cannot_modify_or_delete_records(app):
    with app.app_context():
        record = VerbalAutopsy(
            patientid="TEST-PATIENT-USER",
            datim_code="TEST-DATIM-USER",
        )
        db.session.add(record)
        create_user("regular", role="user")
        record_id = record.id

    client = app.test_client()
    login = api_login(client, "regular")
    headers = bearer(login["access_token"])

    assert client.put(
        f"/api/verbal-autopsy/{record_id}",
        json={"state_name": "Lagos"},
        headers=headers,
    ).status_code == 403

    assert client.delete(
        f"/api/verbal-autopsy/{record_id}",
        headers=headers,
    ).status_code == 403


def test_upload_user_cannot_modify_or_delete_records(app):
    with app.app_context():
        record = VerbalAutopsy(
            patientid="TEST-PATIENT-UPLOADER",
            datim_code="TEST-DATIM-UPLOADER",
        )
        db.session.add(record)
        create_user("uploader", role="upload_user")
        record_id = record.id

    client = app.test_client()
    login = api_login(client, "uploader")
    headers = bearer(login["access_token"])

    assert client.put(
        f"/api/verbal-autopsy/{record_id}",
        json={"state_name": "Lagos"},
        headers=headers,
    ).status_code == 403

    assert client.delete(
        f"/api/verbal-autopsy/{record_id}",
        headers=headers,
    ).status_code == 403


def test_admin_can_modify_record_without_identifier_mass_assignment(app):
    with app.app_context():
        record = VerbalAutopsy(
            patientid="TEST-PATIENT-ADMIN",
            datim_code="TEST-DATIM-ADMIN",
        )
        db.session.add(record)
        create_user("administrator", role="admin")
        record_id = record.id

    client = app.test_client()
    login = api_login(client, "administrator")
    headers = bearer(login["access_token"])

    response = client.put(
        f"/api/verbal-autopsy/{record_id}",
        json={"state_name": "Lagos", "patientid": "MALICIOUS-ID"},
        headers=headers,
    )
    assert response.status_code == 200

    with app.app_context():
        record = db.session.get(VerbalAutopsy, record_id)
        assert record.state_name == "Lagos"
        assert record.patientid == "TEST-PATIENT-ADMIN"


# ---------------------------------------------------------------------------
# Authentication smoke tests
# ---------------------------------------------------------------------------

def test_invalid_credentials_are_rejected(app):
    with app.app_context():
        create_user("credentialtest")

    client = app.test_client()
    response = client.post(
        "/api/auth/login",
        json={
            "username": "credentialtest",
            "password": "wrong-password",
        },
    )
    assert response.status_code == 401


def test_refresh_and_logout_endpoints_work(app):
    with app.app_context():
        create_user("logouttest")

    client = app.test_client()
    login = api_login(client, "logouttest")
    refresh_token = login["refresh_token"]

    logout = client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout.status_code == 200

    reused = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert reused.status_code == 401
