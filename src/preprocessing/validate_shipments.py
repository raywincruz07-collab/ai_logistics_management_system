from pathlib import Path
import pandas as pd

# ----------------------------
# File path
# ----------------------------
DATA_PATH = Path("data/raw/shipments.csv")

# ----------------------------
# Expected schema
# ----------------------------
REQUIRED_COLUMNS = [
    "shipment_id",
    "order_date",
    "dispatch_date",
    "expected_delivery_date",
    "actual_delivery_date",
    "origin_city",
    "origin_state",
    "destination_city",
    "destination_state",
    "warehouse_id",
    "vehicle_type",
    "shipment_priority",
    "product_category",
    "load_weight_kg",
    "volume_m3",
    "base_shipping_cost",
    "delivery_status",
]

ALLOWED_VEHICLE_TYPES = {"Truck", "Mini Truck", "Van"}
ALLOWED_PRIORITIES = {"Low", "Medium", "High"}
ALLOWED_CATEGORIES = {
    "Electronics",
    "Grocery",
    "Pharma",
    "Industrial Goods",
    "Apparel",
}
ALLOWED_STATUS = {"Delivered", "Delayed", "In Transit"}

NUMERIC_COLUMNS = ["load_weight_kg", "volume_m3", "base_shipping_cost"]
DATE_COLUMNS = [
    "order_date",
    "dispatch_date",
    "expected_delivery_date",
    "actual_delivery_date",
]

LOCATION_COLUMNS = [
    "origin_city",
    "origin_state",
    "destination_city",
    "destination_state",
    "warehouse_id",
]


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path)


def check_required_columns(df: pd.DataFrame) -> list[str]:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def validate_unique_ids(df: pd.DataFrame) -> list[str]:
    duplicates = df[df["shipment_id"].duplicated()]["shipment_id"].tolist()
    return duplicates


def validate_missing_locations(df: pd.DataFrame) -> dict[str, int]:
    result = {}
    for col in LOCATION_COLUMNS:
        result[col] = df[col].isna().sum() + (df[col].astype(str).str.strip() == "").sum()
    return result


def validate_numeric_values(df: pd.DataFrame) -> dict[str, int]:
    result = {}
    for col in NUMERIC_COLUMNS:
        result[col] = (df[col] <= 0).sum()
    return result


def validate_categories(df: pd.DataFrame) -> dict[str, set]:
    return {
        "vehicle_type": set(df["vehicle_type"].dropna().unique()) - ALLOWED_VEHICLE_TYPES,
        "shipment_priority": set(df["shipment_priority"].dropna().unique()) - ALLOWED_PRIORITIES,
        "product_category": set(df["product_category"].dropna().unique()) - ALLOWED_CATEGORIES,
        "delivery_status": set(df["delivery_status"].dropna().unique()) - ALLOWED_STATUS,
    }


def validate_dates(df: pd.DataFrame) -> dict[str, int]:
    checks = {
        "invalid_order_date": df["order_date"].isna().sum(),
        "invalid_dispatch_date": df["dispatch_date"].isna().sum(),
        "invalid_expected_delivery_date": df["expected_delivery_date"].isna().sum(),
        "invalid_actual_delivery_date": df["actual_delivery_date"].isna().sum(),
        "dispatch_before_order": (df["dispatch_date"] < df["order_date"]).sum(),
        "expected_before_dispatch": (df["expected_delivery_date"] < df["dispatch_date"]).sum(),
        "actual_before_dispatch": (df["actual_delivery_date"] < df["dispatch_date"]).sum(),
    }
    return checks


def print_report(
    row_count: int,
    missing_columns: list[str],
    duplicate_ids: list[str],
    missing_locations: dict[str, int],
    numeric_issues: dict[str, int],
    category_issues: dict[str, set],
    date_issues: dict[str, int],
) -> None:
    print("\n========== SHIPMENT DATA VALIDATION REPORT ==========")
    print(f"Total rows: {row_count}")

    print("\n[1] Required Columns")
    if not missing_columns:
        print("PASS - All required columns are present.")
    else:
        print(f"FAIL - Missing columns: {missing_columns}")

    print("\n[2] Unique Shipment IDs")
    if not duplicate_ids:
        print("PASS - All shipment_id values are unique.")
    else:
        print(f"FAIL - Duplicate shipment_id values found: {duplicate_ids}")

    print("\n[3] Missing / Empty Location Fields")
    for col, count in missing_locations.items():
        print(f"{col}: {count}")

    print("\n[4] Numeric Value Issues (<= 0)")
    for col, count in numeric_issues.items():
        print(f"{col}: {count}")

    print("\n[5] Invalid Category Values")
    for col, invalid_values in category_issues.items():
        if invalid_values:
            print(f"{col}: INVALID VALUES -> {invalid_values}")
        else:
            print(f"{col}: PASS")

    print("\n[6] Date Validation")
    for check, count in date_issues.items():
        print(f"{check}: {count}")

    print("\n====================================================\n")


def main() -> None:
    df = load_data(DATA_PATH)

    missing_columns = check_required_columns(df)
    if missing_columns:
        print_report(
            row_count=len(df),
            missing_columns=missing_columns,
            duplicate_ids=[],
            missing_locations={},
            numeric_issues={},
            category_issues={},
            date_issues={},
        )
        return

    df = parse_dates(df)

    duplicate_ids = validate_unique_ids(df)
    missing_locations = validate_missing_locations(df)
    numeric_issues = validate_numeric_values(df)
    category_issues = validate_categories(df)
    date_issues = validate_dates(df)

    print_report(
        row_count=len(df),
        missing_columns=missing_columns,
        duplicate_ids=duplicate_ids,
        missing_locations=missing_locations,
        numeric_issues=numeric_issues,
        category_issues=category_issues,
        date_issues=date_issues,
    )


if __name__ == "__main__":
    main()