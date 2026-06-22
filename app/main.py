from pathlib import Path

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.prediction import router as prediction_router
from app.api.routes.model import router as model_router

from app.services.prediction_service import PredictionService


#Service initialization
prediction_service = PredictionService()


app = FastAPI(
    title="AI Model Governance API",
    description="REST API for Machine Learning model governance using GitOps.",
    version="0.1.0"
)

app.state.prediction_service = prediction_service

#include the routers for health and prediction endpoints
app.include_router(health_router)
app.include_router(prediction_router)
app.include_router(model_router)

@app.get("/")
def root():
    return {
        "message": "AI Model Governance API",
        "version": "0.1.0",
        "model": prediction_service.get_model_metadata()
    }