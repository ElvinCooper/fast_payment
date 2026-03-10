import pytest
from app.auth_utils import create_access_token


@pytest.fixture
def auth_header():
    token = create_access_token(data={"sub": "testuser", "id": 1})
    return {"Authorization": f"Bearer {token}"}


def test_obtener_usuario_success(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchone.return_value = {"idusuario": 1, "usuario": "testuser"}

    response = client.get("/api/v1/usuarios/1", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["usuario"] == "testuser"


def test_obtener_usuario_404(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    # Simular que el usuario no existe
    mock_cursor.fetchone.return_value = None

    response = client.get("/api/v1/usuarios/999", headers=auth_header)

    assert response.status_code == 404
    assert "No se encontro ningun usuario con este id" in response.json()["detail"]
