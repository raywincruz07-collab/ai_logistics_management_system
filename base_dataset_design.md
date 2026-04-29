# Base Shipment Dataset Design

## 1. Purpose
The base shipment dataset represents internal logistics operations before API enrichment. It provides the core shipment-level records that will later be enhanced with geocoding, routing, and weather context.

---

## 2. File Name
data/raw/shipments.csv

---

## 3. Dataset Grain
Each row represents one shipment or delivery record.

---

## 4. Required Columns

| Column Name | Type | Description |
|---|---|---|
| shipment_id | string | Unique shipment identifier |
| order_date | date | Date the order was created |
| dispatch_date | date | Date the shipment was dispatched |
| expected_delivery_date | date | Planned delivery date |
| actual_delivery_date | date | Actual delivery date |
| origin_city | string | Origin city |
| origin_state | string | Origin state |
| destination_city | string | Destination city |
| destination_state | string | Destination state |
| warehouse_id | string | Warehouse handling the shipment |
| vehicle_type | string | Vehicle type used for transport |
| shipment_priority | string | Shipment priority level |
| product_category | string | Category of goods |
| load_weight_kg | float | Shipment weight in kilograms |
| volume_m3 | float | Shipment volume in cubic meters |
| base_shipping_cost | float | Planned shipment cost |
| delivery_status | string | Shipment status |

---

## 5. Allowed Example Categories

### vehicle_type
- Truck
- Mini Truck
- Van

### shipment_priority
- Low
- Medium
- High

### product_category
- Electronics
- Grocery
- Pharma
- Industrial Goods
- Apparel

### delivery_status
- Delivered
- Delayed
- In Transit

---

## 6. Recommended Dataset Size
Start with 500 rows for testing.
Later expand to 2000 to 5000 rows after the pipeline works.

---

## 7. Quality Rules
- shipment_id must be unique
- dispatch_date must be on or after order_date
- expected_delivery_date must be on or after dispatch_date
- actual_delivery_date should be realistic relative to dispatch_date
- origin and destination values must be valid Indian city/state combinations
- base_shipping_cost must be positive
- load_weight_kg and volume_m3 must be positive