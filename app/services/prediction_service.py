import json
from pathlib import Path

import joblib

from app.core.config import MODEL_METADATA_PATH, MODEL_PATH
from app.core.constants import FEATURE_NAMES


class PredictionService:
    def __init__(
        self,
        model_path: Path | str | None = None,
        metadata_path: Path | str | None = None,
    ):
        self.model_path = Path(model_path or MODEL_PATH)
        self.metadata_path = Path(metadata_path or MODEL_METADATA_PATH)
        self.model = self.load_model()
        self.metadata = self.load_metadata()

    def load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        return joblib.load(self.model_path)

    def load_metadata(self):
        if not self.metadata_path.exists():
            return {}
        with open(self.metadata_path, encoding="utf-8") as metadata_file:
            return json.load(metadata_file)

    def predict(self, input_data: dict):
        input_array = self._prepare_input(input_data)
        prediction = self.model.predict(input_array)
        return prediction.tolist()

    def _prepare_input(self, input_data: dict):
        return [[input_data[feature] for feature in FEATURE_NAMES]]

    def get_model_metadata(self):
        return self.metadata

    def is_ready(self) -> bool:
        return self.model is not None and bool(self.metadata)

    def reload_model(self):
        self.model = self.load_model()
        self.metadata = self.load_metadata()
