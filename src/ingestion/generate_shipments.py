from pathlib import Path
import random
from datetime import datetime, timedelta
import pandas as pd

# --------------------------------------------------
# Config
# --------------------------------------------------
OUTPUT_PATH = Path("data/raw/shipments.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

NUM_ROWS = 500
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

WAREHOUSES = [
    {"warehouse_id": "WH_CHN_01", "city": "Chennai", "state": "Tamil Nadu"},
    {"warehouse_id": "WH_BLR_01", "city": "Bengaluru", "state": "Karnataka"},
    {"warehouse_id": "WH_HYD_01", "city": "Hyderabad", "state": "Telangana"},
    {"warehouse_id": "WH_MUM_01", "city": "Mumbai", "state": "Maharashtra"},
    {"warehouse_id": "WH_DEL_01", "city": "Delhi", "state": "Delhi"},
]

DESTINATIONS = [
    {"city": "Bengaluru", "state": "Karnataka"},
    {"city": "Chennai", "state": "Tamil Nadu"},
    {"city": "Hyderabad", "state": "Telangana"},
    {"city": "Mumbai", "state": "Maharashtra"},
    {"city": "Delhi", "state": "Delhi"},
    {"city": "Pune", "state": "Maharashtra"},
    {"city": "Ahmedabad", "state": "Gujarat"},
    {"city": "Jaipur", "state": "Rajasthan"},
    {"city": "Coimbatore", "state": "Tamil Nadu"},
    {"city": "Vijayawada", "state": "Andhra Pradesh"},
    {"city": "Surat", "state": "Gujarat"},
    {"city": "Chandigarh", "state": "Chandigarh"},
    {"city": "Kochi", "state": "Kerala"},
    {"city": "Nagpur", "state": "Maharashtra"},
    {"city": "Lucknow", "state": "Uttar Pradesh"},
]

VEHICLE_TYPES = ["Truck", "Mini Truck", "Van"]
SHIPMENT_PRIORITIES = ["Low", "Medium", "High"]
PRODUCT_CATEGORIES = ["Electronics", "Grocery", "Pharma", "Industrial Goods", "Apparel"]

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 3, 31)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days


def random_date(start_date: datetime, max_offset_days: int) -> datetime:
    return start_date + timedelta(days=random.randint(0, max_offset_days))


def choose_destination_not_same_as_origin(origin_city: str, origin_state: str) -> dict:
    valid_destinations = [
        d for d in DESTINATIONS
        if not (d["city"] == origin_city and d["state"] == origin_state)
    ]
    return random.choice(valid_destinations)


def estimate_base_cost(vehicle_type: str, weight: float, volume: float, priority: str) -> float:
    base = 3000

    if vehicle_type == "Truck":
        base += 8000
    elif vehicle_type == "Mini Truck":
        base += 5000
    else:
        base += 2500

    base += weight * 12
    base += volume * 1800

    if priority == "High":
        base += 3000
    elif priority == "Medium":
        base += 1500

    noise = random.randint(-1200, 1200)
    return max(2500, round(base + noise, 2))


def decide_delay(priority: str, vehicle_type: str, product_category: str) -> int:
    delay_probability = 0.22

    if priority == "High":
        delay_probability -= 0.05
    if vehicle_type == "Van":
        delay_probability += 0.03
    if product_category == "Pharma":
        delay_probability -= 0.02
    if product_category == "Industrial Goods":
        delay_probability += 0.04

    return 1 if random.random() < delay_probability else 0


def generate_row(i: int) -> dict:
    warehouse = random.choice(WAREHOUSES)
    destination = choose_destination_not_same_as_origin(warehouse["city"], warehouse["state"])

    order_date = random_date(START_DATE, DATE_RANGE_DAYS)
    dispatch_date = order_date + timedelta(days=random.randint(0, 2))
    planned_transit_days = random.randint(1, 5)
    expected_delivery_date = dispatch_date + timedelta(days=planned_transit_days)

    vehicle_type = random.choice(VEHICLE_TYPES)
    priority = random.choices(
        SHIPMENT_PRIORITIES,
        weights=[0.25, 0.45, 0.30],
        k=1
    )[0]
    product_category = random.choice(PRODUCT_CATEGORIES)

    load_weight_kg = round(random.uniform(80, 650), 2)
    volume_m3 = round(random.uniform(0.5, 5.0), 2)

    is_delayed = decide_delay(priority, vehicle_type, product_category)

    if is_delayed:
        actual_delivery_date = expected_delivery_date + timedelta(days=random.randint(1, 3))
        delivery_status = "Delayed"
    else:
        early_or_on_time = random.choice([0, 0, 1])  # mostly on time, sometimes early
        actual_delivery_date = expected_delivery_date - timedelta(days=early_or_on_time)
        delivery_status = "Delivered"

    base_shipping_cost = estimate_base_cost(vehicle_type, load_weight_kg, volume_m3, priority)

    return {
        "shipment_id": f"SHP{i:05d}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "dispatch_date": dispatch_date.strftime("%Y-%m-%d"),
        "expected_delivery_date": expected_delivery_date.strftime("%Y-%m-%d"),
        "actual_delivery_date": actual_delivery_date.strftime("%Y-%m-%d"),
        "origin_city": warehouse["city"],
        "origin_state": warehouse["state"],
        "destination_city": destination["city"],
        "destination_state": destination["state"],
        "warehouse_id": warehouse["warehouse_id"],
        "vehicle_type": vehicle_type,
        "shipment_priority": priority,
        "product_category": product_category,
        "load_weight_kg": load_weight_kg,
        "volume_m3": volume_m3,
        "base_shipping_cost": base_shipping_cost,
        "delivery_status": delivery_status,
    }


def main() -> None:
    rows = [generate_row(i) for i in range(1, NUM_ROWS + 1)]
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nGenerated shipment dataset saved to: {OUTPUT_PATH}")
    print(f"Total rows: {len(df)}")
    print("\nDelivery status distribution:")
    print(df["delivery_status"].value_counts())
    print("\nWarehouse distribution:")
    print(df["warehouse_id"].value_counts())
    print("\nTop 10 route counts:")
    route_counts = (df["origin_city"] + " → " + df["destination_city"]).value_counts().head(10)
    print(route_counts)


if __name__ == "__main__":
    main()