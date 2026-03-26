import pytest
from unittest.mock import patch
from app.auth_utils import create_access_token


@pytest.fixture
def auth_header():
    token = create_access_token(data={"sub": "testuser", "id": 1})
    return {"Authorization": f"Bearer {token}"}


def test_me_success(client, auth_header):
    response = client.get("/api/v1/usuarios/me", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert data["idusuario"] == 1
    assert data["usuario"] == "testuser"


def test_me_without_auth(client):
    response = client.get("/api/v1/usuarios/me")

    assert response.status_code == 401


def test_logout_success(client, auth_header, mock_pg_conn):
    mock_cursor = mock_pg_conn

    with patch("app.auth_utils.is_token_revoked", return_value=False):
        response = client.post("/api/v1/usuarios/logout", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["message"] == "Sesión cerrada con éxito"
    mock_cursor.execute.assert_called_once()


def test_logout_without_auth(client):
    response = client.post("/api/v1/usuarios/logout")

    assert response.status_code == 401


def test_refresh_success(client, auth_header, mock_pg_conn):
    mock_cursor = mock_pg_conn
    mock_cursor.fetchone.return_value = None

    with patch("app.auth_utils.is_token_revoked", return_value=False):
        response = client.post("/api/v1/usuarios/refresh", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_without_auth(client):
    response = client.post("/api/v1/usuarios/refresh")

    assert response.status_code == 401


def test_refresh_revoked_token(client, mock_pg_conn):
    mock_cursor = mock_pg_conn
    mock_cursor.fetchone.return_value = {"jti": "some-jti"}

    token = create_access_token(data={"sub": "testuser", "id": 1})
    auth_header = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/usuarios/refresh", headers=auth_header)

    assert response.status_code == 401
    assert response.json()["detail"] == "Token ha sido revocado"
