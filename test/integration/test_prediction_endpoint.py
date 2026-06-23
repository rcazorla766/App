"""
Integration tests for POST /predict.

Covers happy-path responses, response schema validation, input validation
(missing fields, wrong types), and delegation to PredictionService.predict().
"""

import pytest

from helpers import VALID_INPUT


class TestPredictEndpoint:
    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_valid_input_returns_200(self, client):
        response = client.post("/predict", json=VALID_INPUT)
        assert response.status_code == 200

    def test_response_contains_prediction_field(self, client):
        data = client.post("/predict", json=VALID_INPUT).json()
        assert "prediction" in data

    def test_response_contains_model_version_field(self, client):
        data = client.post("/predict", json=VALID_INPUT).json()
        assert "model_version" in data

    def test_response_schema_has_exactly_two_fields(self, client):
        data = client.post("/predict", json=VALID_INPUT).json()
        assert set(data.keys()) == {"prediction", "model_version"}

    def test_prediction_is_numeric(self, client):
        data = client.post("/predict", json=VALID_INPUT).json()
        assert isinstance(data["prediction"], (int, float))

    def test_model_version_is_string(self, client):
        data = client.post("/predict", json=VALID_INPUT).json()
        assert isinstance(data["model_version"], str)

    def test_model_version_matches_metadata(self, client):
        data = client.post("/predict", json=VALID_INPUT).json()
        assert data["model_version"] == "v1"

    # ------------------------------------------------------------------
    # Input validation (422 Unprocessable Entity)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("missing_field", list(VALID_INPUT.keys()))
    def test_missing_field_returns_422(self, client, missing_field):
        data = dict(VALID_INPUT)
        del data[missing_field]
        response = client.post("/predict", json=data)
        assert response.status_code == 422

    def test_non_numeric_medinc_returns_422(self, client):
        data = dict(VALID_INPUT)
        data["MedInc"] = "not_a_number"
        response = client.post("/predict", json=data)
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client):
        response = client.post("/predict", json={})
        assert response.status_code == 422

    def test_null_field_returns_422(self, client):
        data = dict(VALID_INPUT)
        data["Latitude"] = None
        response = client.post("/predict", json=data)
        assert response.status_code == 422

    # ------------------------------------------------------------------
    # Service delegation
    # ------------------------------------------------------------------

    def test_prediction_service_is_called(self, client_with_mock):
        client, mock_svc = client_with_mock
        client.post("/predict", json=VALID_INPUT)
        mock_svc.predict.assert_called_once()

    def test_service_receives_all_eight_features(self, client_with_mock):
        client, mock_svc = client_with_mock
        client.post("/predict", json=VALID_INPUT)
        payload_passed = mock_svc.predict.call_args[0][0]
        assert set(payload_passed.keys()) == set(VALID_INPUT.keys())

    def test_service_receives_correct_values(self, client_with_mock):
        client, mock_svc = client_with_mock
        client.post("/predict", json=VALID_INPUT)
        payload_passed = mock_svc.predict.call_args[0][0]
        assert payload_passed == VALID_INPUT

    def test_prediction_value_comes_from_service(self, client_with_mock):
        client, mock_svc = client_with_mock
        mock_svc.predict.return_value = [7.777]
        data = client.post("/predict", json=VALID_INPUT).json()
        assert data["prediction"] == pytest.approx(7.777)

    # ------------------------------------------------------------------
    # Wrong HTTP method
    # ------------------------------------------------------------------

    def test_get_method_not_allowed(self, client):
        response = client.get("/predict")
        assert response.status_code == 405
