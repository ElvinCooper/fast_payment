import pytest
from unittest.mock import patch
from app.auth_utils import create_access_token


@pytest.fixture
def admin_token():
    token = create_access_token(
        data={
            "sub": "testuser",
            "id": 1,
            "db_name": "finanzas_test",
            "tipouser": "admin",
            "username": "testuser",
        }
    )
    return {"Authorization": f"Bearer {token}"}


def test_login_success(client, mock_db_conn, mock_pg_conn):
    with patch("app.routers.auth.get_user_db_from_ciausers") as mock_get_cia:
        with patch("app.routers.auth.get_user_empresas") as mock_empresas:
            mock_get_cia.return_value = {
                "idusers": 1,
                "estatus": 1,
                "tipouser": "admin",
                "db_asignada": "finanzas_test",
                "empresa": "Empresa Test",
                "empresa_id": 1,
                "idcia": 1,
            }
            mock_empresas.return_value = [
                {"idcia": 1, "cidescripcion": "Empresa Test", "descbd": "finanzas_test"}
            ]

            response = client.post(
                "/api/v1/auth/login",
                json={"usuario": "testuser", "password": "correct_clave"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["usuario"] == "testuser"
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user_db"] == "finanzas_test"
            assert data["tipouser"] == "admin"


def test_login_failure(client, mock_db_conn, mock_pg_conn):
    with patch("app.routers.auth.get_user_db_from_ciausers", return_value=None):
        response = client.post(
            "/api/v1/auth/login",
            json={"usuario": "testuser", "password": "wrong_clave"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Usuario o clave incorrectos"


def test_login_inactive_user(client, mock_db_conn, mock_pg_conn):
    with patch("app.routers.auth.get_user_db_from_ciausers") as mock_get_cia:
        mock_get_cia.return_value = {
            "idusers": 1,
            "estatus": 0,
            "db_asignada": "finanzas_test",
        }

        response = client.post(
            "/api/v1/auth/login",
            json={"usuario": "inactiveuser", "password": "correct_clave"},
        )

        assert response.status_code == 403
        assert "inactivo" in response.json()["detail"]


def test_switch_tenant_success(client, admin_token):
    with patch("app.routers.auth.validate_user_empresa") as mock_validate:
        mock_validate.return_value = {
            "descbd": "finanzas_prueba2",
            "cidescripcion": "Empresa 2",
            "idcia": 2,
        }

        response = client.post(
            "/api/v1/auth/switch-tenant",
            json={"empresa_id": 2},
            headers=admin_token,
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["db_name"] == "finanzas_prueba2"
        assert data["empresa"] == "Empresa 2"
        assert data["message"] == "Tenant cambiado exitosamente"


def test_switch_tenant_no_access(client, admin_token):
    with patch("app.routers.auth.validate_user_empresa", return_value=None):
        response = client.post(
            "/api/v1/auth/switch-tenant",
            json={"empresa_id": 999},
            headers=admin_token,
        )

        assert response.status_code == 403
        assert "No tienes acceso a esta empresa" in response.json()["detail"]


def test_switch_tenant_sin_auth(client):
    response = client.post(
        "/api/v1/auth/switch-tenant",
        json={"empresa_id": 1},
    )
    assert response.status_code == 401
