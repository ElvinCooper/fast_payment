from unittest.mock import patch


def test_login_success(client, mock_db_conn, mock_pg_conn):
    # Mock para get_user_db_from_ciausers (busca en ciausers primero)
    with patch("app.routers.auth.get_user_db_from_ciausers") as mock_get_cia:
        mock_get_cia.return_value = {
            "idusers": 1,
            "estatus": 1,
            "tipouser": "admin",
            "db_asignada": "finanzas_test",
            "empresa": "Empresa Test",
        }

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
    # Simular que el usuario NO existe en ciausers
    with patch("app.routers.auth.get_user_db_from_ciausers", return_value=None):
        response = client.post(
            "/api/v1/auth/login",
            json={"usuario": "testuser", "password": "wrong_clave"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Usuario o clave incorrectos"


def test_login_inactive_user(client, mock_db_conn, mock_pg_conn):
    # Simular usuario con estatus = 0 (inactivo)
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
