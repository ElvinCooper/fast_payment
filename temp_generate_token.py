from app.auth_utils import create_access_token

# Generar token para pruebas
token = create_access_token(data={"sub": "testuser", "id": "1"})
print(f"Token: {token}")