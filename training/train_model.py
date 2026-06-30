import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.constants import (  # noqa: E402
    ALGORITHM,
    DATASET_NAME,
    FEATURE_NAMES,
    MODEL_NAME,
    MODEL_VERSION,
    TARGET_NAME,
)

OUTPUT_DIR = PROJECT_ROOT / "app" / "models"
MODEL_FILENAME = f"trained_model_{MODEL_VERSION}.pkl"
METADATA_FILENAME = "model_metadata.json"


def train_and_save_model() -> None:
    print("Loading California Housing dataset...")
    data = fetch_california_housing(as_frame=True)
    dataframe = data.frame

    print(dataframe.head())
    print(f"Dataset shape: {dataframe.shape}")

    features = dataframe[FEATURE_NAMES]
    target = dataframe[TARGET_NAME]

    train_features, test_features, train_target, test_target = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    print("\nTraining Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train_features, train_target)

    predictions = model.predict(test_features)
    rmse = float(np.sqrt(mean_squared_error(test_target, predictions)))
    r2 = float(r2_score(test_target, predictions))

    print("\nModel evaluation:")
    print(f"  RMSE : {rmse:.4f}")
    print(f"  R²   : {r2:.4f}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = OUTPUT_DIR / MODEL_FILENAME
    metadata_path = OUTPUT_DIR / METADATA_FILENAME

    joblib.dump(model, model_path)

    metadata = {
        "model_name": MODEL_NAME,
        "algorithm": ALGORITHM,
        "version": MODEL_VERSION,
        "dataset": DATASET_NAME,
        "features": FEATURE_NAMES,
        "metrics": {
            "rmse": rmse,
            "r2": r2,
        },
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "artifact_path": MODEL_FILENAME,
    }

    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    print(f"\nModel saved to: {model_path.resolve()}")
    print(f"Metadata saved to: {metadata_path.resolve()}")


if __name__ == "__main__":
    train_and_save_model()
