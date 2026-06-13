# Pipeline Design for AI-Based Logistics Management System

## 1. Pipeline Overview

The project follows a multi-stage data pipeline that combines internal shipment records with external API-enriched context. The goal is to transform basic logistics records into a structured analytical dataset for AI-based prediction, KPI monitoring, and executive reporting.

---

## 2. Pipeline Stages

### Stage 1: Shipment Input Data
This stage contains the base shipment records created internally for the project.

Input fields include:
- shipment_id
- order_date
- dispatch_date
- expected_delivery_date
- actual_delivery_date
- origin_city
- origin_state
- destination_city
- destination_state
- warehouse_id
- vehicle_type
- shipment_priority
- product_category
- load_weight_kg
- volume_m3
- base_shipping_cost
- delivery_status

Output:
- base shipment dataset

Storage:
- data/raw/shipments.csv

---

### Stage 2: Geocoding Enrichment
This stage uses the Nominatim API to convert origin and destination city/state values into latitude and longitude coordinates.

Input:
- origin_city
- origin_state
- destination_city
- destination_state

Output fields:
- origin_lat
- origin_lon
- destination_lat
- destination_lon

Storage:
- data/raw/geocoding_responses/
- data/processed/shipments_geocoded.csv

---

### Stage 3: Route Enrichment
This stage uses openrouteservice to calculate route distance and estimated travel duration between origin and destination coordinates.

Input:
- origin_lat
- origin_lon
- destination_lat
- destination_lon

Output fields:
- route_distance_km
- estimated_travel_time_min

Storage:
- data/raw/routing_responses/
- data/processed/shipments_routed.csv

---

### Stage 4: Weather Enrichment
This stage uses Open-Meteo to fetch weather conditions relevant to the shipment route or delivery period.

Input:
- destination_lat
- destination_lon
- dispatch_date or expected_delivery_date

Output fields:
- weather_main
- temperature_c
- precipitation_mm
- wind_speed_kmh

Storage:
- data/raw/weather_responses/
- data/processed/shipments_weather.csv

---

### Stage 5: Feature Engineering
This stage creates business and AI-ready fields from the enriched shipment data.

Derived fields include:
- delay_hours
- on_time_flag
- cost_per_km
- route_efficiency_score

Storage:
- data/final/shipments_featured.csv

---

### Stage 6: Modeling and KPI Layer
This stage uses the final featured dataset for:
- delay risk prediction
- KPI generation
- dashboard reporting
- recommendation logic

Output fields may include:
- delay_risk_score
- recommendation_flag

Storage:
- data/final/shipments_model_ready.csv
- data/final/kpi_summary.csv



## 3. Pipeline Flow Summary

Base Shipment Data
→ Geocoding Enrichment
→ Route Enrichment
→ Weather Enrichment
→ Feature Engineering
→ Modeling and KPI Generation
→ Dashboard and Reporting



## 4. Design Principles

- Raw API responses must be stored separately for traceability
- Each enrichment stage should create a new structured output file
- Final analytical data should only be created after all enrichment steps are complete
- The pipeline should be modular so each stage can be rerun independently