from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/processed/shipments_geocoded.csv")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "origin_city", "origin_state", "destination_city", "destination_state",
        "origin_lat", "origin_lon", "destination_lat", "destination_lon"
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    missing_origin = df[
        df["origin_lat"].isna() | df["origin_lon"].isna()
    ][["shipment_id", "origin_city", "origin_state"]]

    missing_destination = df[
        df["destination_lat"].isna() | df["destination_lon"].isna()
    ][["shipment_id", "destination_city", "destination_state"]]

    print("\n========== GEOCODING VALIDATION REPORT ==========")
    print(f"Total rows: {len(df)}")
    print(f"Rows missing origin coordinates: {len(missing_origin)}")
    print(f"Rows missing destination coordinates: {len(missing_destination)}")

    if len(missing_origin) > 0:
        print("\n[Missing Origin Coordinates]")
        print(missing_origin.to_string(index=False))

    if len(missing_destination) > 0:
        print("\n[Missing Destination Coordinates]")
        print(missing_destination.to_string(index=False))

    print("\n=================================================\n")


if __name__ == "__main__":
    main()