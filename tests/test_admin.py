import pytest
from unittest.mock import patch, MagicMock
from app.auth_utils import create_access_token


@pytest.fixture
def admin_auth_header():
    token = create_access_token(data={"sub": "admin", "id": 1})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def non_admin_auth_header():
    token = create_access_token(data={"sub": "user", "id": 4})
    return {"Authorization": f"Bearer {token}"}


def test_get_users_sin_auth(client):
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_get_users_success(client, admin_auth_header, mock_db_conn):
    mock_conn, mock_cursor = mock_db_conn

    mock_cursor.fetchall.return_value = [
        {"idusuario": 3, "usuario": "testuser"},
        {"idusuario": 4, "usuario": "anotheruser"},
    ]

    with patch("app.postgres_db.get_all_user_databases") as mock_get_dbs:
        mock_get_dbs.return_value = {
            3: "finanzas_test",
            4: None,
        }

        response = client.get("/api/v1/admin/users", headers=admin_auth_header)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["usuario"] == "testuser"
        assert data[0]["db_asignada"] == "finanzas_test"
        assert data[1]["usuario"] == "anotheruser"
        assert data[1]["db_asignada"] is None


def test_get_users_empty(client, admin_auth_header, mock_db_conn):
    mock_conn, mock_cursor = mock_db_conn
    mock_cursor.fetchall.return_value = []

    with patch("app.postgres_db.get_all_user_databases", return_value={}):
        response = client.get("/api/v1/admin/users", headers=admin_auth_header)

        assert response.status_code == 200
        assert response.json() == []


def test_asignar_acceso_sin_auth(client):
    response = client.put(
        "/api/v1/admin/user/routing",
        json={"idusuario": 3, "database": "testdb", "clave": "testkey"},
    )
    assert response.status_code == 401


def test_asignar_acceso_usuario_no_existe(client, admin_auth_header, mock_db_conn):
    mock_conn, mock_cursor = mock_db_conn

    mock_cursor.fetchone.return_value = None

    response = client.put(
        "/api/v1/admin/user/routing",
        json={"idusuario": 999, "database": "testdb", "clave": "testkey"},
        headers=admin_auth_header,
    )

    assert response.status_code == 404
    assert "Usuario no encontrado" in response.json()["detail"]


def test_asignar_acceso_no_existe_en_mapeo(client, admin_auth_header, mock_db_conn):
    with patch(
        "app.postgres_db.asignar_db_usuario", return_value="Usuario no encontrado"
    ):
        response = client.put(
            "/api/v1/admin/user/routing",
            json={"idusuario": 3, "clave": "testkey"},
            headers=admin_auth_header,
        )

    assert response.status_code == 404
    assert "Usuario no encontrado" in response.json()["detail"]


def test_asignar_acceso_success(client, admin_auth_header, mock_db_conn):
    with patch(
        "app.postgres_db.asignar_db_usuario", return_value="Filas actualizadas: 1"
    ):
        response = client.put(
            "/api/v1/admin/user/routing",
            json={"idusuario": 3, "clave": "testkey"},
            headers=admin_auth_header,
        )

    assert response.status_code == 200
    assert "actualizado exitosamente" in response.json()["message"]


def test_get_server_databases_sin_auth(client):
    response = client.get("/api/v1/admin/server/databases")
    assert response.status_code == 401


def test_get_server_databases_no_admin(client, non_admin_auth_header, mock_db_conn):
    response = client.get(
        "/api/v1/admin/server/databases", headers=non_admin_auth_header
    )

    assert response.status_code == 403
    assert "Solo administradores pueden acceder" in response.json()["detail"]


def test_get_server_databases_success(client, admin_auth_header, mock_db_conn):
    mock_conn, mock_cursor = mock_db_conn

    with (
        patch("mysql.connector.connect") as mock_mysql_conn,
        patch("app.auth_utils.is_token_revoked", return_value=False),
    ):
        mock_mysql_conn.return_value.__enter__ = MagicMock(
            return_value=mock_mysql_conn.return_value
        )
        mock_mysql_conn.return_value.__exit__ = MagicMock(return_value=False)

        mock_temp_conn = MagicMock()
        mock_temp_cursor = MagicMock()
        mock_temp_cursor.fetchall.return_value = [
            ("information_schema",),
            ("mydb",),
            ("mysql",),
            ("testdb",),
        ]
        mock_temp_conn.cursor.return_value = mock_temp_cursor

        mock_mysql_conn.return_value = mock_temp_conn

        response = client.get(
            "/api/v1/admin/server/databases", headers=admin_auth_header
        )

    assert response.status_code == 200
    data = response.json()
    assert "databases" in data
    assert "mydb" in data["databases"]
    assert "testdb" in data["databases"]


def test_get_server_databases_error_conexion(client, admin_auth_header, mock_db_conn):
    mock_conn, mock_cursor = mock_db_conn

    import mysql.connector

    with (
        patch("mysql.connector.connect") as mock_mysql_conn,
        patch("app.auth_utils.is_token_revoked", return_value=False),
    ):
        mock_mysql_conn.side_effect = mysql.connector.Error("Connection refused")

        response = client.get(
            "/api/v1/admin/server/databases", headers=admin_auth_header
        )

    assert response.status_code == 500
    assert "Error al conectar al servidor" in response.json()["detail"]
