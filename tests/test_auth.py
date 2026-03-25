from unittest.mock import patch


def test_login_success(client, mock_db_conn, mock_pg_conn):
    mock_conn, mock_cursor = mock_db_conn

    # Simular que el usuario existe en la DB
    mock_cursor.fetchone.return_value = {"idusuario": 1, "usuario": "testuser"}

    # Mock para get_user_database
    with patch("app.routers.auth.get_user_database") as mock_get_db:
        mock_get_db.return_value = "finanzas_test"

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


def test_login_failure(client, mock_db_conn, mock_pg_conn):
    mock_conn, mock_cursor = mock_db_conn

    # Simular que el usuario NO existe o clave incorrecta
    mock_cursor.fetchone.return_value = None

    with patch("app.routers.auth.get_user_database", return_value=None):
        response = client.post(
            "/api/v1/auth/login",
            json={"usuario": "testuser", "password": "wrong_clave"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Usuario o clave incorrectos"
