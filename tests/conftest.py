import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database import get_connection
from app.auth_utils import get_current_user, get_user_connection


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_conn():
    """Fixture para mockear la conexión a la base de datos"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Sobrescribir la dependencia get_connection
    app.dependency_overrides[get_connection] = lambda: mock_conn
    yield mock_conn, mock_cursor
    app.dependency_overrides.clear()


@pytest.fixture
def mock_pg_conn():
    """Fixture para mockear la conexión a PostgreSQL"""
    with patch("app.postgres_db.get_pg_connection") as mock_pg:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pg.return_value = mock_conn
        yield mock_cursor


@pytest.fixture
def mock_token_not_revoked():
    """Fixture para mockear que el token no está revocado"""
    with patch("app.auth_utils.is_token_revoked", return_value=False):
        yield


@pytest.fixture
def mock_user_connection():
    """Fixture para mockear la conexión de usuario con routing"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Sobrescribir get_user_connection
    app.dependency_overrides[get_user_connection] = lambda: mock_conn
    yield mock_conn, mock_cursor
    app.dependency_overrides.clear()
