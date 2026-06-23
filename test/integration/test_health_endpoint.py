"""
Integration tests for GET /health.

Verifies that the health-check endpoint is reachable, returns the correct
HTTP status code, and produces the expected JSON response body.
"""


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
