"""
SmartFlow 데이터베이스 설정
SQLite를 사용하며, 프로덕션에서는 PostgreSQL로 변경 가능
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./smartflow.db"

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite 전용
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()

# 의존성: DB 세션 가져오기
def get_db():
    """
    FastAPI 의존성으로 사용
    각 요청마다 DB 세션을 생성하고 종료
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 초기화
def init_db():
    """
    모든 테이블 생성
    """
    from models import Equipment, Order, Schedule, Forecast, InventoryPolicy, User
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 초기화 완료!")
