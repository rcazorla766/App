import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_MODEL_PATH = BASE_DIR / "models" / "trained_model_v1.pkl"
DEFAULT_METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

MODEL_PATH = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
MODEL_METADATA_PATH = Path(os.getenv("MODEL_METADATA_PATH", str(DEFAULT_METADATA_PATH)))

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
