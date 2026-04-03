import pytest
from unittest.mock import patch, MagicMock
from app.auth_utils import create_access_token


@pytest.fixture
def admin_auth_header():
    token = create_access_token(
        data={
            "sub": "admin",
            "id": 1,
            "db_name": "finanzas_test",
            "tipouser": "admin",
            "username": "admin",
            "idcia": 1,
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def non_admin_auth_header():
    token = create_access_token(
        data={
            "sub": "user",
            "id": 4,
            "db_name": "finanzas_test",
            "tipouser": "user",
            "username": "user",
            "idcia": 1,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def test_get_users_sin_auth(client):
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_get_users_success(client, admin_auth_header, mock_cia_conn):
    mock_conn, mock_cursor = mock_cia_conn

    mock_cursor.fetchall.return_value = [
        {"idusers": 3, "usuario": "testuser", "tipouser": "admin"},
        {"idusers": 4, "usuario": "anotheruser", "tipouser": "standard"},
    ]

    response = client.get("/api/v1/admin/users", headers=admin_auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["idusuario"] == 3
    assert data[0]["usuario"] == "testuser"
    assert data[0]["tipouser"] == "admin"
    assert data[1]["idusuario"] == 4
    assert data[1]["tipouser"] == "standard"


def test_get_users_empty(client, admin_auth_header, mock_cia_conn):
    mock_conn, mock_cursor = mock_cia_conn
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
            "app.mysql_db.actualizar_usuario_cia",
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
            "app.mysql_db.actualizar_usuario_cia",
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
            "app.mysql_db.actualizar_usuario_cia",
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


def test_listar_tipos_usuario_sin_auth(client):
    response = client.get("/api/v1/admin/user/tipos")
    assert response.status_code == 401


def test_listar_tipos_usuario_no_admin(client, non_admin_auth_header):
    with patch("app.routers.admin.is_admin", return_value=False):
        response = client.get("/api/v1/admin/user/tipos", headers=non_admin_auth_header)

    assert response.status_code == 403
    assert "Solo administradores" in response.json()["detail"]


def test_listar_tipos_usuario_success(client, admin_auth_header):
    with patch("app.routers.admin.is_admin", return_value=True):
        with patch(
            "app.mysql_db.get_tipos_usuario", return_value=["admin", "standard"]
        ):
            response = client.get("/api/v1/admin/user/tipos", headers=admin_auth_header)

    assert response.status_code == 200
    assert "tipos_usuario" in response.json()
    assert response.json()["tipos_usuario"] == ["admin", "standard"]


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
        patch("app.dependencies.is_token_revoked", return_value=False),
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

    # Mockear la conexión de usuario para el endpoint get_server_databases
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True

    with (
        patch("mysql.connector.connect") as mock_mysql_conn,
        patch("app.dependencies.is_token_revoked", return_value=False),
        patch("app.mysql_db.get_user_empresas", return_value=[]),
        patch("app.routers.admin.is_admin", return_value=True),
    ):
        # La primera conexión (get_user_connection - ciadatabase) debe ser mockeada con el mock_conn
        mock_mysql_conn.side_effect = [
            mock_conn,  # Para get_user_connection -> ciadatabase
            mysql.connector.Error(
                "Connection refused"
            ),  # Para SHOW DATABASES (sin database)
        ]

        response = client.get(
            "/api/v1/admin/server/databases", headers=admin_auth_header
        )

    assert response.status_code == 500
    assert "Error al conectar al servidor" in response.json()["detail"]
