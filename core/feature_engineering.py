# Turns raw user input into the exact feature row the RandomForestRegressor was trained on
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from config import FEATURE_COLUMNS, DAY_DUMMY_COLUMNS, DAY_NAME_MAP
from features.geo_features import haversine, calculate_bearing, NYC_CENTER

#Everything the user picked on the UI, before feature engineering

@dataclass 
#dataclass is a convenient way to create a class whose main purpose is to store data
#Python automatically creates __init__()
class TripRequest:
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    passenger_count: int
    pickup_datetime: datetime

# a class that takes a TripRequest and returns a single-row DataFrame with the exact columns the model expects
class FeatureEngineer:
  
    def transform(self, trip: TripRequest) -> pd.DataFrame:
        row = self._engineer_raw_features(trip)
        row.update(self._engineer_day_dummies(trip.pickup_datetime))
        return pd.DataFrame([row], columns=FEATURE_COLUMNS)




    #returns summary info for UI appears after user clicks predict
    def trip_summary(self, trip: TripRequest) -> dict:
        raw = self._engineer_raw_features(trip)
        dow = trip.pickup_datetime.weekday()
        
        return {
            "trip_distance_km": round(raw["trip_distance_km"], 2),
            "bearing_deg": round(raw["bearing"], 1),
            "pickup_dist_from_center_km": round(raw["pickup_dist_from_center"], 2),
            "dropoff_dist_from_center_km": round(raw["dropoff_dist_from_center"], 2),
            "hour": raw["hour"],
            "day_name": DAY_NAME_MAP[dow].capitalize(),
            "month": raw["month"],
            "year": raw["year"],
            "is_weekend": bool(raw["is_weekend"]),
            "is_rush_hour": bool(raw["is_rush_hour"]),
        }




    #calls your haversine/calculate_bearing functions, computes hour/day/month/rush-hour/weekend
    @staticmethod #This function belongs to the class for organization, but it doesn't need an instance (self)
    def _engineer_raw_features(trip: TripRequest) -> dict:
        distance_km = haversine(
            trip.pickup_lat, trip.pickup_lon, trip.dropoff_lat, trip.dropoff_lon
        )
        bearing = calculate_bearing(
            trip.pickup_lat, trip.pickup_lon, trip.dropoff_lat, trip.dropoff_lon
        )
        pickup_dist_center = haversine(trip.pickup_lat, trip.pickup_lon, *NYC_CENTER)
        dropoff_dist_center = haversine(trip.dropoff_lat, trip.dropoff_lon, *NYC_CENTER)

        hour = trip.pickup_datetime.hour
        dow = trip.pickup_datetime.weekday()
        month = trip.pickup_datetime.month
        year = trip.pickup_datetime.year
        is_weekend = int(dow >= 5)
        is_rush_hour = int((7 <= hour <= 9) or (16 <= hour <= 19))

        return {
            "pickup_longitude": trip.pickup_lon,
            "pickup_latitude": trip.pickup_lat,
            "dropoff_longitude": trip.dropoff_lon,
            "dropoff_latitude": trip.dropoff_lat,
            "passenger_count": trip.passenger_count,
            "trip_distance_km": distance_km,
            "bearing": bearing,
            "pickup_dist_from_center": pickup_dist_center,
            "dropoff_dist_from_center": dropoff_dist_center,
            "hour": hour,
            "month": month,
            "year": year,
            "is_weekend": is_weekend,
            "is_rush_hour": is_rush_hour,
        }

    # convert the day of the week into one-hot encoded variables
    @staticmethod
    def _engineer_day_dummies(pickup_datetime: datetime) -> dict:
        day_name = DAY_NAME_MAP[pickup_datetime.weekday()]
        active_col = f"is_{day_name}"
        return {col: int(col == active_col) for col in DAY_DUMMY_COLUMNS}
