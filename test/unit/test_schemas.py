"""
Unit tests for Pydantic schemas:
  - PredictionRequest
  - PredictionResponse
  - ModelInformationResponse

These tests verify field validation, type coercion, and serialisation
behaviour without starting the FastAPI application.
"""

import pytest
from pydantic import ValidationError

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.schemas.model import ModelInformationResponse
from helpers import MOCK_METADATA, VALID_INPUT


# ---------------------------------------------------------------------------
# PredictionRequest
# ---------------------------------------------------------------------------


class TestPredictionRequest:
    def test_valid_input_is_accepted(self):
        req = PredictionRequest(**VALID_INPUT)
        assert req.MedInc == VALID_INPUT["MedInc"]

    def test_all_field_values_are_stored(self):
        req = PredictionRequest(**VALID_INPUT)
        for field, value in VALID_INPUT.items():
            assert getattr(req, field) == value

    def test_integer_values_are_coerced_to_float(self):
        data = dict(VALID_INPUT)
        data["HouseAge"] = 41  # int → should coerce to float
        req = PredictionRequest(**data)
        assert isinstance(req.HouseAge, float)

    @pytest.mark.parametrize("missing_field", list(VALID_INPUT.keys()))
    def test_missing_required_field_raises_validation_error(self, missing_field):
        data = dict(VALID_INPUT)
        del data[missing_field]
        with pytest.raises(ValidationError):
            PredictionRequest(**data)

    def test_non_numeric_string_raises_validation_error(self):
        data = dict(VALID_INPUT)
        data["MedInc"] = "not_a_number"
        with pytest.raises(ValidationError):
            PredictionRequest(**data)

    def test_none_value_raises_validation_error(self):
        data = dict(VALID_INPUT)
        data["Latitude"] = None
        with pytest.raises(ValidationError):
            PredictionRequest(**data)

    def test_model_dump_returns_all_fields(self):
        req = PredictionRequest(**VALID_INPUT)
        dumped = req.model_dump()
        assert isinstance(dumped, dict)
        assert set(dumped.keys()) == set(VALID_INPUT.keys())

    def test_model_dump_preserves_values(self):
        req = PredictionRequest(**VALID_INPUT)
        dumped = req.model_dump()
        for field, value in VALID_INPUT.items():
            assert dumped[field] == value

    def test_extra_fields_are_ignored(self):
        """Pydantic v2 ignores extra fields by default (no ValidationError)."""
        data = dict(VALID_INPUT)
        data["extra_unknown_field"] = 999
        # Should not raise; extra fields are silently ignored
        req = PredictionRequest(**data)
        assert not hasattr(req, "extra_unknown_field")


# ---------------------------------------------------------------------------
# PredictionResponse
# ---------------------------------------------------------------------------


class TestPredictionResponse:
    def test_valid_response_is_created(self):
        resp = PredictionResponse(prediction=4.526, model_version="v1")
        assert resp.prediction == 4.526
        assert resp.model_version == "v1"

    def test_missing_prediction_raises_validation_error(self):
        with pytest.raises(ValidationError):
            PredictionResponse(model_version="v1")

    def test_missing_model_version_raises_validation_error(self):
        with pytest.raises(ValidationError):
            PredictionResponse(prediction=4.526)

    def test_empty_model_raises_validation_error(self):
        with pytest.raises(ValidationError):
            PredictionResponse()

    def test_integer_prediction_coerced_to_float(self):
        resp = PredictionResponse(prediction=4, model_version="v1")
        assert isinstance(resp.prediction, float)

    def test_prediction_value_is_stored_correctly(self):
        resp = PredictionResponse(prediction=1.23, model_version="v2")
        assert resp.prediction == pytest.approx(1.23)

    def test_model_version_is_string(self):
        resp = PredictionResponse(prediction=4.526, model_version="v1")
        assert isinstance(resp.model_version, str)


# ---------------------------------------------------------------------------
# ModelInformationResponse
# ---------------------------------------------------------------------------


class TestModelInformationResponse:
    def test_valid_response_is_created(self):
        resp = ModelInformationResponse(**MOCK_METADATA)
        assert resp.model_name == MOCK_METADATA["model_name"]
        assert resp.algorithm == MOCK_METADATA["algorithm"]
        assert resp.version == MOCK_METADATA["version"]
        assert resp.dataset == MOCK_METADATA["dataset"]

    @pytest.mark.parametrize("missing_field", list(MOCK_METADATA.keys()))
    def test_missing_required_field_raises_validation_error(self, missing_field):
        data = dict(MOCK_METADATA)
        del data[missing_field]
        with pytest.raises(ValidationError):
            ModelInformationResponse(**data)

    def test_all_fields_are_strings(self):
        resp = ModelInformationResponse(**MOCK_METADATA)
        assert isinstance(resp.model_name, str)
        assert isinstance(resp.algorithm, str)
        assert isinstance(resp.version, str)
        assert isinstance(resp.dataset, str)

    def test_schema_has_exactly_four_fields(self):
        resp = ModelInformationResponse(**MOCK_METADATA)
        dumped = resp.model_dump()
        assert set(dumped.keys()) == {"model_name", "algorithm", "version", "dataset"}
