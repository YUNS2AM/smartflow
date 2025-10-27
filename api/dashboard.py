"""
SmartFlow 대시보드 API
KPI, 생산 현황, 알림
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Order, Schedule, Equipment
from schemas import DashboardSummary, ProductionStatus, Alert

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """전체 요약 (KPI)"""
    total_orders = db.query(Order).count()
    pending = db.query(Order).filter(Order.status == "pending").count()
    in_progress = db.query(Order).filter(Order.status == "in_progress").count()
    completed = db.query(Order).filter(Order.status == "completed").count()
    
    # 납기 준수율 (더미)
    on_time_rate = 92.5
    utilization = 87.3
    
    return DashboardSummary(
        total_orders=total_orders,
        pending_orders=pending,
        in_progress_orders=in_progress,
        completed_orders=completed,
        on_time_rate=on_time_rate,
        equipment_utilization=utilization,
        alerts_count=3
    )

@router.get("/production")
def get_production_status(db: Session = Depends(get_db)):
    """오늘 생산 현황"""
    equipment_list = db.query(Equipment).all()
    
    status = []
    for eq in equipment_list:
        status.append({
            "machine_id": eq.machine_id,
            "current_order": "ORD-001",
            "progress": 65.0,
            "status": "in_progress"
        })
    
    return {"production_status": status}

@router.get("/alerts")
def get_alerts():
    """긴급 알림"""
    return {
        "alerts": [
            {
                "type": "deadline",
                "severity": "high",
                "message": "ORD-005 납기 2일 남음",
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "inventory",
                "severity": "medium",
                "message": "Product_c0 재고 부족",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
