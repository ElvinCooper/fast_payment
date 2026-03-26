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

    response = client.get("/api/v1/admin/users", headers=admin_auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["idusuario"] == 3
    assert data[0]["usuario"] == "testuser"
    assert data[1]["idusuario"] == 4
    assert data[1]["usuario"] == "anotheruser"


def test_get_users_empty(client, admin_auth_header, mock_db_conn):
    mock_conn, mock_cursor = mock_db_conn
    mock_cursor.fetchall.return_value = []

    response = client.get("/api/v1/admin/users", headers=admin_auth_header)

    assert response.status_code == 200
    assert response.json() == []


def test_asignar_acceso_sin_auth(client):
    response = client.put(
        "/api/v1/admin/user/cia",
        json={"idusers": 3, "clave": "testkey"},
    )
    assert response.status_code == 401


def test_asignar_acceso_usuario_no_existe(client, admin_auth_header, mock_db_conn):
    with patch("app.routers.admin.is_admin", return_value=True):
        with patch(
            "app.postgres_db.actualizar_usuario_cia",
            return_value="Usuario no encontrado en ciausers",
        ):
            response = client.put(
                "/api/v1/admin/user/cia",
                json={"idusers": 999, "clave": "testkey"},
                headers=admin_auth_header,
            )

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"].lower()


def test_asignar_acceso_no_existe_en_mapeo(client, admin_auth_header, mock_db_conn):
    with patch("app.routers.admin.is_admin", return_value=True):
        with patch(
            "app.postgres_db.actualizar_usuario_cia",
            return_value="Usuario no encontrado en ciausers",
        ):
            response = client.put(
                "/api/v1/admin/user/cia",
                json={"idusers": 3, "clave": "testkey"},
                headers=admin_auth_header,
            )

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"].lower()


def test_asignar_acceso_success(client, admin_auth_header, mock_db_conn):
    with patch("app.routers.admin.is_admin", return_value=True):
        with patch(
            "app.postgres_db.actualizar_usuario_cia",
            return_value="Usuario actualizado exitosamente",
        ):
            response = client.put(
                "/api/v1/admin/user/cia",
                json={
                    "idusers": 3,
                    "clave": "testkey",
                    "estatus": 1,
                    "tipouser": "admin",
                },
                headers=admin_auth_header,
            )

    assert response.status_code == 200
    assert "actualizado" in response.json()["message"].lower()


def test_get_server_databases_sin_auth(client):
    response = client.get("/api/v1/admin/server/databases")
    assert response.status_code == 401


def test_get_server_databases_no_admin(client, non_admin_auth_header, mock_db_conn):
    with patch("app.routers.admin.is_admin", return_value=False):
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


def test_get_server_databases_error_conexion(client, admin_auth_header):
    """Test que simula un error al conectar al servidor MySQL"""
    import mysql.connector

    # Mockear get_user_connection para evitar que intente conectar
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"idusuario": 1, "tipouser": "admin"}
    mock_conn.cursor.return_value = mock_cursor

    with (
        patch("mysql.connector.connect") as mock_mysql_conn,
        patch("app.auth_utils.is_token_revoked", return_value=False),
        patch("app.routers.admin.is_admin", return_value=True),
        patch("app.postgres_db.get_user_database") as mock_get_db,
        patch("app.auth_utils.get_user_connection") as mock_user_conn,
    ):
        # Configurar el mock para get_user_database
        mock_get_db.return_value = "ciadatabase"
        mock_user_conn.return_value = mock_conn

        # Hacer que la conexión del servidor falle
        def connect_side_effect(*args, **kwargs):
            # Permitir la primera conexión (get_user_database),
            # pero fallar la segunda (SHOW DATABASES)
            if kwargs.get("database") == "ciadatabase":
                mock_temp_conn = MagicMock()
                return mock_temp_conn
            raise mysql.connector.Error("Connection refused")

        mock_mysql_conn.side_effect = connect_side_effect

        response = client.get(
            "/api/v1/admin/server/databases", headers=admin_auth_header
        )

    assert response.status_code == 500
    assert "Error al conectar al servidor" in response.json()["detail"]
