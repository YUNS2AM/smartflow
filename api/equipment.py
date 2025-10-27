"""
SmartFlow 설비 관리 API
설비 CRUD + 엑셀 업로드/다운로드
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO

from database import get_db
from models import Equipment
from schemas import Equipment as EquipmentSchema, EquipmentCreate, EquipmentUpdate, UploadResponse
from core.excel_parser import parse_equipment_excel, create_equipment_template

router = APIRouter()

@router.get("/list", response_model=List[EquipmentSchema])
def list_equipment(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    설비 목록 조회
    
    - skip: 건너뛸 개수
    - limit: 최대 조회 개수
    """
    equipment_list = db.query(Equipment).offset(skip).limit(limit).all()
    return equipment_list

@router.get("/{machine_id}", response_model=EquipmentSchema)
def get_equipment(machine_id: str, db: Session = Depends(get_db)):
    """특정 설비 조회"""
    equipment = db.query(Equipment).filter(Equipment.machine_id == machine_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="설비를 찾을 수 없습니다")
    return equipment

@router.post("/create", response_model=EquipmentSchema)
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """
    설비 추가
    
    필수 정보:
    - machine_id: 설비 번호 (예: "1호기")
    - tonnage: 톤수
    - capacity_per_hour: 시간당 생산능력
    - shift_start: 가동 시작 시간
    - shift_end: 가동 종료 시간
    """
    # 중복 체크
    existing = db.query(Equipment).filter(Equipment.machine_id == equipment.machine_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"이미 존재하는 설비 번호: {equipment.machine_id}")
    
    # 새 설비 생성
    db_equipment = Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    
    return db_equipment

@router.put("/update/{machine_id}", response_model=EquipmentSchema)
def update_equipment(
    machine_id: str,
    equipment: EquipmentUpdate,
    db: Session = Depends(get_db)
):
    """설비 정보 수정"""
    db_equipment = db.query(Equipment).filter(Equipment.machine_id == machine_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="설비를 찾을 수 없습니다")
    
    # 업데이트
    update_data = equipment.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    
    return db_equipment

@router.delete("/delete/{machine_id}")
def delete_equipment(machine_id: str, db: Session = Depends(get_db)):
    """설비 삭제"""
    db_equipment = db.query(Equipment).filter(Equipment.machine_id == machine_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="설비를 찾을 수 없습니다")
    
    db.delete(db_equipment)
    db.commit()
    
    return {"success": True, "message": f"{machine_id} 삭제 완료"}

@router.post("/upload", response_model=UploadResponse)
async def upload_equipment_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    설비 정보 엑셀 일괄 업로드
    
    필수 컬럼:
    - 사출기번호
    - 톤수
    - 가동시간_시작
    - 가동시간_종료
    - 생산능력_개_시간
    """
    # 파일 형식 체크
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다")
    
    # 엑셀 파싱
    equipment_list = await parse_equipment_excel(file)
    
    # DB에 저장
    created_count = 0
    errors = []
    
    for eq_data in equipment_list:
        try:
            # 중복 체크
            existing = db.query(Equipment).filter(
                Equipment.machine_id == eq_data['machine_id']
            ).first()
            
            if existing:
                # 업데이트
                for key, value in eq_data.items():
                    setattr(existing, key, value)
            else:
                # 신규 생성
                db_equipment = Equipment(**eq_data)
                db.add(db_equipment)
            
            created_count += 1
        except Exception as e:
            errors.append(f"{eq_data['machine_id']}: {str(e)}")
    
    db.commit()
    
    return UploadResponse(
        success=True,
        message=f"{created_count}개 설비 업로드 완료",
        count=created_count,
        errors=errors if errors else None
    )

@router.get("/download/template")
def download_equipment_template():
    """
    설비 정보 엑셀 템플릿 다운로드
    
    템플릿에는 예시 데이터가 포함되어 있습니다.
    """
    template = create_equipment_template()
    
    return StreamingResponse(
        BytesIO(template),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=설비정보_템플릿.xlsx"}
    )
