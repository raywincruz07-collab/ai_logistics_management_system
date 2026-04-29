from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/final/shipments_featured.csv")

REQUIRED_COLUMNS = [
    "delay_hours",
    "on_time_flag",
    "delivery_lead_time_hours",
    "planned_lead_time_hours",
    "cost_per_km",
    "is_high_priority",
    "is_delayed",
    "month",
    "day_of_week",
    "route_efficiency_score",
    "recommendation_flag",
]

def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    print("\n========== FEATURE VALIDATION REPORT ==========")
    print(f"Total rows: {len(df)}")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"Missing required columns: {missing_cols}")
        return

    for col in REQUIRED_COLUMNS:
        print(f"Rows missing {col}: {df[col].isna().sum()}")

    print("\nRecommendation flag distribution:")
    print(df["recommendation_flag"].value_counts(dropna=False))

    print("\n==============================================\n")


if __name__ == "__main__":
    main()