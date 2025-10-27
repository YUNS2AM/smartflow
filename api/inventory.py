"""
SmartFlow 재고 최적화 API
안전재고, 재주문점, 발주량 계산
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import random

from database import get_db
from schemas import InventoryPolicy, InventoryStatus

router = APIRouter()

@router.post("/calculate", response_model=InventoryPolicy)
def calculate_inventory_policy(product_code: str, avg_demand: int = 800, db: Session = Depends(get_db)):
    """재고 정책 계산 (더미)"""
    safety_stock = int(avg_demand * 0.3)
    reorder_point = int(avg_demand * 0.5)
    recommended_order_qty = int(avg_demand * 1.5)
    
    return InventoryPolicy(
        product_code=product_code,
        safety_stock=safety_stock,
        reorder_point=reorder_point,
        recommended_order_qty=recommended_order_qty,
        lead_time_days=7,
        service_level=0.95
    )

@router.get("/status/{product_code}", response_model=InventoryStatus)
def get_inventory_status(product_code: str):
    """제품별 재고 상태 (더미)"""
    current = random.randint(500, 1200)
    safety = 300
    reorder = 500
    
    if current < safety:
        status = "critical"
        action = "즉시 발주 필요!"
    elif current < reorder:
        status = "warning"
        action = "발주 고려"
    else:
        status = "safe"
        action = "정상"
    
    return InventoryStatus(
        product_code=product_code,
        current_stock=current,
        safety_stock=safety,
        reorder_point=reorder,
        status=status,
        recommended_action=action
    )

@router.get("/alerts")
def get_inventory_alerts():
    """재고 알림 목록 (더미)"""
    return {
        "alerts": [
            {"product_code": "Product_c0", "type": "warning", "message": "재고 부족"},
            {"product_code": "Product_c15", "type": "critical", "message": "긴급 발주 필요"}
        ]
    }
