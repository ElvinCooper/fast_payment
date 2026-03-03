import pytest
from app.auth_utils import create_access_token

@pytest.fixture
def auth_header():
    token = create_access_token(data={"sub": "testuser", "id": 1})
    return {"Authorization": f"Bearer {token}"}

def test_registrar_pago_success(client, auth_header):
    pago_data = {
        "idcliente": 1,
        "monto": 500.0,
        "fecha": "2024-03-03"
    }
    
    response = client.post("/api/v1/pagos/", json=pago_data, headers=auth_header)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Pago registrado correctamente"

def test_registrar_pago_sin_auth(client):
    response = client.post("/api/v1/pagos/", json={})
    assert response.status_code == 401
