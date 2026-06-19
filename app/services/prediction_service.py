from pathlib import Path
import joblib
import json

# Define paths for the model and metadata
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "trained_model_v1.pkl"
MODEL_METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

class PredictionService:
    def __init__(self, model_path: str = MODEL_PATH):
        # Initialize the PredictionService with the path to the trained model
        self.model_path = Path(model_path)
        self.metadata_path = Path(MODEL_METADATA_PATH)
        self.model = self.load_model()
        self.metadata = self.load_metadata()

    def load_model(self):
        # Load the trained model from the specified path
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        return joblib.load(self.model_path)

    def load_metadata(self):
        if not self.metadata_path.exists():
            return {}
        with open(self.metadata_path, "r") as f:
            return json.load(f)

    def predict(self, input_data: dict):
        # Convert input data to the appropriate format for prediction
        input_array = self._prepare_input(input_data)
        prediction = self.model.predict(input_array)
        return prediction.tolist()

    def _prepare_input(self, input_data: dict):
        # Convert the input dictionary to a 2D array (list of lists)
        # Assuming the model expects a specific order of features
        feature_order = [
            "MedInc", "HouseAge", "AveRooms", "AveBedrms",
            "Population", "AveOccup", "Latitude", "Longitude"
        ]
        input_array = [[input_data[feature] for feature in feature_order]]
        return input_array
    
    def get_model_metadata(self):
        return self.metadata

    def reload_model(self):
        # Reload the model from the file system
        self.model = self.load_model()
        self.metadata = self.load_metadata()