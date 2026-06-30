from fastapi import APIRouter, Request

router = APIRouter()
 

@router.get("/health", tags=["Health"])
def health():
    """
    Liveness probe: confirms the API process is running.
    """
    return {"status": "healthy"}


@router.get("/ready", tags=["Health"])
def ready(request: Request):
    """
    Readiness probe: confirms the model and metadata are loaded.
    """
    prediction_service = request.app.state.prediction_service
    model_loaded = prediction_service.model is not None

    if not model_loaded:
        return {"status": "not_ready", "model_loaded": False}

    return {
        "status": "ready",
        "model_loaded": True,
        "model_version": prediction_service.get_model_metadata().get("version", "unknown"),
    }
