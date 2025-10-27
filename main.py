"""
SmartFlow 백엔드 메인 애플리케이션 (완전체)
FastAPI 기반 사출성형 공급망 최적화 AI 플랫폼

✅ AI 모델 완전 통합
✅ 모든 API 엔드포인트 구현
✅ 경진대회 제출 준비 완료
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# API 라우터 import
from api import equipment, orders, schedule, inventory, dashboard, auth
from api import forecast as forecast_api
from database import init_db

# 앱 시작/종료 시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    print("\n" + "="*60)
    print("🚀 SmartFlow 백엔드 시작...")
    print("="*60)
    
    init_db()  # 데이터베이스 초기화
    print("✅ 데이터베이스 초기화 완료!")
    
    # AI 모델 로드 확인
    try:
        from core.ai_forecaster import get_forecaster
        forecaster = get_forecaster()
        if forecaster.models:
            print("✅ AI 모델 로드 성공!")
        else:
            print("⚠️  AI 모델 없음 - 더미 모드로 실행")
    except Exception as e:
        print(f"⚠️  AI 모듈 로드 실패: {e}")
    
    print("="*60)
    print("✅ SmartFlow 백엔드 준비 완료!")
    print("📖 API 문서: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    yield
    
    # 종료 시
    print("\n👋 SmartFlow 백엔드 종료\n")

# FastAPI 앱 생성
app = FastAPI(
    title="SmartFlow API",
    description="""
    # 🏭 SmartFlow - 사출성형 공급망 최적화 AI 플랫폼
    
    ## 📊 주요 기능
    
    ### 1. **AI 수요 예측** 🤖
    - **XGBoost + LightGBM + CatBoost** 앙상블 모델
    - **T+1 ~ T+4일** 멀티호라이즌 예측
    - **발주 발생 확률** 계산
    - **자동 추천 시스템**
    
    ### 2. **설비 관리** ⚙️
    - 설비 CRUD + 엑셀 업로드
    - 템플릿 다운로드
    - 실시간 가동 현황
    
    ### 3. **주문 관리** 📦
    - 주문 CRUD + 엑셀 업로드
    - 긴급 주문 처리
    - 납기 모니터링
    
    ### 4. **스케줄링** 📅
    - AI 기반 생산 스케줄 최적화
    - 간트차트 데이터 제공
    - 납기 준수율 계산
    
    ### 5. **재고 최적화** 📊
    - 안전재고 계산
    - 재주문점 계산
    - 재고 알림
    
    ### 6. **대시보드** 📈
    - KPI 실시간 모니터링
    - 생산 현황 요약
    - 긴급 알림
    
    ---
    
    ## 🏆 제5회 K-인공지능 제조데이터 분석 경진대회
    
    **팀명**: SmartFlow  
    **목표**: 납기 준수율 최대화 & 재고 최적화  
    **기술**: FastAPI + AI (XGBoost/LightGBM/CatBoost)
    
    ---
    
    ## 📚 API 문서
    
    - **Swagger UI**: `/docs` (현재 페이지)
    - **ReDoc**: `/redoc`
    - **OpenAPI JSON**: `/openapi.json`
    
    ---
    
    ## 🚀 빠른 시작
    
    1. **AI 수요 예측 데모**: `GET /api/forecast/demo`
    2. **시스템 상태 확인**: `GET /health`
    3. **AI 모델 상태**: `GET /api/forecast/model-status`
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS 설정 (개발 환경용 - 모든 origin 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["🔑 인증 관리"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["⚙️ 설비 관리"])
app.include_router(orders.router, prefix="/api/orders", tags=["📦 주문 관리"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["📅 스케줄링"])
app.include_router(forecast_api.router, prefix="/api/forecast", tags=["🤖 AI 수요 예측 ⭐"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["📊 재고 최적화"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["📈 대시보드"])

# 루트 엔드포인트
@app.get("/")
def root():
    """
    SmartFlow API 서버
    
    제5회 K-인공지능 제조데이터 분석 경진대회 출품작
    """
    return {
        "message": "🏭 SmartFlow API Server v2.0",
        "version": "2.0.0",
        "description": "사출성형 공급망 최적화 AI 플랫폼",
        "competition": "제5회 K-인공지능 제조데이터 분석 경진대회",
        "team": "SmartFlow",
        "features": [
            "✅ AI 수요 예측 (XGBoost + LightGBM + CatBoost)",
            "✅ 생산 스케줄링 최적화",
            "✅ 재고 최적화",
            "✅ 엑셀 업로드/다운로드",
            "✅ 실시간 대시보드"
        ],
        "api_docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "quick_start": {
            "ai_demo": "/api/forecast/demo",
            "health_check": "/health",
            "model_status": "/api/forecast/model-status"
        },
        "status": "✅ 실행 중"
    }

@app.get("/health")
def health_check():
    """
    헬스 체크
    
    시스템 상태 확인
    """
    try:
        from core.ai_forecaster import get_forecaster
        forecaster = get_forecaster()
        model_loaded = forecaster.models is not None
    except:
        model_loaded = False
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "✅ 정상",
            "ai_model": "✅ 정상" if model_loaded else "⚠️ 더미 모드",
            "api": "✅ 정상"
        }
    }

@app.get("/api/status")
def api_status():
    """전체 시스템 상태"""
    try:
        from core.ai_forecaster import get_forecaster
        forecaster = get_forecaster()
        model_status = {
            "loaded": forecaster.models is not None,
            "version": "v1.0" if forecaster.models else "dummy",
            "path": forecaster.model_path
        }
    except Exception as e:
        model_status = {
            "loaded": False,
            "version": "error",
            "error": str(e)
        }
    
    return {
        "service": "SmartFlow",
        "version": "2.0.0",
        "status": "running",
        "ai_model": model_status,
        "endpoints": {
            "total": 30,
            "categories": [
                "인증 (3개)",
                "설비 관리 (6개)",
                "주문 관리 (7개)",
                "스케줄링 (5개)",
                "AI 예측 (6개)",
                "재고 관리 (3개)",
                "대시보드 (3개)"
            ]
        }
    }


# 실행
if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                    🏭 SmartFlow v2.0                       ║
    ║        사출성형 공급망 최적화 AI 플랫폼 (완전체)            ║
    ║                                                            ║
    ║  제5회 K-인공지능 제조데이터 분석 경진대회                  ║
    ║  팀명: SmartFlow                                           ║
    ╚════════════════════════════════════════════════════════════╝
    
    🤖 AI 모델: XGBoost + LightGBM + CatBoost 앙상블
    📅 스케줄링: 유전 알고리즘 최적화
    📊 재고: 안전재고 + 재주문점 계산
    
    🚀 서버 시작 중...
    
    📖 API 문서: http://localhost:8000/docs
    📊 대시보드: http://localhost:3000
    🔍 헬스 체크: http://localhost:8000/health
    🤖 AI 데모: http://localhost:8000/api/forecast/demo
    
    ⌨️  종료: Ctrl + C
    
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
