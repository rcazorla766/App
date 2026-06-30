"""
Unit tests for PredictionService.

Each test class covers one method.  The session-level patch in conftest.py
replaces load_model / load_metadata with lambdas, so PredictionService() can
be instantiated without a model file on disk.

For tests that need the *real* load_model / load_metadata implementations,
the unpatched originals are imported from helpers.py and temporarily
restored via patch.object.
"""

import json
import joblib
import numpy as np
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from sklearn.dummy import DummyRegressor

from app.services.prediction_service import PredictionService
from helpers import MOCK_METADATA, VALID_INPUT, original_load_model, original_load_metadata


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    def test_model_attribute_is_set(self):
        service = PredictionService()
        assert service.model is not None

    def test_metadata_attribute_is_set(self):
        service = PredictionService()
        assert service.metadata is not None

    def test_metadata_matches_mock(self):
        service = PredictionService()
        assert service.metadata == MOCK_METADATA

    def test_model_path_is_path_object(self):
        service = PredictionService()
        assert isinstance(service.model_path, Path)

    def test_metadata_path_is_path_object(self):
        service = PredictionService()
        assert isinstance(service.metadata_path, Path)


# ---------------------------------------------------------------------------
# load_model  (tests use the real, unpatched implementation)
# ---------------------------------------------------------------------------


class TestLoadModel:
    def test_raises_when_model_file_is_missing(self, tmp_path):
        """Real load_model raises FileNotFoundError for a non-existent pkl."""
        service = PredictionService()
        service.model_path = tmp_path / "missing.pkl"

        with patch.object(PredictionService, "load_model", original_load_model):
            with pytest.raises(FileNotFoundError, match="Model file not found"):
                service.load_model()

    def test_loads_model_successfully(self, tmp_path):
        """Real load_model returns an object when a valid pkl file exists."""
        model_obj = DummyRegressor()
        model_obj.fit([[0]], [0])
        model_path = tmp_path / "model.pkl"
        joblib.dump(model_obj, model_path)

        service = PredictionService()
        service.model_path = model_path

        with patch.object(PredictionService, "load_model", original_load_model):
            result = service.load_model()

        assert result is not None


# ---------------------------------------------------------------------------
# load_metadata  (tests use the real, unpatched implementation)
# ---------------------------------------------------------------------------


class TestLoadMetadata:
    def test_returns_empty_dict_when_file_is_missing(self, tmp_path):
        """Real load_metadata returns {} when the JSON file does not exist."""
        service = PredictionService()
        service.metadata_path = tmp_path / "missing_metadata.json"

        with patch.object(PredictionService, "load_metadata", original_load_metadata):
            result = service.load_metadata()

        assert result == {}

    def test_parses_json_correctly(self, tmp_path):
        """Real load_metadata returns the parsed contents of the JSON file."""
        metadata_path = tmp_path / "metadata.json"
        metadata_path.write_text(json.dumps(MOCK_METADATA), encoding="utf-8")

        service = PredictionService()
        service.metadata_path = metadata_path

        with patch.object(PredictionService, "load_metadata", original_load_metadata):
            result = service.load_metadata()

        assert result == MOCK_METADATA

    def test_returned_metadata_contains_all_keys(self, tmp_path):
        metadata_path = tmp_path / "metadata.json"
        metadata_path.write_text(json.dumps(MOCK_METADATA), encoding="utf-8")

        service = PredictionService()
        service.metadata_path = metadata_path

        with patch.object(PredictionService, "load_metadata", original_load_metadata):
            result = service.load_metadata()

        assert set(result.keys()) == {"model_name", "algorithm", "version", "dataset"}


# ---------------------------------------------------------------------------
# _prepare_input
# ---------------------------------------------------------------------------


