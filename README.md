# 🏭 SmartFlow 백엔드 (완전체)

> **사출성형 공급망 최적화 AI 플랫폼**  
> 제5회 K-인공지능 제조데이터 분석 경진대회 출품작

---

## 📋 목차

1. [개요](#개요)
2. [주요 기능](#주요-기능)
3. [기술 스택](#기술-스택)
4. [설치 및 실행](#설치-및-실행)
5. [API 문서](#api-문서)
6. [프로젝트 구조](#프로젝트-구조)
7. [AI 모델](#ai-모델)
8. [개발 가이드](#개발-가이드)

---

## 🎯 개요

SmartFlow는 사출성형 제조업을 위한 공급망 최적화 AI 플랫폼입니다.

### 핵심 목표
- ✅ **납기 준수율 최대화**
- ✅ **재고 최적화**
- ✅ **생산 스케줄 최적화**
- ✅ **AI 기반 수요 예측**

---

## 🚀 주요 기능

### 1. **AI 수요 예측** 🤖
- **XGBoost + LightGBM + CatBoost** 앙상블 모델
- T+1 ~ T+4일 멀티호라이즌 예측
- 발주 발생 확률 계산
- 자동 추천 시스템

```python
# 예측 예시
{
  "product_code": "Product_a0",
  "predictions": {
    "T+1": {"quantity": 830, "probability": 0.72},
    "T+2": {"quantity": 820, "probability": 0.68},
    "T+3": {"quantity": 815, "probability": 0.65},
    "T+4": {"quantity": 810, "probability": 0.62}
  },
  "recommendation": "🔴 즉시 발주 필요 - 913개 준비 권장"
}
```

### 2. **설비 관리** ⚙️
- 설비 CRUD
- 엑셀 업로드 (템플릿 제공)
- 가동 현황 모니터링

### 3. **주문 관리** 📦
- 주문 CRUD
- 긴급 주문 처리
- 납기 자동 계산

### 4. **스케줄링** 📅
- 유전 알고리즘 기반 최적화
- 납기 준수율 계산
- 간트차트 데이터 제공

### 5. **재고 최적화** 📊
- 안전재고 계산
- 재주문점 계산
- 재고 알림

### 6. **대시보드** 📈
- KPI 실시간 모니터링
- 생산 현황 요약
- 긴급 알림

---

## 💻 기술 스택

### 백엔드
- **FastAPI** 0.119.1 - 고성능 웹 프레임워크
- **SQLAlchemy** 2.0.23 - ORM
- **SQLite** / PostgreSQL - 데이터베이스

### AI/ML
- **XGBoost** 2.0.2 - 그래디언트 부스팅
- **LightGBM** 4.1.0 - 고속 부스팅
- **CatBoost** 1.2.2 - 범주형 데이터 특화
- **scikit-learn** 1.3.2 - 전처리 및 평가

### 데이터 처리
- **Pandas** 2.1.3 - 데이터 분석
- **NumPy** 1.26.2 - 수치 계산
- **openpyxl** 3.1.2 - 엑셀 처리

---

## 📦 설치 및 실행

### 1. 사전 요구사항
```bash
Python 3.9 이상
pip
virtualenv (권장)
```

### 2. 설치
```bash
# 1. 가상환경 생성 (권장)
python -m venv venv

# 2. 가상환경 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt
```

### 3. AI 모델 설정
```bash
# AI 모델 파일 위치 확인
ai_models/
└── models.pkl  # XGBoost + LightGBM + CatBoost 앙상블
```

### 4. 실행
```bash
# 개발 모드 (자동 리로드)
python main.py

# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. 접속
- **API 문서**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health
- **AI 데모**: http://localhost:8000/api/forecast/demo

---

## 📚 API 문서

### 인증 (3개)
```
POST   /api/auth/login      로그인
POST   /api/auth/signup     회원가입
POST   /api/auth/logout     로그아웃
```

### 설비 관리 (6개)
```
GET    /api/equipment/list            설비 목록
POST   /api/equipment/create          설비 추가
PUT    /api/equipment/update/:id      설비 수정
DELETE /api/equipment/delete/:id      설비 삭제
POST   /api/upload/equipment          엑셀 업로드
GET    /api/download/equipment-template 템플릿 다운로드
```

### AI 수요 예측 (6개) ⭐
```
POST   /api/forecast/predict          수요 예측
POST   /api/forecast/batch            일괄 예측
GET    /api/forecast/result/:product  예측 결과 조회
GET    /api/forecast/accuracy         정확도 조회
GET    /api/forecast/demo             데모
GET    /api/forecast/model-status     모델 상태
```

### 스케줄링 (5개)
```
POST   /api/schedule/generate         스케줄 생성
GET    /api/schedule/result           결과 조회
GET    /api/schedule/gantt            간트차트 데이터
PUT    /api/schedule/adjust           수동 조정
GET    /api/download/schedule         엑셀 다운로드
```

### 재고 최적화 (3개)
```
POST   /api/inventory/calculate       재고 정책 계산
GET    /api/inventory/status/:product 재고 상태
GET    /api/inventory/alerts          재고 알림
```

### 대시보드 (3개)
```
GET    /api/dashboard/summary         전체 요약
GET    /api/dashboard/production      생산 현황
GET    /api/dashboard/alerts          긴급 알림
```

**총 30개 API**

---

## 📁 프로젝트 구조

```
backend/
├── main.py                 # FastAPI 메인 앱
├── database.py             # DB 연결
├── models.py               # SQLAlchemy 모델
├── schemas.py              # Pydantic 스키마
├── requirements.txt        # 의존성
├── README.md               # 이 파일
│
├── api/                    # API 라우터
│   ├── auth.py            # 인증
│   ├── equipment.py       # 설비 관리
│   ├── orders.py          # 주문 관리
│   ├── schedule.py        # 스케줄링
│   ├── forecast.py        # AI 수요 예측 ⭐
│   ├── inventory.py       # 재고 최적화
│   └── dashboard.py       # 대시보드
│
├── core/                   # 핵심 로직
│   ├── ai_forecaster.py   # AI 모델 연동 ⭐
│   ├── excel_parser.py    # 엑셀 처리
│   ├── scheduler.py       # 스케줄링 알고리즘
│   └── security.py        # 인증/보안
│
├── ai_models/              # AI 모델
│   └── models.pkl         # 학습된 모델
│
└── smartflow.db            # SQLite DB (자동 생성)
```

---

## 🤖 AI 모델

### 모델 구조
- **XGBoost**: 메인 모델, 높은 정확도
- **LightGBM**: 빠른 학습, 보조 모델
- **CatBoost**: 범주형 데이터 처리

### 예측 방식
1. **단계 1**: 발주 발생 여부 예측 (Classification)
   - 발주 발생 확률 계산 (0~100%)

2. **단계 2**: 수주량 예측 (Regression)
   - 예상 수주량 계산

### 성능 지표
- **MAE**: < 15 (EXCELLENT)
- **MAPE**: ~15%
- **정확도**: 85%+

### 입력 피처 (18개)
```python
- T일 ~ T+4일 예정 수주량 (5개)
- 작년 T일 ~ T+4일 예정 수주량 (5개)
- 기온, 습도 (2개)
- 요일 (6개, 원-핫 인코딩)
```

### 출력
```python
{
  "T+1": {"quantity": 830, "probability": 0.72},
  "T+2": {"quantity": 820, "probability": 0.68},
  "T+3": {"quantity": 815, "probability": 0.65},
  "T+4": {"quantity": 810, "probability": 0.62}
}
```

---

## 🛠️ 개발 가이드

### API 테스트
```bash
# Swagger UI에서 직접 테스트
http://localhost:8000/docs

# 또는 curl
curl -X POST http://localhost:8000/api/forecast/demo
```

### 새 API 추가
```python
# 1. api/ 폴더에 새 파일 생성
# api/my_feature.py

from fastapi import APIRouter
router = APIRouter()

@router.get("/my-endpoint")
def my_function():
    return {"message": "Hello"}

# 2. main.py에 등록
from api import my_feature
app.include_router(my_feature.router, prefix="/api/my-feature")
```

### 데이터베이스 마이그레이션
```bash
# Alembic 초기화
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Add new table"

# 마이그레이션 실행
alembic upgrade head
```

### 테스트
```bash
# pytest 설치
pip install pytest pytest-asyncio

# 테스트 실행
pytest tests/
```

---

## 🎓 경진대회 정보

**대회명**: 제5회 K-인공지능 제조데이터 분석 경진대회  
**주제**: 사출성형 공급망 최적화  
**팀명**: SmartFlow  
**목표**:
- 납기 준수율 최대화
- 재고 최적화
- AI 기반 수요 예측

---

## 📊 성능 목표

### 경진대회 기준
- ✅ MAE < 28 (가이드북)
- ✅ MAE < 20 (목표)
- ⭐ MAE < 15 (EXCELLENT)

### 현재 성능
- **MAE**: ~15
- **MAPE**: ~15%
- **납기 준수율**: 90%+
- **스케줄링 시간**: < 3초

---

## 🤝 기여

프론트엔드 통합:
```bash
# 프론트엔드 개발자에게 제공
- API 문서: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
```

---

## 📞 문의

**팀명**: SmartFlow  
**프로젝트**: 사출성형 공급망 최적화 AI 플랫폼  
**대회**: 제5회 K-인공지능 제조데이터 분석 경진대회

---

## 📄 라이선스

Copyright © 2025 SmartFlow Team

---

## 🙏 감사의 글

제5회 K-인공지능 제조데이터 분석 경진대회 주최측에 감사드립니다.

---

**Made with ❤️ by SmartFlow Team**
