"""
SmartFlow 주문 관리 API
주문 CRUD + 엑셀 업로드/다운로드 + 긴급 주문
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
from datetime import datetime

from database import get_db
from models import Order
from schemas import Order as OrderSchema, OrderCreate, OrderUpdate, UploadResponse
from core.excel_parser import parse_order_excel, create_order_template

router = APIRouter()

@router.get("/list", response_model=List[OrderSchema])
def list_orders(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    주문 목록 조회
    
    - status: 주문 상태 필터 (pending, scheduled, in_progress, completed)
    - skip: 건너뛸 개수
    - limit: 최대 조회 개수
    """
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/{order_number}", response_model=OrderSchema)
def get_order(order_number: str, db: Session = Depends(get_db)):
    """특정 주문 조회"""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order

@router.post("/create", response_model=OrderSchema)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    주문 생성
    
    필수 정보:
    - order_number: 주문 번호
    - product_code: 제품 코드
    - quantity: 수량
    - due_date: 납기일
    """
    # 중복 체크
    existing = db.query(Order).filter(Order.order_number == order.order_number).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"이미 존재하는 주문 번호: {order.order_number}"
        )
    
    # 새 주문 생성
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.put("/update/{order_number}", response_model=OrderSchema)
def update_order(
    order_number: str,
    order: OrderUpdate,
    db: Session = Depends(get_db)
):
    """주문 정보 수정"""
    db_order = db.query(Order).filter(Order.order_number == order_number).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # 업데이트
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.delete("/delete/{order_number}")
def delete_order(order_number: str, db: Session = Depends(get_db)):
    """주문 삭제"""
    db_order = db.query(Order).filter(Order.order_number == order_number).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    db.delete(db_order)
    db.commit()
    
    return {"success": True, "message": f"{order_number} 삭제 완료"}

@router.post("/urgent", response_model=OrderSchema)
def create_urgent_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    긴급 주문 추가
    
    자동으로 is_urgent=True, priority=1로 설정됨
    """
    # 긴급 주문 설정
    order_dict = order.dict()
    order_dict['is_urgent'] = True
    order_dict['priority'] = 1
    
    # 중복 체크
    existing = db.query(Order).filter(Order.order_number == order.order_number).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"이미 존재하는 주문 번호: {order.order_number}"
        )
    
    # 새 주문 생성
    db_order = Order(**order_dict)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.post("/upload", response_model=UploadResponse)
async def upload_order_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    주문 정보 엑셀 일괄 업로드
    
    필수 컬럼:
    - 주문번호
    - 제품코드
    - 수량
    - 납기일
    """
    # 파일 형식 체크
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다")
    
    # 엑셀 파싱
    orders_list = await parse_order_excel(file)
    
    # DB에 저장
    created_count = 0
    errors = []
    
    for order_data in orders_list:
        try:
            # 중복 체크
            existing = db.query(Order).filter(
                Order.order_number == order_data['order_number']
            ).first()
            
            if existing:
                # 업데이트
                for key, value in order_data.items():
                    setattr(existing, key, value)
            else:
                # 신규 생성
                db_order = Order(**order_data)
                db.add(db_order)
            
            created_count += 1
        except Exception as e:
            errors.append(f"{order_data['order_number']}: {str(e)}")
    
    db.commit()
    
    return UploadResponse(
        success=True,
        message=f"{created_count}개 주문 업로드 완료",
        count=created_count,
        errors=errors if errors else None
    )

@router.get("/download/template")
def download_order_template():
    """
    주문 정보 엑셀 템플릿 다운로드
    
    템플릿에는 예시 데이터가 포함되어 있습니다.
    """
    template = create_order_template()
    
    return StreamingResponse(
        BytesIO(template),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=주문정보_템플릿.xlsx"}
    )

@router.get("/pending/count")
def get_pending_count(db: Session = Depends(get_db)):
    """대기 중인 주문 개수"""
    count = db.query(Order).filter(Order.status == "pending").count()
    return {"count": count}

@router.get("/urgent/list", response_model=List[OrderSchema])
def list_urgent_orders(db: Session = Depends(get_db)):
    """긴급 주문 목록"""
    orders = db.query(Order).filter(Order.is_urgent == True).all()
    return orders
