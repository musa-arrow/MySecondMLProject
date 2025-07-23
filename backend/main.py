from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class PredictRequest(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    humidity: float
    rainfall: float
    ph: float
    N: float
    P: float
    K: float
    soil_type: str
    crop_type: str
    fertilizer_type: str
    pest_count: int

class PredictResponse(BaseModel):
    probability: float
    result: str
    message: str

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    # Örnek kural tabanlı mantık (dummy)
    score = 0
    if request.temperature > 15 and request.temperature < 35:
        score += 1
    if request.humidity > 40 and request.humidity < 90:
        score += 1
    if request.rainfall > 50 and request.rainfall < 300:
        score += 1
    if request.ph > 5.5 and request.ph < 7.5:
        score += 1
    if request.pest_count < 10:
        score += 1
    probability = (score / 5) * 100
    result = "olumlu" if probability > 50 else "olumsuz"
    message = f"%{int(probability)} olasılıkla {result} sonuç!"
    return PredictResponse(probability=probability, result=result, message=message) 