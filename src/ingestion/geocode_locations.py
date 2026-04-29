from pathlib import Path
import json
import time
import requests
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
SHIPMENTS_PATH = Path("data/raw/shipments.csv")
RAW_RESPONSES_DIR = Path("data/raw/geocoding_responses")
OUTPUT_PATH = Path("data/processed/shipments_geocoded.csv")

RAW_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# API config
# --------------------------------------------------
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "ai-logistics-management-system/1.0 (student project)"
}

# --------------------------------------------------
# Functions
# --------------------------------------------------
def load_shipments(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Shipment file not found: {path}")
    return pd.read_csv(path)


def build_unique_locations(df: pd.DataFrame) -> pd.DataFrame:
    origin_locations = df[["origin_city", "origin_state"]].drop_duplicates().rename(
        columns={"origin_city": "city", "origin_state": "state"}
    )
    destination_locations = df[["destination_city", "destination_state"]].drop_duplicates().rename(
        columns={"destination_city": "city", "destination_state": "state"}
    )
    unique_locations = pd.concat([origin_locations, destination_locations], ignore_index=True).drop_duplicates()
    unique_locations["location_key"] = unique_locations["city"].str.strip() + ", " + unique_locations["state"].str.strip()
    return unique_locations


def geocode_location(city: str, state: str) -> dict:
    params = {
        "city": city,
        "state": state,
        "country": "India",
        "format": "jsonv2",
        "limit": 1,
    }
    response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_response(location_key: str, response_data: dict) -> None:
    safe_name = location_key.replace(",", "").replace(" ", "_").replace("/", "_")
    file_path = RAW_RESPONSES_DIR / f"{safe_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)


def extract_lat_lon(response_data: list) -> tuple[float | None, float | None]:
    if not response_data:
        return None, None
    try:
        lat = float(response_data[0]["lat"])
        lon = float(response_data[0]["lon"])
        return lat, lon
    except (KeyError, ValueError, IndexError, TypeError):
        return None, None


def geocode_unique_locations(unique_locations: pd.DataFrame) -> pd.DataFrame:
    results = []

    for _, row in unique_locations.iterrows():
        city = row["city"]
        state = row["state"]
        location_key = row["location_key"]

        print(f"Geocoding: {location_key}")

        try:
            response_data = geocode_location(city, state)
            save_raw_response(location_key, response_data)
            lat, lon = extract_lat_lon(response_data)
        except Exception as e:
            print(f"Failed for {location_key}: {e}")
            response_data = []
            lat, lon = None, None

        results.append({
            "city": city,
            "state": state,
            "location_key": location_key,
            "lat": lat,
            "lon": lon,
        })

        time.sleep(1)  # respectful delay for public API

    return pd.DataFrame(results)


def merge_geocodes(shipments: pd.DataFrame, geocoded: pd.DataFrame) -> pd.DataFrame:
    geocoded_origin = geocoded.rename(columns={
        "city": "origin_city",
        "state": "origin_state",
        "lat": "origin_lat",
        "lon": "origin_lon",
    })[["origin_city", "origin_state", "origin_lat", "origin_lon"]]

    geocoded_destination = geocoded.rename(columns={
        "city": "destination_city",
        "state": "destination_state",
        "lat": "destination_lat",
        "lon": "destination_lon",
    })[["destination_city", "destination_state", "destination_lat", "destination_lon"]]

    merged = shipments.merge(
        geocoded_origin,
        on=["origin_city", "origin_state"],
        how="left"
    ).merge(
        geocoded_destination,
        on=["destination_city", "destination_state"],
        how="left"
    )

    return merged


def main() -> None:
    shipments = load_shipments(SHIPMENTS_PATH)
    unique_locations = build_unique_locations(shipments)

    print(f"Total shipments: {len(shipments)}")
    print(f"Unique locations to geocode: {len(unique_locations)}")

    geocoded = geocode_unique_locations(unique_locations)
    merged = merge_geocodes(shipments, geocoded)

    merged.to_csv(OUTPUT_PATH, index=False)

    print("\nGeocoding completed.")
    print(f"Output saved to: {OUTPUT_PATH}")

    missing_origin = merged["origin_lat"].isna().sum() + merged["origin_lon"].isna().sum()
    missing_destination = merged["destination_lat"].isna().sum() + merged["destination_lon"].isna().sum()

    print(f"Rows with missing origin coordinates: {missing_origin}")
    print(f"Rows with missing destination coordinates: {missing_destination}")


if __name__ == "__main__":
    main()