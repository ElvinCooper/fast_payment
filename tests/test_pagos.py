import pytest
from app.auth_utils import create_access_token

@pytest.fixture
def auth_header():
    token = create_access_token(data={"sub": "testuser", "id": 1})
    return {"Authorization": f"Bearer {token}"}

def test_registrar_pago_success(client, auth_header, mock_db_conn):
    mock_conn, mock_cursor = mock_db_conn
    mock_cursor.lastrowid = 101 # Simular un ID insertado
    
    pago_data = {
        "idcliente": 724353,
        "cliente_nombre": "Elvin",
        "monto": 2500.0,
        "idusuario": 9,
        "usuario_nombre": "Andrew"
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
        "usuario_nombre": "Andrew"
    }
    
    response = client.post("/api/v1/pagos/", json=pago_data, headers=auth_header)
    
    assert response.status_code == 422
    assert "El monto del pago debe ser una cantidad mayor a cero" in response.text

def test_registrar_pago_sin_auth(client):
    response = client.post("/api/v1/pagos/", json={})
    assert response.status_code == 401