class TestPrepareInput:
    def test_returns_2d_list(self):
        service = PredictionService()
        result = service._prepare_input(VALID_INPUT)
        assert isinstance(result, list)
        assert isinstance(result[0], list)

    def test_outer_list_has_one_row(self):
        service = PredictionService()
        result = service._prepare_input(VALID_INPUT)
        assert len(result) == 1

    def test_row_has_eight_features(self):
        service = PredictionService()
        result = service._prepare_input(VALID_INPUT)
        assert len(result[0]) == 8

    def test_feature_order_matches_model_expectation(self):
        """Features must appear in the exact order the model was trained with."""
        service = PredictionService()
        result = service._prepare_input(VALID_INPUT)
        expected = [
            VALID_INPUT["MedInc"],
            VALID_INPUT["HouseAge"],
            VALID_INPUT["AveRooms"],
            VALID_INPUT["AveBedrms"],
            VALID_INPUT["Population"],
            VALID_INPUT["AveOccup"],
            VALID_INPUT["Latitude"],
            VALID_INPUT["Longitude"],
        ]
        assert result[0] == expected


# ---------------------------------------------------------------------------
# predict
# ---------------------------------------------------------------------------


class TestPredict:
    def test_returns_list(self):
        service = PredictionService()
        result = service.predict(VALID_INPUT)
        assert isinstance(result, list)

    def test_returns_single_value(self):
        service = PredictionService()
        result = service.predict(VALID_INPUT)
        assert len(result) == 1

    def test_returned_value_is_numeric(self):
        service = PredictionService()
        result = service.predict(VALID_INPUT)
        assert isinstance(result[0], (int, float))

    def test_calls_model_predict_once(self):
        service = PredictionService()
        service.predict(VALID_INPUT)
        service.model.predict.assert_called_once()

    def test_model_receives_correctly_shaped_input(self):
        """The mock model must be called with a 2-D list of one row."""
        service = PredictionService()
        service.predict(VALID_INPUT)
        call_args = service.model.predict.call_args[0][0]
        assert len(call_args) == 1
        assert len(call_args[0]) == 8


# ---------------------------------------------------------------------------
# get_model_metadata
# ---------------------------------------------------------------------------


class TestGetModelMetadata:
    def test_returns_dict(self):
        service = PredictionService()
        assert isinstance(service.get_model_metadata(), dict)

    def test_returns_correct_metadata(self):
        service = PredictionService()
        assert service.get_model_metadata() == MOCK_METADATA

    def test_contains_required_keys(self):
        service = PredictionService()
        metadata = service.get_model_metadata()
        for key in ("model_name", "algorithm", "version", "dataset"):
            assert key in metadata


# ---------------------------------------------------------------------------
# reload_model
# ---------------------------------------------------------------------------


class TestReloadModel:
    def test_reload_replaces_model(self):
        service = PredictionService()
        new_model = MagicMock()
        new_model.predict.return_value = np.array([9.99])

        with patch.object(PredictionService, "load_model", lambda self: new_model):
            service.reload_model()

        assert service.model is new_model

    def test_reload_replaces_metadata(self):
        service = PredictionService()
        new_metadata = {
            "model_name": "v2",
            "algorithm": "XGBoost",
            "version": "v2",
            "dataset": "test",
        }

        with patch.object(PredictionService, "load_metadata", lambda self: new_metadata):
            service.reload_model()

        assert service.metadata == new_metadata

    def test_reload_calls_both_loaders(self):
        service = PredictionService()
        load_model_calls = []
        load_metadata_calls = []

        def track_load_model(self):
            load_model_calls.append(1)
            return MagicMock()

        def track_load_metadata(self):
            load_metadata_calls.append(1)
            return {}

        with patch.object(PredictionService, "load_model", track_load_model), \
                patch.object(PredictionService, "load_metadata", track_load_metadata):
            service.reload_model()

        assert len(load_model_calls) == 1
        assert len(load_metadata_calls) == 1


# ---------------------------------------------------------------------------
# is_ready
# ---------------------------------------------------------------------------


class TestIsReady:
    def test_returns_true_when_model_and_metadata_exist(self):
        service = PredictionService()
        assert service.is_ready() is True
