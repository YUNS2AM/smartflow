"""
SmartFlow AI 수요 예측 API
XGBoost + Prophet 앙상블 모델 (더미 구현)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import random

from database import get_db
from models import Forecast
from schemas import ForecastRequest, ForecastResult

router = APIRouter()

@router.post("/predict", response_model=ForecastResult)
def predict_demand(request: ForecastRequest, db: Session = Depends(get_db)):
    """AI 수요 예측 (더미 구현)"""
    predictions = []
    dates = []
    confidence_intervals = []
    
    base_demand = random.randint(700, 900)
    
    for i in range(request.days):
        date = request.start_date + timedelta(days=i)
        prediction = int(base_demand + random.randint(-100, 100))
        predictions.append(prediction)
        dates.append(date)
        
        confidence_intervals.append({
            'date': date.isoformat(),
            'lower': int(prediction * 0.85),
            'upper': int(prediction * 1.15)
        })
    
    return ForecastResult(
        product_code=request.product_code,
        predictions=predictions,
        dates=dates,
        confidence_intervals=confidence_intervals,
        accuracy=15.2
    )
