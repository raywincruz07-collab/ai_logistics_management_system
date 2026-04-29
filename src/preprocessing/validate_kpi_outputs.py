from pathlib import Path
import pandas as pd

FILES = [
    Path("data/final/kpi_summary.csv"),
    Path("data/final/warehouse_kpi_summary.csv"),
    Path("data/final/route_kpi_summary.csv"),
]

def main() -> None:
    print("\n========== KPI OUTPUT VALIDATION REPORT ==========")

    for file_path in FILES:
        if not file_path.exists():
            print(f"Missing file: {file_path}")
            continue

        df = pd.read_csv(file_path)
        print(f"\nFile: {file_path}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

    print("\n==================================================\n")


if __name__ == "__main__":
    main()