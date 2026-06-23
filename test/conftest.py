"""
Root test configuration and shared fixtures.

A session-scoped autouse fixture patches PredictionService.load_model and
PredictionService.load_metadata before app.main is imported for the first
time, so that the tests can run without a trained model file on disk.
"""

import pytest
from unittest.mock import MagicMock, patch

from helpers import MOCK_METADATA, make_mock_model


# ---------------------------------------------------------------------------
# Session-level patch: allows app.main to be imported without model on disk
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def patched_app():
    """
    Patch PredictionService so app.main can be imported safely.
    Yields the FastAPI application instance for use by other fixtures.
    """
    with patch.multiple(
        "app.services.prediction_service.PredictionService",
        load_model=lambda self: make_mock_model(),
        load_metadata=lambda self: dict(MOCK_METADATA),
    ):
        from app.main import app  # deferred: patches are active at this point
        yield app


# ---------------------------------------------------------------------------
# Reusable fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client(patched_app):
    """TestClient connected to the FastAPI application."""
    from fastapi.testclient import TestClient

    with TestClient(patched_app) as c:
        yield c


@pytest.fixture
def mock_service():
    """Fully-controlled MagicMock replacement for PredictionService."""
    svc = MagicMock()
    svc.predict.return_value = [4.526]
    svc.get_model_metadata.return_value = dict(MOCK_METADATA)
    return svc


@pytest.fixture
def client_with_mock(patched_app, mock_service):
    """
    TestClient with a controllable mock injected into app.state.
    Yields (client, mock_service) so tests can assert on mock calls.
    Restores the original service after each test.
    """
    from fastapi.testclient import TestClient

    original = patched_app.state.prediction_service
    patched_app.state.prediction_service = mock_service
    with TestClient(patched_app) as c:
        yield c, mock_service
    patched_app.state.prediction_service = original
