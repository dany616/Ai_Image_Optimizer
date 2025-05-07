from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

# 환경 변수 로드
load_dotenv()

# PostgreSQL 데이터베이스 설정
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ai_photo_db')

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 데이터베이스 연결 문자열 검증
if not os.getenv('DB_USER') or not os.getenv('DB_PASSWORD'):
    logger.warning("데이터베이스 사용자 이름 또는 비밀번호가 설정되지 않았습니다. .env 파일을 확인하세요.")
    logger.info(f"현재 사용 중인 데이터베이스 설정: Host={DB_HOST}, Port={DB_PORT}, DB={DB_NAME}")

# 엔진 생성
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    logger.info("데이터베이스 연결 엔진 생성 성공")
except Exception as e:
    logger.error(f"데이터베이스 연결 엔진 생성 실패: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 세션 관리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 사용자 모델
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    credits = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    images = relationship("Image", back_populates="user")
    user_images = relationship("UserImage", back_populates="user")

# 이미지 메타데이터 모델
class Image(Base):
    __tablename__ = "images"
    
    image_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    original_image_url = Column(Text, nullable=False)
    generated_image_url = Column(Text)
    background_style = Column(Text)
    model_version = Column(Text)
    processing_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="images")
    user_images = relationship("UserImage", back_populates="image")

# 사용자별 이미지 처리 기록 모델
class UserImage(Base):
    __tablename__ = "user_images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    image_id = Column(Integer, ForeignKey('images.image_id', ondelete='CASCADE'))
    credits_used = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="user_images")
    image = relationship("Image", back_populates="user_images")

# 테이블 생성 함수
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"데이터베이스 테이블 생성 실패: {str(e)}")
        raise 