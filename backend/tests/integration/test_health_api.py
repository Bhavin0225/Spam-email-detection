import pytest
from fastapi.testclient import TestClient
from tests.conftest import DB_AVAILABLE

def test_health_endpoint_status(client: TestClient):
    """
    Verifies that the GET /health route behaves correctly based on database availability.
    - If database is connected: returns 200 OK and status is 'connected'
    - If database is disconnected: returns 503 Service Unavailable
    """
    response = client.get("/health")
    
    if DB_AVAILABLE:
        assert response.status_code == 200
        body = response.json()
        assert "status" in body
        assert "database" in body
        assert body["status"] == "ok"
        assert body["database"] == "connected"
    else:
        assert response.status_code == 503
        body = response.json()
        assert "detail" in body
        assert body["detail"] == "Database connection is unavailable."
