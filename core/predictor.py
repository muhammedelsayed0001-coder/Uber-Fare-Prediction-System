import os
import joblib
import pandas as pd

from config import MODEL_PATH


class UberFarePredictor:
    
    #load the .pkl file containing the trained model
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at '{model_path}'. "
            )
            
        self.model = joblib.load(model_path)


    #predict takes a DataFrame with the exact columns the model expects and returns prediction fare
    def predict(self, features: pd.DataFrame) -> float:
        prediction = self.model.predict(features)
        return float(prediction[0])
