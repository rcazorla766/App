"""
Integration tests for health endpoints.

Verifies liveness (/health) and readiness (/ready).
"""

from helpers import MOCK_METADATA


class TestHealthEndpoint:
    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_content_type_is_json(self, client):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

    def test_status_field_is_healthy(self, client):
        response = client.get("/health")
        assert response.json()["status"] == "healthy"

    def test_response_has_exactly_one_field(self, client):
        response = client.get("/health")
        assert set(response.json().keys()) == {"status"}

    def test_method_not_allowed_for_post(self, client):
        response = client.post("/health")
        assert response.status_code == 405


class TestReadyEndpoint:
    def test_returns_200(self, client):
        response = client.get("/ready")
        assert response.status_code == 200

    def test_status_is_ready(self, client):
        response = client.get("/ready")
        assert response.json()["status"] == "ready"

    def test_model_loaded_is_true(self, client):
        response = client.get("/ready")
        assert response.json()["model_loaded"] is True

    def test_model_version_matches_metadata(self, client):
        response = client.get("/ready")
        assert response.json()["model_version"] == MOCK_METADATA["version"]

    def test_method_not_allowed_for_post(self, client):
        response = client.post("/ready")
        assert response.status_code == 405
