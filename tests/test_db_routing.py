from unittest.mock import patch, MagicMock
from app.database import get_connection
from app.postgres_db import (
    get_user_database,
    sincronizar_usuarios,
    get_all_user_databases,
)


class TestGetUserDatabase:
    """Tests para la función get_user_database"""

    def test_get_user_database_existe(self):
        """Verifica que obtiene la BD asignada correctamente"""
        with patch("app.postgres_db.get_pg_connection") as mock_pg:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {"db_asignada": "finanzas_cliente1"}
            mock_conn.cursor.return_value = mock_cursor
            mock_pg.return_value = mock_conn

            result = get_user_database(1)

            assert result == "finanzas_cliente1"

    def test_get_user_database_no_existe(self):
        """Verifica que retorna None cuando no existe"""
        with patch("app.postgres_db.get_pg_connection") as mock_pg:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value = mock_cursor
            mock_pg.return_value = mock_conn

            result = get_user_database(999)

            assert result is None


class TestSincronizarUsuarios:
    """Tests para la sincronización de usuarios"""

    def test_sincronizar_usuarios_existe(self):
        """Verifica que la función sincronizar_usuarios existe y es callable"""
        assert callable(sincronizar_usuarios)

    def test_sincronizar_usuarios_sin_usuarios(self):
        """Verifica que sincroniza cuando no hay usuarios en MySQL"""
        with (
            patch("mysql.connector.connect") as mock_mysql_conn,
            patch("app.postgres_db.get_pg_connection") as mock_pg,
        ):
            mock_mysql_cursor = MagicMock()
            mock_mysql_cursor.fetchall.return_value = []
            mock_mysql_inst = MagicMock()
            mock_mysql_inst.cursor.return_value = mock_mysql_cursor
            mock_mysql_conn.return_value = mock_mysql_inst

            mock_pg_conn = MagicMock()
            mock_pg_cursor = MagicMock()
            mock_pg_conn.cursor.return_value = mock_pg_cursor
            mock_pg.return_value = mock_pg_conn

            sincronizar_usuarios()

            mock_mysql_conn.assert_called_once()
            mock_pg_conn.commit.assert_called_once()


class TestUserConnectionRouting:
    """Tests para la conexión dinámica por usuario"""

    def test_get_connection_acepta_user_id(self):
        """Verifica que get_connection acepta user_id como parámetro"""
        import inspect

        sig = inspect.signature(get_connection)
        params = list(sig.parameters.keys())

        assert "user_id" in params
        assert sig.parameters["user_id"].default is None


class TestGetAllUserDatabases:
    """Tests para la función get_all_user_databases"""

    def test_get_all_user_databases_existe(self):
        """Verifica que la función existe y es callable"""
        assert callable(get_all_user_databases)

    def test_get_all_user_databases_retorna_dict(self):
        """Verifica que retorna un diccionario"""
        with patch("app.postgres_db.get_pg_connection") as mock_pg:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                {"idusuario": 1, "db_asignada": "finanzas"},
                {"idusuario": 2, "db_asignada": "ventas"},
                {"idusuario": 3, "db_asignada": None},
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_pg.return_value = mock_conn

            result = get_all_user_databases()

            assert isinstance(result, dict)
            assert result[1] == "finanzas"
            assert result[2] == "ventas"
            assert result[3] is None

    def test_get_all_user_databases_vacio(self):
        """Verifica que retorna dict vacío cuando no hay usuarios"""
        with patch("app.postgres_db.get_pg_connection") as mock_pg:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.cursor.return_value = mock_cursor
            mock_pg.return_value = mock_conn

            result = get_all_user_databases()

            assert result == {}
