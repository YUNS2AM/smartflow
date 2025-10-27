"""
SmartFlow 스케줄링 API
생산 스케줄 생성 및 관리 (핵심 기능!)
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
from datetime import datetime
import pandas as pd
import time

from database import get_db
from models import Equipment, Order, Schedule
from schemas import ScheduleResponse, GanttData
from core.scheduler import ProductionScheduler

router = APIRouter()

@router.post("/generate", response_model=ScheduleResponse)
def generate_schedule(db: Session = Depends(get_db)):
    """
    생산 스케줄 생성 ⭐ 핵심 기능!
    
    프로세스:
    1. 대기 중인 주문 조회
    2. 활성 설비 조회
    3. 스케줄링 알고리즘 실행 (3초 이내 목표)
    4. 스케줄 결과 DB 저장
    5. 성능 지표 반환
    
    Returns:
        - schedule_id: 스케줄 ID
        - schedules: 스케줄 리스트
        - metrics: 성능 지표 (납기 준수율, 가동률 등)
    """
    start_time = time.time()
    
    # 1. 대기 중인 주문 조회
    orders = db.query(Order).filter(Order.status.in_(["pending", "scheduled"])).all()
    if not orders:
        raise HTTPException(status_code=404, detail="스케줄링할 주문이 없습니다")
    
    # 2. 활성 설비 조회
    equipment_list = db.query(Equipment).filter(Equipment.status == "active").all()
    if not equipment_list:
        raise HTTPException(status_code=404, detail="사용 가능한 설비가 없습니다")
    
    # 3. 데이터 변환
    orders_data = [
        {
            'order_number': order.order_number,
            'product_code': order.product_code,
            'quantity': order.quantity,
            'due_date': order.due_date.strftime('%Y-%m-%d'),
            'priority': order.priority,
            'is_urgent': order.is_urgent
        }
        for order in orders
    ]
    
    equipment_data = [
        {
            'machine_id': eq.machine_id,
            'capacity_per_hour': eq.capacity_per_hour,
            'shift_start': eq.shift_start,
            'shift_end': eq.shift_end,
            'tonnage': eq.tonnage,
            'status': eq.status
        }
        for eq in equipment_list
    ]
    
    # 4. 스케줄링 엔진 실행
    scheduler = ProductionScheduler(equipment_data, orders_data)
    result = scheduler.generate_schedule()
    
    # 5. DB에 저장
    schedule_id = result['schedule_id']
    
    for item in result['schedules']:
        # 주문 ID 찾기
        order = db.query(Order).filter(Order.order_number == item['order_number']).first()
        
        # Schedule 테이블에 저장
        db_schedule = Schedule(
            schedule_id=schedule_id,
            order_id=order.id,
            machine_id=item['machine_id'],
            start_time=datetime.fromisoformat(item['start_time']),
            end_time=datetime.fromisoformat(item['end_time']),
            duration_minutes=item['duration_minutes'],
            is_on_time=item['is_on_time']
        )
        db.add(db_schedule)
        
        # 주문 상태 업데이트
        order.status = "scheduled"
    
    db.commit()
    
    # 6. 처리 시간 계산
    elapsed = time.time() - start_time
    result['metrics']['processing_time'] = round(elapsed, 2)
    
    print(f"✅ 스케줄링 완료: {elapsed:.2f}초")
    
    return ScheduleResponse(
        schedule_id=schedule_id,
        schedules=result['schedules'],
        metrics=result['metrics'],
        generated_at=result['generated_at']
    )

@router.get("/result")
def get_schedule_result(
    schedule_id: str = None,
    db: Session = Depends(get_db)
):
    """
    스케줄 결과 조회
    
    - schedule_id가 없으면 가장 최근 스케줄 조회
    """
    query = db.query(Schedule)
    
    if schedule_id:
        query = query.filter(Schedule.schedule_id == schedule_id)
    else:
        # 가장 최근 스케줄
        latest = db.query(Schedule).order_by(Schedule.created_at.desc()).first()
        if not latest:
            raise HTTPException(status_code=404, detail="스케줄이 없습니다")
        schedule_id = latest.schedule_id
        query = query.filter(Schedule.schedule_id == schedule_id)
    
    schedules = query.all()
    
    if not schedules:
        raise HTTPException(status_code=404, detail="스케줄을 찾을 수 없습니다")
    
    # 결과 포맷팅
    result = []
    for schedule in schedules:
        order = db.query(Order).filter(Order.id == schedule.order_id).first()
        result.append({
            'order_number': order.order_number,
            'product_code': order.product_code,
            'machine_id': schedule.machine_id,
            'start_time': schedule.start_time.isoformat(),
            'end_time': schedule.end_time.isoformat(),
            'duration_minutes': schedule.duration_minutes,
            'is_on_time': schedule.is_on_time,
            'status': schedule.status
        })
    
    return {
        'schedule_id': schedule_id,
        'schedules': result
    }

@router.get("/gantt", response_model=List[GanttData])
def get_gantt_chart_data(
    schedule_id: str = None,
    db: Session = Depends(get_db)
):
    """
    간트차트용 데이터 조회
    
    Returns:
        [
            {
                'machine_id': '1호기',
                'tasks': [
                    {
                        'order_number': 'ORD-001',
                        'start': '2025-11-15T08:00:00',
                        'end': '2025-11-15T10:30:00',
                        'status': 'planned'
                    }
                ]
            }
        ]
    """
    # 스케줄 조회
    query = db.query(Schedule)
    
    if schedule_id:
        query = query.filter(Schedule.schedule_id == schedule_id)
    else:
        # 가장 최근 스케줄
        latest = db.query(Schedule).order_by(Schedule.created_at.desc()).first()
        if latest:
            query = query.filter(Schedule.schedule_id == latest.schedule_id)
    
    schedules = query.all()
    
    if not schedules:
        raise HTTPException(status_code=404, detail="스케줄이 없습니다")
    
    # 간트차트 데이터 생성
    gantt_data = {}
    
    for schedule in schedules:
        order = db.query(Order).filter(Order.id == schedule.order_id).first()
        machine_id = schedule.machine_id
        
        if machine_id not in gantt_data:
            gantt_data[machine_id] = {
                'machine_id': machine_id,
                'tasks': []
            }
        
        gantt_data[machine_id]['tasks'].append({
            'order_number': order.order_number,
            'product_code': order.product_code,
            'start': schedule.start_time.isoformat(),
            'end': schedule.end_time.isoformat(),
            'duration_minutes': schedule.duration_minutes,
            'is_on_time': schedule.is_on_time,
            'status': schedule.status
        })
    
    return list(gantt_data.values())

@router.get("/download")
def download_schedule_excel(
    schedule_id: str = None,
    db: Session = Depends(get_db)
):
    """
    스케줄 엑셀 다운로드
    
    간트차트를 엑셀로 다운로드
    """
    # 스케줄 조회
    query = db.query(Schedule)
    
    if schedule_id:
        query = query.filter(Schedule.schedule_id == schedule_id)
    else:
        latest = db.query(Schedule).order_by(Schedule.created_at.desc()).first()
        if latest:
            query = query.filter(Schedule.schedule_id == latest.schedule_id)
    
    schedules = query.all()
    
    if not schedules:
        raise HTTPException(status_code=404, detail="스케줄이 없습니다")
    
    # 데이터프레임 생성
    data = []
    for schedule in schedules:
        order = db.query(Order).filter(Order.id == schedule.order_id).first()
        data.append({
            '주문번호': order.order_number,
            '제품코드': order.product_code,
            '수량': order.quantity,
            '사출기': schedule.machine_id,
            '시작시간': schedule.start_time,
            '종료시간': schedule.end_time,
            '작업시간(분)': schedule.duration_minutes,
            '납기일': order.due_date,
            '납기준수': '준수' if schedule.is_on_time else '지연'
        })
    
    df = pd.DataFrame(data)
    
    # 엑셀 생성
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='생산 스케줄', index=False)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=생산스케줄_{schedule_id}.xlsx"}
    )

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: str, db: Session = Depends(get_db)):
    """스케줄 삭제"""
    schedules = db.query(Schedule).filter(Schedule.schedule_id == schedule_id).all()
    
    if not schedules:
        raise HTTPException(status_code=404, detail="스케줄을 찾을 수 없습니다")
    
    for schedule in schedules:
        db.delete(schedule)
    
    db.commit()
    
    return {"success": True, "message": f"스케줄 {schedule_id} 삭제 완료"}
