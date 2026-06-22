from fastapi import APIRouter, Request

from app.schemas.model import ModelInformationResponse

#create a router for prediction endpoints
router = APIRouter()

#the endpoint
@router.get(
    "/model",
    response_model=ModelInformationResponse,
    tags=["Model"]
)
def get_model_information(request: Request):

    prediction_service = request.app.state.prediction_service

    metadata = prediction_service.get_model_metadata()

    return ModelInformationResponse(**metadata)