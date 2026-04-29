from pathlib import Path
import joblib
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
INPUT_PATH = Path("data/final/shipments_featured.csv")
MODEL_PATH = Path("models/delay_risk_model.pkl")
OUTPUT_PATH = Path("data/final/shipments_scored.csv")

# --------------------------------------------------
# Config
# --------------------------------------------------
CATEGORICAL_FEATURES = [
    "vehicle_type",
    "shipment_priority",
    "product_category",
    "weather_main",
]

NUMERIC_FEATURES = [
    "load_weight_kg",
    "volume_m3",
    "base_shipping_cost",
    "route_distance_km",
    "estimated_travel_time_min",
    "temperature_c",
    "precipitation_mm",
    "wind_speed_kmh",
    "is_high_priority",
]

FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# --------------------------------------------------
# Functions
# --------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def load_model(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


def main() -> None:
    df = load_data(INPUT_PATH)
    model = load_model(MODEL_PATH)

    missing_cols = [col for col in FEATURES if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    X = df[FEATURES]

    df["predicted_is_delayed"] = model.predict(X)
    df["delay_risk_score"] = model.predict_proba(X)[:, 1]

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nDelay scoring completed.")
    print(f"Scored dataset saved to: {OUTPUT_PATH}")
    print("\nPrediction distribution:")
    print(df["predicted_is_delayed"].value_counts(dropna=False))
    print("\nDelay risk score summary:")
    print(df["delay_risk_score"].describe())


if __name__ == "__main__":
    main()