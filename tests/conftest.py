import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.database import get_connection

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
