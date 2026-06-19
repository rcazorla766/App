import os
import joblib
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load the California housing dataset
print("Loading California Housing dataset...")
data = fetch_california_housing(as_frame=True)
df = data.frame

print(df.head())
print(f"Dataset shape: {df.shape}")
print(df.info())

# Features and target
X = df.drop(columns=["MedHouseVal"])
y = df["MedHouseVal"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a Random Forest model
print("\nTraining Random Forest model...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"\nModel evaluation:")
print(f"  RMSE : {rmse:.4f}")
print(f"  R²   : {r2:.4f}")

# Save the model
output_dir = os.path.join(os.path.dirname(__file__), "..", "app", "models")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "trained_model_v1.pkl")

joblib.dump(model, output_path)

print(f"\nModel saved to: {os.path.abspath(output_path)}")
