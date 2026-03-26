import pytest
from app.auth_utils import create_access_token
from unittest.mock import patch
from io import BytesIO


@pytest.fixture
def auth_header():
    token = create_access_token(data={"sub": "testuser", "id": 1})
    return {"Authorization": f"Bearer {token}"}


def test_registrar_pago_success(client, auth_header, mock_user_connection):
    mock_conn, mock_cursor = mock_user_connection
    mock_cursor.lastrowid = 101  # Simular un ID insertado

    # Mockear la respuesta del query de validación
    mock_cursor.fetchone.return_value = (10000.0, 5000.0, 500.0)  # vprestamo, deuda_al_dia, mora_total

    pago_data = {
        "idcliente": 724353,
        "cliente_nombre": "Elvin",
        "monto": 2500.0,
        "idprestamo": 1,
        "idusuario": 9,
        "usuario_nombre": "Andrew",
    }

    response = client.post("/api/v1/pagos/", json=pago_data, headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Pago registrado exitosamente"
    assert data["idpago"] == 101


def test_registrar_pago_monto_invalido(client, auth_header):
    # Probar el validador personalizado (monto <= 0)
    pago_data = {
        "idcliente": 724353,
        "cliente_nombre": "Elvin",
        "monto": 0,
        "idusuario": 9,
        "usuario_nombre": "Andrew",
    }

    response = client.post("/api/v1/pagos/", json=pago_data, headers=auth_header)

    assert response.status_code == 422
    assert "El monto del pago debe ser una cantidad mayor a cero" in response.text


def test_registrar_pago_sin_auth(client):
    response = client.post("/api/v1/pagos/", json={})
    assert response.status_code == 401


def test_generar_recibo_pdf_success(client):
    """Test para generar recibo en PDF"""
    mock_pdf = BytesIO(b"PDF content")

    with patch("app.routers.pagos.generar_recibo_termico") as mock_gen:
        mock_gen.return_value = mock_pdf

        recibo_data = {
            "cliente": "Juan Perez",
            "monto": 2500.00,
            "atendido_por": "Cajero Admin",
        }

        response = client.post("/api/v1/pagos/recibo", json=recibo_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment; filename=recibo_" in response.headers["content-disposition"]


def test_registrar_pago_monto_excede_deuda(client, auth_header, mock_user_connection):
    """Test cuando el monto del pago excede la deuda total"""
    mock_conn, mock_cursor = mock_user_connection

    # Mockear la respuesta del query de validación
    mock_cursor.fetchone.return_value = (10000.0, 5000.0, 500.0)  # vprestamo, deuda_al_dia, mora_total

    # Mockear el lastrowid para que el test no falle si pasa la validación (aunque no debería pasar)
    mock_cursor.lastrowid = 101

    pago_data = {
        "idcliente": 724353,
        "cliente_nombre": "Elvin",
        "monto": 6000.0,  # Excede la deuda total de 5500.0
        "idprestamo": 1,
        "idusuario": 9,
        "usuario_nombre": "Andrew",
    }

    response = client.post("/api/v1/pagos/", json=pago_data, headers=auth_header)

    assert response.status_code == 400
    assert "El monto del pago" in response.json()["detail"]
    assert "excede la deuda total" in response.json()["detail"]
    assert "Deuda actual: $5000.00" in response.json()["detail"]
    assert "Mora: $500.00" in response.json()["detail"]
    assert "Total deuda: $5500.00" in response.json()["detail"]


def test_generar_recibo_pdf_error(client):
    """Test para manejar error al generar PDF"""
    with patch(
        "app.routers.pagos.generar_recibo_termico",
        side_effect=Exception("Error generando PDF"),
    ):
        recibo_data = {
            "cliente": "Juan Perez",
            "monto": 2500.00,
            "atendido_por": "Cajero Admin",
        }

        response = client.post("/api/v1/pagos/recibo", json=recibo_data)

        assert response.status_code == 500
        assert "Error al generar comprobante" in response.json()["detail"]
