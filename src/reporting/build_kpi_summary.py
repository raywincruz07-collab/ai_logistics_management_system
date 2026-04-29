from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
INPUT_PATH = Path("data/final/shipments_featured.csv")
OUTPUT_DIR = Path("data/final")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OVERALL_KPI_PATH = OUTPUT_DIR / "kpi_summary.csv"
WAREHOUSE_KPI_PATH = OUTPUT_DIR / "warehouse_kpi_summary.csv"
ROUTE_KPI_PATH = OUTPUT_DIR / "route_kpi_summary.csv"

# --------------------------------------------------
# Functions
# --------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def build_overall_kpis(df: pd.DataFrame) -> pd.DataFrame:
    kpis = {
        "total_shipments": len(df),
        "on_time_delivery_rate_pct": round(df["on_time_flag"].mean() * 100, 2),
        "average_delay_hours": round(df["delay_hours"].mean(), 2),
        "total_shipping_cost": round(df["base_shipping_cost"].sum(), 2),
        "average_shipping_cost": round(df["base_shipping_cost"].mean(), 2),
        "average_cost_per_km": round(df["cost_per_km"].mean(), 2),
        "average_route_efficiency_score": round(df["route_efficiency_score"].mean(), 2),
        "delayed_shipment_count": int(df["is_delayed"].sum()),
        "high_priority_shipment_count": int(df["is_high_priority"].sum()),
    }

    return pd.DataFrame(list(kpis.items()), columns=["kpi_name", "kpi_value"])


def build_warehouse_kpis(df: pd.DataFrame) -> pd.DataFrame:
    warehouse_kpis = (
        df.groupby("warehouse_id")
        .agg(
            total_shipments=("shipment_id", "count"),
            on_time_delivery_rate_pct=("on_time_flag", lambda x: round(x.mean() * 100, 2)),
            average_delay_hours=("delay_hours", lambda x: round(x.mean(), 2)),
            total_shipping_cost=("base_shipping_cost", lambda x: round(x.sum(), 2)),
            average_cost_per_km=("cost_per_km", lambda x: round(x.mean(), 2)),
            average_route_efficiency_score=("route_efficiency_score", lambda x: round(x.mean(), 2)),
        )
        .reset_index()
        .sort_values(by="average_route_efficiency_score", ascending=False)
    )
    return warehouse_kpis


def build_route_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df["route_name"] = df["origin_city"] + " → " + df["destination_city"]

    route_kpis = (
        df.groupby("route_name")
        .agg(
            total_shipments=("shipment_id", "count"),
            on_time_delivery_rate_pct=("on_time_flag", lambda x: round(x.mean() * 100, 2)),
            average_delay_hours=("delay_hours", lambda x: round(x.mean(), 2)),
            average_cost_per_km=("cost_per_km", lambda x: round(x.mean(), 2)),
            average_route_efficiency_score=("route_efficiency_score", lambda x: round(x.mean(), 2)),
        )
        .reset_index()
        .sort_values(by="average_delay_hours", ascending=False)
    )
    return route_kpis


def main() -> None:
    df = load_data(INPUT_PATH)

    overall_kpis = build_overall_kpis(df)
    warehouse_kpis = build_warehouse_kpis(df)
    route_kpis = build_route_kpis(df)

    overall_kpis.to_csv(OVERALL_KPI_PATH, index=False)
    warehouse_kpis.to_csv(WAREHOUSE_KPI_PATH, index=False)
    route_kpis.to_csv(ROUTE_KPI_PATH, index=False)

    print("\nKPI summary generation completed.")
    print(f"Saved: {OVERALL_KPI_PATH}")
    print(f"Saved: {WAREHOUSE_KPI_PATH}")
    print(f"Saved: {ROUTE_KPI_PATH}")


if __name__ == "__main__":
    main()