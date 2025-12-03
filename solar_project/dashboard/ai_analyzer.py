import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

class SolarOptimizer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def prepare_features(self, weather_data, solar_data):
        """Prepare features for ML model"""
        features = []
        for w, s in zip(weather_data, solar_data):
            feature_vector = [
                w['temperature'],
                w['cloud_coverage_percent'],
                w['wind_speed_kmh'],
                w['humidity_percent'],
                w['uv_index'],
                s['efficiency_percent'],
                s['temperature_c'],
            ]
            features.append(feature_vector)
        return np.array(features)
    
    def train_model(self, features, outputs):
        """Train ML model with historical data"""
        if len(features) > 10:
            scaled_features = self.scaler.fit_transform(features)
            self.model.fit(scaled_features, outputs)
            self.is_trained = True
    
    def predict_optimal_hours(self, weather_forecast):
        """Predict optimal hours for solar usage"""
        if not self.is_trained or len(weather_forecast) < 24:
            return self._default_recommendation()
        
        predictions = []
        for weather in weather_forecast:
            feature = np.array([[
                weather.get('temperature', 20),
                weather.get('cloud_coverage_percent', 50),
                weather.get('wind_speed_kmh', 10),
                weather.get('humidity_percent', 60),
                weather.get('uv_index', 5),
                85.0, 45.0,
            ]])
            scaled = self.scaler.transform(feature)
            pred = self.model.predict(scaled)[0]
            predictions.append(max(0, pred))
        
        # Find peak hours
        peak_idx = np.argmax(predictions)
        optimal_start = peak_idx
        optimal_end = min(peak_idx + 4, 23)
        
        return {
            'start': optimal_start,
            'end': optimal_end,
            'predicted_output': float(np.mean(predictions[optimal_start:optimal_end+1])),
            'confidence': float(np.max(predictions) / 100),
        }
    
    def generate_recommendation(self, optimization):
        """Generate human-readable recommendation"""
        start = optimization['start']
        end = optimization['end']
        output = optimization['predicted_output']
        
        if output > 70:
            suggestion = f"Excellent conditions! Peak usage window is {start}:00-{end}:00. Use high-consumption appliances (EV charging, water heater, etc.)"
        elif output > 50:
            suggestion = f"Good conditions. Optimal window is {start}:00-{end}:00. Schedule moderate loads."
        else:
            suggestion = f"Moderate conditions. Limited solar available. Use grid or battery backup during {start}:00-{end}:00."
        
        return suggestion
    
    def _default_recommendation(self):
        """Return default when model not trained"""
        return {
            'start': 9,
            'end': 16,
            'predicted_output': 50.0,
            'confidence': 0.5,
        }