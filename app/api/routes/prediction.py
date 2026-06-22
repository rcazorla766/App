from fastapi import APIRouter, Request

from app.schemas.prediction import PredictionRequest
from app.schemas.prediction import PredictionResponse

#create a router for prediction endpoints
router = APIRouter()

#the endpoint
@router.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Prediction"]
)
def predict(
    prediction_request: PredictionRequest,
    request: Request
):
    #get the prediction service from the app state
    prediction_service = request.app.state.prediction_service

    #make a prediction using the service
    #prediction = prediction_service.predict(prediction_request.dict())
    prediction = prediction_service.predict(prediction_request.model_dump())  # Use model_dump() to convert to dict if using Pydantic v2

    #get model metadata
    model_metadata = prediction_service.get_model_metadata()
    model_version = model_metadata.get("version", "unknown")

    #return the prediction and model version
    return PredictionResponse(
        prediction=prediction[0],
        model_version=model_version
    )