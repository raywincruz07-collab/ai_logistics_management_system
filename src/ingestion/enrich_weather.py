from pathlib import Path
import json
import time
import requests
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
INPUT_PATH = Path("data/processed/shipments_routed.csv")
RAW_RESPONSES_DIR = Path("data/raw/weather_responses")
OUTPUT_PATH = Path("data/processed/shipments_weather.csv")

if RAW_RESPONSES_DIR.exists() and not RAW_RESPONSES_DIR.is_dir():
    raise ValueError(f"{RAW_RESPONSES_DIR} exists but is not a directory")

RAW_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# API config
# --------------------------------------------------
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"

# --------------------------------------------------
# Functions
# --------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def build_unique_weather_queries(df: pd.DataFrame) -> pd.DataFrame:
    weather_df = df[[
        "destination_city",
        "destination_state",
        "destination_lat",
        "destination_lon",
        "expected_delivery_date"
    ]].drop_duplicates().copy()

    weather_df["weather_key"] = (
        weather_df["destination_city"].astype(str).str.strip() + "_" +
        weather_df["expected_delivery_date"].astype(str).str.strip()
    )
    return weather_df


def fetch_weather(lat: float, lon: float, date_str: str) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "daily": "weather_code,temperature_2m_max,precipitation_sum,wind_speed_10m_max",
        "timezone": "auto",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def save_raw_response(weather_key: str, response_data: dict) -> None:
    safe_name = weather_key.replace(" ", "_").replace("/", "_")
    file_path = RAW_RESPONSES_DIR / f"{safe_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)


def map_weather_code(code: int | None) -> str:
    weather_code_map = {
        0: "Clear",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Slight Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        80: "Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        95: "Thunderstorm",
    }
    return weather_code_map.get(code, "Unknown")


def extract_weather_metrics(response_data: dict) -> tuple[str | None, float | None, float | None, float | None]:
    try:
        daily = response_data["daily"]
        weather_code = daily["weather_code"][0]
        temperature_c = daily["temperature_2m_max"][0]
        precipitation_mm = daily["precipitation_sum"][0]
        wind_speed_kmh = daily["wind_speed_10m_max"][0]
        weather_main = map_weather_code(weather_code)
        return weather_main, temperature_c, precipitation_mm, wind_speed_kmh
    except (KeyError, IndexError, TypeError):
        return None, None, None, None


def enrich_unique_weather(unique_weather: pd.DataFrame) -> pd.DataFrame:
    results = []

    for _, row in unique_weather.iterrows():
        weather_key = row["weather_key"]
        print(f"Weather: {row['destination_city']} on {row['expected_delivery_date']}")

        try:
            response_data = fetch_weather(
                lat=float(row["destination_lat"]),
                lon=float(row["destination_lon"]),
                date_str=str(row["expected_delivery_date"]),
            )
            save_raw_response(weather_key, response_data)
            weather_main, temperature_c, precipitation_mm, wind_speed_kmh = extract_weather_metrics(response_data)
        except Exception as e:
            print(f"Failed weather {weather_key}: {e}")
            response_data = {}
            weather_main, temperature_c, precipitation_mm, wind_speed_kmh = None, None, None, None

        results.append({
            "destination_city": row["destination_city"],
            "destination_state": row["destination_state"],
            "expected_delivery_date": row["expected_delivery_date"],
            "weather_main": weather_main,
            "temperature_c": temperature_c,
            "precipitation_mm": precipitation_mm,
            "wind_speed_kmh": wind_speed_kmh,
        })

        time.sleep(0.5)

    return pd.DataFrame(results)


def merge_weather(df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    merge_cols = ["destination_city", "destination_state", "expected_delivery_date"]
    merged = df.merge(weather_df, on=merge_cols, how="left")
    return merged


def main() -> None:
    df = load_data(INPUT_PATH)
    unique_weather = build_unique_weather_queries(df)

    print(f"Total shipments: {len(df)}")
    print(f"Unique weather queries: {len(unique_weather)}")

    weather_df = enrich_unique_weather(unique_weather)
    merged = merge_weather(df, weather_df)

    merged.to_csv(OUTPUT_PATH, index=False)

    print("\nWeather enrichment completed.")
    print(f"Output saved to: {OUTPUT_PATH}")

    print(f"Rows with missing weather_main: {merged['weather_main'].isna().sum()}")
    print(f"Rows with missing temperature_c: {merged['temperature_c'].isna().sum()}")
    print(f"Rows with missing precipitation_mm: {merged['precipitation_mm'].isna().sum()}")
    print(f"Rows with missing wind_speed_kmh: {merged['wind_speed_kmh'].isna().sum()}")


if __name__ == "__main__":
    main()