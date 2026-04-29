from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/final/shipments_scored.csv")

REQUIRED_COLUMNS = [
    "predicted_is_delayed",
    "delay_risk_score",
]

def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    print("\n========== SCORED DATA VALIDATION REPORT ==========")
    print(f"Total rows: {len(df)}")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"Missing required columns: {missing_cols}")
        return

    for col in REQUIRED_COLUMNS:
        print(f"Rows missing {col}: {df[col].isna().sum()}")

    invalid_scores = ((df["delay_risk_score"] < 0) | (df["delay_risk_score"] > 1)).sum()
    print(f"Rows with invalid delay_risk_score outside [0,1]: {invalid_scores}")

    print("\nPrediction distribution:")
    print(df["predicted_is_delayed"].value_counts(dropna=False))

    print("\n==================================================\n")


if __name__ == "__main__":
    main()