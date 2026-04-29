from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/processed/shipments_weather.csv")

REQUIRED_COLUMNS = [
    "weather_main",
    "temperature_c",
    "precipitation_mm",
    "wind_speed_kmh",
]

def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    print("\n========== WEATHER VALIDATION REPORT ==========")
    print(f"Total rows: {len(df)}")

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            print(f"Missing required column: {col}")
            return

    for col in REQUIRED_COLUMNS:
        print(f"Rows missing {col}: {df[col].isna().sum()}")

    print("\n==============================================\n")


if __name__ == "__main__":
    main()