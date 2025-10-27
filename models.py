"""
SmartFlow 데이터베이스 모델
SQLAlchemy ORM 모델 정의
"""
from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, Time
from sqlalchemy.sql import func
from database import Base

class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    company_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Equipment(Base):
    """설비 정보 테이블"""
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(50), unique=True, index=True)  # "1호기", "2호기"
    machine_name = Column(String(100))
    tonnage = Column(Integer)  # 톤수
    capacity_per_hour = Column(Integer)  # 시간당 생산능력
    shift_start = Column(String(10))  # "08:00"
    shift_end = Column(String(10))  # "18:00"
    status = Column(String(20), default="active")  # active, maintenance, inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Order(Base):
    """주문 정보 테이블"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    product_code = Column(String(50), index=True)
    product_name = Column(String(100))
    quantity = Column(Integer)
    due_date = Column(Date)
    priority = Column(Integer, default=1)  # 1=높음, 5=낮음
    status = Column(String(20), default="pending")  # pending, scheduled, in_progress, completed
    is_urgent = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Schedule(Base):
    """스케줄 결과 테이블"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(50), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    machine_id = Column(String(50))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    is_on_time = Column(Boolean)
    status = Column(String(20), default="planned")  # planned, in_progress, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Forecast(Base):
    """예측 결과 테이블"""
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), index=True)
    forecast_date = Column(Date)
    predicted_demand = Column(Integer)
    confidence_lower = Column(Integer)
    confidence_upper = Column(Integer)
    actual_demand = Column(Integer, nullable=True)
    mape = Column(Float, nullable=True)
    model_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InventoryPolicy(Base):
    """재고 정책 테이블"""
    __tablename__ = "inventory_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, index=True)
    safety_stock = Column(Integer)  # 안전재고
    reorder_point = Column(Integer)  # 재주문점
    recommended_order_qty = Column(Integer)  # 추천 발주량
    lead_time_days = Column(Integer)  # 리드타임
    service_level = Column(Float, default=0.95)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
