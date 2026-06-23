"""
Shared constants, factory functions, and captured original methods for all tests.

Imported by both conftest.py (fixtures) and individual test modules.
The original PredictionService methods are captured here at import time,
BEFORE any session-level patches are applied, so unit tests can call
the real implementations when needed.
"""

import numpy as np
from unittest.mock import MagicMock

from app.services.prediction_service import PredictionService

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

MOCK_METADATA = {
    "model_name": "House Price Predictor",
    "algorithm": "Random Forest",
    "version": "v1",
    "dataset": "California Housing",
}

VALID_INPUT = {
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.9841,
    "AveBedrms": 1.0238,
    "Population": 322.0,
    "AveOccup": 2.5556,
    "Latitude": 37.88,
    "Longitude": -122.23,
}

# ---------------------------------------------------------------------------
# Capture real (unpatched) methods before the session fixture applies patches
# ---------------------------------------------------------------------------

original_load_model = PredictionService.load_model
original_load_metadata = PredictionService.load_metadata

# ---------------------------------------------------------------------------
# Factory: each call returns a fresh, independent mock sklearn model
# ---------------------------------------------------------------------------


def make_mock_model() -> MagicMock:
    """Return a new MagicMock that behaves like a fitted sklearn estimator."""
    model = MagicMock()
    model.predict.return_value = np.array([4.526])
    return model
