from pathlib import Path
import numpy as np
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
INPUT_PATH = Path("data/processed/shipments_weather.csv")
OUTPUT_PATH = Path("data/final/shipments_featured.csv")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Functions
# --------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    date_cols = [
        "order_date",
        "dispatch_date",
        "expected_delivery_date",
        "actual_delivery_date",
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df["delay_hours"] = (
        (df["actual_delivery_date"] - df["expected_delivery_date"]).dt.total_seconds() / 3600
    )
    df["delay_hours"] = df["delay_hours"].fillna(0)

    df["on_time_flag"] = (df["delay_hours"] <= 0).astype(int)

    df["delivery_lead_time_hours"] = (
        (df["actual_delivery_date"] - df["dispatch_date"]).dt.total_seconds() / 3600
    )

    df["planned_lead_time_hours"] = (
        (df["expected_delivery_date"] - df["dispatch_date"]).dt.total_seconds() / 3600
    )

    return df


def create_cost_features(df: pd.DataFrame) -> pd.DataFrame:
    df["cost_per_km"] = np.where(
        df["route_distance_km"] > 0,
        df["base_shipping_cost"] / df["route_distance_km"],
        np.nan
    )
    return df


def create_operational_flags(df: pd.DataFrame) -> pd.DataFrame:
    df["is_high_priority"] = (df["shipment_priority"] == "High").astype(int)
    df["is_delayed"] = (df["delay_hours"] > 0).astype(int)
    df["month"] = df["dispatch_date"].dt.month
    df["day_of_week"] = df["dispatch_date"].dt.day_name()
    return df


def create_route_efficiency_score(df: pd.DataFrame) -> pd.DataFrame:
    # Lower cost_per_km and lower delay are better.
    # This is a simple interpretable business score, not a scientific benchmark.
    cost_component = 100 - (df["cost_per_km"].fillna(df["cost_per_km"].median()) * 2)
    delay_component = 100 - (df["delay_hours"].clip(lower=0) * 2)
    weather_penalty = np.where(
        df["weather_main"].isin(["Heavy Rain", "Thunderstorm", "Violent Rain Showers"]),
        15,
        0
    )

    raw_score = (0.5 * cost_component) + (0.5 * delay_component) - weather_penalty
    df["route_efficiency_score"] = raw_score.clip(lower=0, upper=100).round(2)
    return df


def create_recommendation_flag(df: pd.DataFrame) -> pd.DataFrame:
    conditions = [
        (df["delay_hours"] > 0) & (df["shipment_priority"] == "High"),
        (df["cost_per_km"] > df["cost_per_km"].median()) & (df["route_efficiency_score"] < 60),
        (df["weather_main"].isin(["Heavy Rain", "Thunderstorm", "Violent Rain Showers"])),
    ]
    choices = [
        "Prioritize and Escalate",
        "Review Route Cost Efficiency",
        "Monitor Weather Risk",
    ]

    df["recommendation_flag"] = np.select(conditions, choices, default="Normal Monitoring")
    return df


def main() -> None:
    df = load_data(INPUT_PATH)
    df = parse_dates(df)
    df = create_time_features(df)
    df = create_cost_features(df)
    df = create_operational_flags(df)
    df = create_route_efficiency_score(df)
    df = create_recommendation_flag(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nFeature engineering completed.")
    print(f"Output saved to: {OUTPUT_PATH}")
    print("\nCreated columns:")
    print([
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
    ])


if __name__ == "__main__":
    main()