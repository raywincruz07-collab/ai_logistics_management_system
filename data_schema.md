## Dataset Grain
Each row in the master dataset represents one shipment or delivery record. The dataset combines internal shipment information with external API-enriched context such as route, weather, and geolocation data.

## Column Groups
1. Shipment identity fields
2. Shipment planning and operational fields
3. Route and location fields
4. Weather enrichment fields
5. Cost and performance fields
6. Derived AI / KPI fields

## Master Shipment Dataset Schema

| Column Name | Type | Source | Description |
|---|---|---|---|
| shipment_id | string | internal | Unique shipment identifier |
| order_date | date | internal | Date when shipment order was created |
| dispatch_date | date | internal | Date when shipment was dispatched |
| expected_delivery_date | date | internal | Planned delivery date |
| actual_delivery_date | date | internal | Actual delivery completion date |
| origin_city | string | internal | Shipment origin city |
| origin_state | string | internal | Shipment origin state |
| destination_city | string | internal | Shipment destination city |
| destination_state | string | internal | Shipment destination state |
| warehouse_id | string | internal | Warehouse handling the shipment |
| vehicle_type | string | internal | Type of vehicle used |
| shipment_priority | string | internal | Priority level such as low, medium, high |
| product_category | string | internal | Product or shipment category |
| load_weight_kg | float | internal | Shipment weight in kilograms |
| volume_m3 | float | internal | Shipment volume in cubic meters |
| base_shipping_cost | float | internal | Base planned shipping cost |
| delivery_status | string | internal | Status such as delivered, delayed, in transit |
| origin_lat | float | API/derived | Latitude of origin location |
| origin_lon | float | API/derived | Longitude of origin location |
| destination_lat | float | API/derived | Latitude of destination location |
| destination_lon | float | API/derived | Longitude of destination location |
| route_distance_km | float | API | Route distance from routing API |
| estimated_travel_time_min | float | API | Estimated travel time from routing API |
| weather_main | string | API | Main weather condition affecting shipment |
| temperature_c | float | API | Temperature in Celsius |
| precipitation_mm | float | API | Precipitation level |
| wind_speed_kmh | float | API | Wind speed in kilometers per hour |
| delay_hours | float | derived | Difference between expected and actual delivery |
| on_time_flag | int | derived | 1 if delivered on time, else 0 |
| cost_per_km | float | derived | Shipping cost divided by route distance |
| delay_risk_score | float | model/derived | Predicted shipment delay risk score |
| route_efficiency_score | float | derived | Efficiency score based on cost, time, distance |
| recommendation_flag | string | derived | Suggested action such as monitor, reroute, prioritize |

## Why This Schema Works
This schema is designed to support three major layers of the project:
- machine learning for delay prediction
- logistics performance monitoring through KPIs
- management-level decision support through recommendations

The internal fields capture shipment operations, the API fields add real-world context, and the derived fields support predictive analytics and executive reporting.