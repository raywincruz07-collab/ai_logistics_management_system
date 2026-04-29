from pathlib import Path
import json
import os
import time
import requests
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
INPUT_PATH = Path("data/processed/shipments_geocoded.csv")
RAW_RESPONSES_DIR = Path("data/raw/routing_responses")
OUTPUT_PATH = Path("data/processed/shipments_routed.csv")
CACHE_PATH = Path("data/processed/unique_routes_cache.csv")

if RAW_RESPONSES_DIR.exists() and not RAW_RESPONSES_DIR.is_dir():
    raise ValueError(f"{RAW_RESPONSES_DIR} exists but is not a directory")

RAW_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# API config
# --------------------------------------------------
ORS_API_KEY = os.getenv("ORS_API_KEY")
if not ORS_API_KEY:
    raise EnvironmentError("ORS_API_KEY is not set. Please set it before running the script.")

ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
HEADERS = {
    "Authorization": ORS_API_KEY,
    "Content-Type": "application/json",
}

MAX_RETRIES = 5
NORMAL_SLEEP_SECONDS = 1.5
RATE_LIMIT_SLEEP_SECONDS = 20

# --------------------------------------------------
# Functions
# --------------------------------------------------
def load_shipments(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def build_unique_routes(df: pd.DataFrame) -> pd.DataFrame:
    route_cols = [
        "origin_city", "origin_state", "destination_city", "destination_state",
        "origin_lat", "origin_lon", "destination_lat", "destination_lon"
    ]
    unique_routes = df[route_cols].drop_duplicates().copy()
    unique_routes["route_key"] = (
        unique_routes["origin_city"].str.strip() + "_" +
        unique_routes["destination_city"].str.strip()
    )
    return unique_routes


def get_raw_response_path(route_key: str) -> Path:
    safe_name = route_key.replace(" ", "_").replace("/", "_")
    return RAW_RESPONSES_DIR / f"{safe_name}.json"


def raw_response_exists(route_key: str) -> bool:
    return get_raw_response_path(route_key).exists()


def load_raw_response(route_key: str) -> dict:
    file_path = get_raw_response_path(route_key)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_raw_response(route_key: str, response_data: dict) -> None:
    file_path = get_raw_response_path(route_key)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)


def call_route_api(origin_lon: float, origin_lat: float, destination_lon: float, destination_lat: float) -> dict:
    body = {
        "coordinates": [
            [origin_lon, origin_lat],
            [destination_lon, destination_lat]
        ]
    }
    response = requests.post(ORS_URL, headers=HEADERS, json=body, timeout=60)
    response.raise_for_status()
    return response.json()


def call_route_api_with_retry(origin_lon: float, origin_lat: float, destination_lon: float, destination_lat: float, route_key: str) -> dict:
    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"API call attempt {attempt}/{MAX_RETRIES} for {route_key}")
            return call_route_api(origin_lon, origin_lat, destination_lon, destination_lat)

        except requests.exceptions.HTTPError as e:
            last_exception = e
            status_code = e.response.status_code if e.response is not None else None

            if status_code == 429:
                print(f"429 rate limit hit for {route_key}. Sleeping {RATE_LIMIT_SLEEP_SECONDS} seconds...")
                time.sleep(RATE_LIMIT_SLEEP_SECONDS)
            else:
                print(f"HTTP error for {route_key}: {e}")
                time.sleep(5)

        except Exception as e:
            last_exception = e
            print(f"Unexpected error for {route_key}: {e}")
            time.sleep(5)

    raise RuntimeError(f"All retries failed for {route_key}: {last_exception}")


def extract_route_metrics(response_data: dict) -> tuple[float | None, float | None]:
    try:
        summary = response_data["routes"][0]["summary"]
        distance_km = summary["distance"] / 1000
        duration_min = summary["duration"] / 60
        return distance_km, duration_min
    except (KeyError, IndexError, TypeError):
        return None, None


def process_unique_routes(unique_routes: pd.DataFrame) -> pd.DataFrame:
    results = []

    for _, row in unique_routes.iterrows():
        route_key = row["route_key"]
        print(f"\nProcessing route: {row['origin_city']} -> {row['destination_city']}")

        response_data = None

        try:
            if raw_response_exists(route_key):
                print(f"Using cached raw response for {route_key}")
                response_data = load_raw_response(route_key)
            else:
                response_data = call_route_api_with_retry(
                    origin_lon=float(row["origin_lon"]),
                    origin_lat=float(row["origin_lat"]),
                    destination_lon=float(row["destination_lon"]),
                    destination_lat=float(row["destination_lat"]),
                    route_key=route_key,
                )
                save_raw_response(route_key, response_data)

            distance_km, duration_min = extract_route_metrics(response_data)

        except Exception as e:
            print(f"FAILED route {route_key}: {e}")
            distance_km, duration_min = None, None

        results.append({
            "origin_city": row["origin_city"],
            "origin_state": row["origin_state"],
            "destination_city": row["destination_city"],
            "destination_state": row["destination_state"],
            "route_key": route_key,
            "route_distance_km": distance_km,
            "estimated_travel_time_min": duration_min,
        })

        time.sleep(NORMAL_SLEEP_SECONDS)

    return pd.DataFrame(results)


def merge_routes(shipments: pd.DataFrame, routed: pd.DataFrame) -> pd.DataFrame:
    merge_cols = ["origin_city", "origin_state", "destination_city", "destination_state"]
    merged = shipments.merge(
        routed[merge_cols + ["route_distance_km", "estimated_travel_time_min"]],
        on=merge_cols,
        how="left"
    )
    return merged


def main() -> None:
    shipments = load_shipments(INPUT_PATH)
    unique_routes = build_unique_routes(shipments)

    print(f"Total shipments: {len(shipments)}")
    print(f"Unique routes to process: {len(unique_routes)}")

    routed = process_unique_routes(unique_routes)
    routed.to_csv(CACHE_PATH, index=False)

    merged = merge_routes(shipments, routed)
    merged.to_csv(OUTPUT_PATH, index=False)

    missing_distance = merged["route_distance_km"].isna().sum()
    missing_duration = merged["estimated_travel_time_min"].isna().sum()

    print("\nRouting completed.")
    print(f"Route cache saved to: {CACHE_PATH}")
    print(f"Output saved to: {OUTPUT_PATH}")
    print(f"Rows with missing route_distance_km: {missing_distance}")
    print(f"Rows with missing estimated_travel_time_min: {missing_duration}")


if __name__ == "__main__":
    main()