#its purpose is to store constants fixed values that are shared across multiple files
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "predictions.db")

MODEL_PATH = os.path.join(BASE_DIR, "models", "uber_rf_model.pkl")
# MODEL_PATH = "C:\\Users\\Hp\\Documents\\Uber_Project\\models\\uber_rf_model.pkl" 
# It works no matter where you run the program from in any operating system



NYC_CENTER = (40.7128, -74.0060)
DEFAULT_ZOOM = 12

LAT_BOUNDS = (39.0, 42.0)
LON_BOUNDS = (-75.0, -72.0)


DAY_DUMMY_COLUMNS = [
    "is_friday", "is_monday", "is_saturday", "is_sunday",
    "is_thursday", "is_tuesday", "is_wednesday",
]

# Exact column order the RandomForestRegressor was fit on Reggressors notebook ,Prediction input must match with it 
FEATURE_COLUMNS = [
    "pickup_longitude", "pickup_latitude",
    "dropoff_longitude", "dropoff_latitude",
    "passenger_count", "trip_distance_km", "bearing",
    "pickup_dist_from_center", "dropoff_dist_from_center",
    "hour", "month", "year", "is_weekend", "is_rush_hour",
] + DAY_DUMMY_COLUMNS

DAY_NAME_MAP = {
    0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
    4: "friday", 5: "saturday", 6: "sunday",
}
