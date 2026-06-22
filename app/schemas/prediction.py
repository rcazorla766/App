from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    MedInc: float = Field(..., description="Median income")
    HouseAge: float = Field(..., description="Median house age")
    AveRooms: float = Field(..., description="Average number of rooms")
    AveBedrms: float = Field(..., description="Average number of bedrooms")
    Population: float = Field(..., description="Population")
    AveOccup: float = Field(..., description="Average occupancy")
    Latitude: float = Field(..., description="Latitude")
    Longitude: float = Field(..., description="Longitude")

class PredictionResponse(BaseModel):
    prediction: float = Field(...,description="Predicted house price")

    model_version: str = Field(...,description="Model version used for prediction")