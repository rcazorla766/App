from pathlib import Path

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.services.prediction_service import PredictionService

#Service initialization
prediction_service = PredictionService()

app = FastAPI(
    title="AI Model Governance API",
    description="REST API for Machine Learning model governance using GitOps.",
    version="0.1.0"
)

app.state.prediction_service = prediction_service

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "message": "AI Model Governance API",
        "version": "0.1.0",
        "model": prediction_service.get_model_metadata()
    }