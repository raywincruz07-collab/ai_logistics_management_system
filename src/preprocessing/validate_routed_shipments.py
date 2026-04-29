from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/processed/shipments_routed.csv")

REQUIRED_COLUMNS = [
    "route_distance_km",
    "estimated_travel_time_min",
]

def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    print("\n========== ROUTING VALIDATION REPORT ==========")
    print(f"Total rows: {len(df)}")

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            print(f"Missing required column: {col}")
            return

    missing_distance = df["route_distance_km"].isna().sum()
    missing_duration = df["estimated_travel_time_min"].isna().sum()
    non_positive_distance = (df["route_distance_km"] <= 0).sum()
    non_positive_duration = (df["estimated_travel_time_min"] <= 0).sum()

    print(f"Rows missing route_distance_km: {missing_distance}")
    print(f"Rows missing estimated_travel_time_min: {missing_duration}")
    print(f"Rows with non-positive route_distance_km: {non_positive_distance}")
    print(f"Rows with non-positive estimated_travel_time_min: {non_positive_duration}")
    print("\n===============================================\n")


if __name__ == "__main__":
    main()