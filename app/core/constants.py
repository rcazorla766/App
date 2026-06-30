"""Shared ML constants used by training and inference."""

FEATURE_NAMES = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]

TARGET_NAME = "MedHouseVal"

MODEL_NAME = "House Price Predictor"
ALGORITHM = "Random Forest"
MODEL_VERSION = "v1"
DATASET_NAME = "California Housing"
