import joblib
import pandas as pd

# Load model
model = joblib.load("models/delay_risk_model.pkl")

# Create one sample input row
sample = pd.DataFrame([{
    "vehicle_type": "Truck",
    "shipment_priority": "High",
    "product_category": "Electronics",
    "weather_main": "Rain",

    "load_weight_kg": 1200.5,
    "volume_m3": 15.2,
    "base_shipping_cost": 450.0,
    "route_distance_km": 320.0,
    "estimated_travel_time_min": 410.0,
    "temperature_c": 18.5,
    "precipitation_mm": 6.2,
    "wind_speed_kmh": 22.0,
    "is_high_priority": 1
}])

# Predict
prediction = model.predict(sample)
probability = model.predict_proba(sample)

print("Prediction:", prediction)
print("Prediction probability:", probability)