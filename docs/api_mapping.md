# API Mapping for AI-Based Logistics Management System

## 1. Selected APIs

### API 1: Nominatim
Purpose:
Convert origin and destination city/state names into geographic coordinates.

Used for:
- origin_lat
- origin_lon
- destination_lat
- destination_lon

Why needed:
Routing and weather APIs require coordinates.

---

### API 2: openrouteservice
Purpose:
Calculate route distance and estimated travel time between origin and destination coordinates.

Used for:
- route_distance_km
- estimated_travel_time_min

Why needed:
Supports route intelligence, cost analysis, and delay-risk features.

---

### API 3: Open-Meteo
Purpose:
Fetch weather conditions for shipment routes or delivery dates.

Used for:
- weather_main
- temperature_c
- precipitation_mm
- wind_speed_kmh

Why needed:
Weather is an external risk factor affecting logistics performance.

---

### API 4: data.gov.in (optional)
Purpose:
Add Indian transport context data for advanced enrichment.

Possible usage:
- transport trends
- road/region context
- sector-level benchmarking

Why needed:
Improves realism and external context for India-based logistics analysis.


## 2. API to Schema Mapping

| API | Input | Output Fields | Schema Columns Filled |
|---|---|---|---|
| Nominatim | city, state | latitude, longitude | origin_lat, origin_lon, destination_lat, destination_lon |
| openrouteservice | origin coordinates, destination coordinates | route distance, travel duration | route_distance_km, estimated_travel_time_min |
| Open-Meteo | latitude, longitude, date/time | temperature, precipitation, wind speed, weather code | weather_main, temperature_c, precipitation_mm, wind_speed_kmh |
| data.gov.in (optional) | dataset API parameters | transport context fields | optional external enrichment fields |


## 3. API Priority

### Phase 1
- Nominatim
- openrouteservice
- Open-Meteo

### Phase 2
- data.gov.in optional enrichment

## 4. Implementation Logic

1. Read shipment master data with origin and destination city/state
2. Use Nominatim to geocode both locations
3. Use openrouteservice to calculate distance and estimated travel time
4. Use Open-Meteo to fetch weather data for delivery-relevant time and location
5. Merge all API results into the enriched shipment dataset 