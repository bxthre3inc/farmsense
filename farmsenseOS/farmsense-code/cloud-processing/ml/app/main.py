
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from app.model_stubs import predict_yield, predict_moisture_trend
import uvicorn

app = FastAPI(
    title="FarmSense ML Prediction Service",
    description="Agricultural AI/ML Microservice",
    version="1.0.0"
)

@app.get("/predict/yield/{field_id}")
async def get_yield_prediction(field_id: str):
    """Predict crop yield for a specific field"""
    try:
        prediction = predict_yield(field_id)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/moisture-trend")
async def get_moisture_trend(field_id: str):
    """Predict moisture trend for the next 48 hours for a field"""
    # In a real app, we'd fetch actual sensor history here
    # Mock sensor history
    mock_history = [
        {"moisture": 0.25}, {"moisture": 0.24}, {"moisture": 0.23}
    ]
    try:
        trends = predict_moisture_trend(mock_history)
        return {
            "field_id": field_id,
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml-prediction"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
