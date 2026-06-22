from pydantic import BaseModel

class ModelInformationResponse(BaseModel):
    model_name: str
    algorithm: str
    version: str
    dataset: str