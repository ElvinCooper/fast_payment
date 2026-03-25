import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestSecurityHeaders:
    def test_x_content_type_options_header(self, client: TestClient):
        response = client.get("/")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_strict_transport_security_header(self, client: TestClient):
        response = client.get("/")
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=" in response.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in response.headers["Strict-Transport-Security"]

    def test_security_headers_on_protected_endpoint(
        self,
        client: TestClient,
        mock_user_connection,
        mock_pg_conn,
        mock_token_not_revoked,
    ):
        from app.auth_utils import create_access_token

        token = create_access_token(data={"sub": "test", "id": 1})
        response = client.get(
            "/api/v1/usuarios", headers={"Authorization": f"Bearer {token}"}
        )
        assert "X-Content-Type-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers
