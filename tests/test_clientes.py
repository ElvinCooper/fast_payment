import pytest
from app.auth_utils import create_access_token


@pytest.fixture
def auth_header():
    token = create_access_token(data={"sub": "testuser", "id": 1})
    return {"Authorization": f"Bearer {token}"}


def test_buscar_clientes_sin_auth(client):
    response = client.get("/api/v1/clientes/buscar?CLIENTE=juan")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_buscar_clientes_success(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    # Datos simulados de la DB
    mock_cursor.fetchall.return_value = [
        {
            "idcliente": 1,
            "CLIENTE": "Juan Perez",
            "nprestamo": 123,
            "vprestamo": 1000.50,
            "estado_cuota": "sin cuota vencida",
            "cantidad_cutas": 0,
            "vpendiente": 0,
            "fecha": "13-03-2026 15:44:26",
        }
    ]

    response = client.get("/api/v1/clientes/buscar?CLIENTE=juan", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["CLIENTE"] == "Juan Perez"
    assert data[0]["cantidad_cutas"] == 0
    assert data[0]["vpendiente"] == 0 or data[0]["vpendiente"] == "0"
    assert data[0]["estado_cuota"] == "sin cuota vencida"


def test_obtener_cliente_por_id_404(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    # Simular que el cliente no existe
    mock_cursor.fetchall.return_value = []

    response = client.get("/api/v1/clientes/999", headers=auth_header)

    assert response.status_code == 404
    assert (
        "No se encontraron clientes con prestamos activos" in response.json()["detail"]
    )
