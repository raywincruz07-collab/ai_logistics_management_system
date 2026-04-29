from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# --------------------------------------------------
# Paths
# --------------------------------------------------
INPUT_PATH = Path("data/final/shipments_featured.csv")
MODEL_DIR = Path("models")
REPORTS_DIR = Path("reports")
PREDICTIONS_PATH = Path("data/final/delay_predictions.csv")
MODEL_PATH = MODEL_DIR / "delay_risk_model.pkl"
METRICS_PATH = REPORTS_DIR / "delay_model_metrics.txt"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Config
# --------------------------------------------------
TARGET = "is_delayed"

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


def build_pipeline() -> Pipeline:
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    from sklearn.preprocessing import StandardScaler

    numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("num", numeric_transformer, NUMERIC_FEATURES),
        ]
    )

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=42
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    return pipeline


def save_metrics(y_train, y_test, y_pred) -> None:
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        f.write("Delay Risk Model Metrics\n")
        f.write("========================\n\n")
        f.write("Train class distribution:\n")
        f.write(str(y_train.value_counts().sort_index()))
        f.write("\n\n")
        f.write("Test class distribution:\n")
        f.write(str(y_test.value_counts().sort_index()))
        f.write("\n\n")
        f.write(f"Accuracy: {accuracy:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
        f.write("\nConfusion Matrix:\n")
        f.write(str(cm))

    print(f"Metrics saved to: {METRICS_PATH}")


def main() -> None:
    df = load_data(INPUT_PATH)

    missing_cols = [col for col in FEATURES + [TARGET] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    X = df[FEATURES]
    y = df[TARGET]

    print("\nFull target distribution:")
    print(y.value_counts().sort_index())

    X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(
        X, y, df.index,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    print("\nTrain target distribution:")
    print(y_train.value_counts().sort_index())

    print("\nTest target distribution:")
    print(y_test.value_counts().sort_index())

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    save_metrics(y_train, y_test, y_pred)

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")

    predictions_df = df.loc[test_idx].copy()
    predictions_df["predicted_is_delayed"] = y_pred
    predictions_df["delay_risk_score"] = y_prob
    predictions_df.to_csv(PREDICTIONS_PATH, index=False)

    print(f"Predictions saved to: {PREDICTIONS_PATH}")
    print("\nTest prediction distribution:")
    print(pd.Series(y_pred).value_counts().sort_index())

    print("\nTraining completed successfully.")


if __name__ == "__main__":
    main()