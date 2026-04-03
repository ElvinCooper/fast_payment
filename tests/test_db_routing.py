from unittest.mock import patch, MagicMock
from app.database import get_connection
from app.mysql_db import (
    get_user_database,
    get_all_user_databases,
)


class TestGetUserDatabase:
    """Tests para la función get_user_database"""

    def test_get_user_database_existe(self):
        """Verifica que obtiene la BD asignada correctamente"""
        with patch("mysql.connector.connect") as mock_mysql:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = ("finanzasprueba",)
            mock_conn.cursor.return_value = mock_cursor
            mock_mysql.return_value = mock_conn

            result = get_user_database(1)

            assert result == "finanzasprueba"

    def test_get_user_database_no_existe(self):
        """Verifica que retorna None cuando no existe"""
        with patch("mysql.connector.connect") as mock_mysql:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value = mock_cursor
            mock_mysql.return_value = mock_conn

            result = get_user_database(999)

            assert result is None


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
        with patch("mysql.connector.connect") as mock_mysql:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "finanzas"),
                (2, "ventas"),
                (3, None),
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_mysql.return_value = mock_conn

            result = get_all_user_databases()

            assert isinstance(result, dict)
            assert result[1] == "finanzas"
            assert result[2] == "ventas"
            assert result[3] is None

    def test_get_all_user_databases_vacio(self):
        """Verifica que retorna dict vacío cuando no hay usuarios"""
        with patch("mysql.connector.connect") as mock_mysql:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.cursor.return_value = mock_cursor
            mock_mysql.return_value = mock_conn

            result = get_all_user_databases()

            assert result == {}
