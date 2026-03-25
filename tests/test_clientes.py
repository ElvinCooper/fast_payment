import pytest
from app.auth_utils import create_access_token
from datetime import datetime


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
            "deuda_al_dia": 0,
            "mora_total": 0,
            "fecha": "13-03-2026 15:44:26",
        }
    ]

    response = client.get("/api/v1/clientes/buscar?CLIENTE=juan", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["CLIENTE"] == "Juan Perez"
    assert data[0]["cantidad_cutas"] == 0
    assert data[0]["deuda_al_dia"] == 0 or data[0]["deuda_al_dia"] == "0"
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


def test_obtener_clientes_sin_auth(client):
    response = client.get("/api/v1/clientes/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_obtener_clientes_success(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchall.return_value = [
        {
            "idcliente": 1,
            "CLIENTE": "Juan Perez",
            "nprestamo": 123,
            "vprestamo": 1000.50,
            "FECHAP": datetime(2026, 3, 15),
            "fechav": datetime(2026, 6, 15),
            "cel": "8091234567",
            "estado_cuota": "sin cuota vencida",
            "cantidad_cutas": 0,
            "deuda_al_dia": 0,
            "mora_total": 0,
            "fecha": "15-03-2026 10:00:00",
        }
    ]

    response = client.get("/api/v1/clientes/", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["CLIENTE"] == "Juan Perez"
    assert data[0]["FECHAP"] == "15-03-2026"
    assert data[0]["fechav"] == "15-06-2026"


def test_obtener_cliente_por_id_success(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchall.return_value = [
        {
            "idcliente": 1,
            "CLIENTE": "Juan Perez",
            "nprestamo": 123,
            "vprestamo": 1000.50,
            "FECHAP": datetime(2026, 3, 15),
            "fechav": datetime(2026, 6, 15),
            "cel": "8091234567",
            "estado_cuota": "sin cuota vencida",
            "cantidad_cutas": 0,
            "deuda_al_dia": 0,
            "mora_total": 0,
            "fecha": "15-03-2026 10:00:00",
        }
    ]

    response = client.get("/api/v1/clientes/1", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["CLIENTE"] == "Juan Perez"


def test_cuotas_vencidas_sin_auth(client):
    response = client.get("/api/v1/clientes/cuotas/vencidas")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_cuotas_vencidas_success(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchall.return_value = [
        {
            "NPRESTAMO": 123,
            "CODIGO": 1,
            "CLIENTE": "Juan Perez",
            "FECHAP": "2026-03-15T00:00:00",
            "fechav": "2026-06-15T00:00:00",
            "cel": "8091234567",
            "ncuotas": 2,
            "deuda_al_dia": 500.00,
            "mora_total": 50.00,
            "estado_cuota": "con cuota vencida",
        }
    ]

    response = client.get("/api/v1/clientes/cuotas/vencidas", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["CLIENTE"] == "Juan Perez"
    assert data[0]["ncuotas"] == 2


def test_obtener_clientes_404(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchall.return_value = []

    response = client.get("/api/v1/clientes/", headers=auth_header)

    assert response.status_code == 404
    assert (
        "No se encontraron clientes con prestamos activos" in response.json()["detail"]
    )


def test_cuotas_vencidas_404(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchall.return_value = []

    response = client.get("/api/v1/clientes/cuotas/vencidas", headers=auth_header)

    assert response.status_code == 404
    assert "No se encontraron clientes con cuotas vencidas" in response.json()["detail"]


def test_buscar_clientes_404(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchall.return_value = []

    response = client.get(
        "/api/v1/clientes/buscar?CLIENTE=noexiste", headers=auth_header
    )

    assert response.status_code == 404
    assert (
        "No se encontraron clientes con el nombre indicado" in response.json()["detail"]
    )


def test_buscar_clientes_con_fechas(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection

    mock_cursor.fetchall.return_value = [
        {
            "idcliente": 1,
            "CLIENTE": "Juan Perez",
            "nprestamo": 123,
            "vprestamo": 1000.50,
            "FECHAP": datetime(2026, 3, 15),
            "fechav": datetime(2026, 6, 15),
            "cel": "8091234567",
            "estado_cuota": "con cuota vencida",
            "cantidad_cutas": 2,
            "deuda_al_dia": 500.00,
            "mora_total": 50.00,
            "fecha": "15-03-2026 10:00:00",
        }
    ]

    response = client.get("/api/v1/clientes/buscar?CLIENTE=juan", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["FECHAP"] == "15-03-2026"
    assert data[0]["fechav"] == "15-06-2026"
