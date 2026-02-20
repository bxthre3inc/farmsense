import random
from datetime import datetime, timedelta

def predict_yield(field_id: str, history_days: int = 30):
    """
    Mock yield prediction based on historical stability.
    In production, this would use a Random Forest or LSTM model.
    """
    # Simulate a baseline yield and some variability
    base_yield = 180.0 # bushels/acre
    variability = random.uniform(-15.0, 15.0)
    confidence = random.uniform(0.85, 0.96)
    
    return {
        "field_id": field_id,
        "predicted_yield_bu_acre": round(base_yield + variability, 2),
        "confidence_score": round(confidence, 3),
        "prediction_date": datetime.utcnow().isoformat(),
        "model_version": "yield-v1.2.0-baseline"
    }

def predict_moisture_trend(sensor_readings: list):
    """
    Mock moisture trend prediction for the next 48 hours.
    """
    if not sensor_readings:
        return []
    
    current_avg = sum(r['moisture'] for r in sensor_readings) / len(sensor_readings)
    predictions = []
    
    for i in range(1, 49):
        # Apply a simple decay and some noise
        decay = 0.002 * i
        noise = random.uniform(-0.005, 0.005)
        predicted_val = max(0, current_avg - decay + noise)
        
        predictions.append({
            "hour": i,
            "moisture_predicted": round(predicted_val, 4),
            "timestamp": (datetime.utcnow() + timedelta(hours=i)).isoformat()
        })
        
    return predictions
