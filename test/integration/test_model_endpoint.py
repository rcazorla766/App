"""
Integration tests for GET /model.

Verifies that the model-information endpoint returns the correct HTTP status,
a well-formed JSON body matching ModelInformationResponse, and that it
delegates to PredictionService.get_model_metadata().
"""

from helpers import MOCK_METADATA


class TestModelEndpoint:
    def test_returns_200(self, client):
        response = client.get("/model")
        assert response.status_code == 200

    def test_content_type_is_json(self, client):
        response = client.get("/model")
        assert "application/json" in response.headers["content-type"]

    def test_response_schema_has_exactly_four_fields(self, client):
        expected_keys = {"model_name", "algorithm", "version", "dataset"}
        assert set(client.get("/model").json().keys()) == expected_keys

    def test_model_name_matches_metadata(self, client):
        assert client.get("/model").json()["model_name"] == MOCK_METADATA["model_name"]

    def test_algorithm_matches_metadata(self, client):
        assert client.get("/model").json()["algorithm"] == MOCK_METADATA["algorithm"]

    def test_version_matches_metadata(self, client):
        assert client.get("/model").json()["version"] == MOCK_METADATA["version"]

    def test_dataset_matches_metadata(self, client):
        assert client.get("/model").json()["dataset"] == MOCK_METADATA["dataset"]

    def test_all_fields_are_strings(self, client):
        data = client.get("/model").json()
        for key in ("model_name", "algorithm", "version", "dataset"):
            assert isinstance(data[key], str), f"Field '{key}' is not a string"

    def test_delegates_to_prediction_service(self, client_with_mock):
        client, mock_svc = client_with_mock
        client.get("/model")
        mock_svc.get_model_metadata.assert_called_once()

    def test_method_not_allowed_for_post(self, client):
        response = client.post("/model")
        assert response.status_code == 405
