from fastapi import FastAPI
from controller import epics
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user_db")

# 환경 변수 로드
load_dotenv()

app = FastAPI()

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid
from datetime import datetime
import shutil
from typing import Optional

# database.py에서 모델과 세션 관리 함수 임포트
from .database import User, Image, UserImage, get_db, SQLALCHEMY_DATABASE_URL, engine, Base

# 테이블 생성
Base.metadata.create_all(bind=engine)

# 파일 저장 경로 설정
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    logger.info(f"업로드 디렉토리 생성: {UPLOAD_DIR}")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = None,  # 실제 구현시 인증 시스템에서 가져올 예정
    background_style: Optional[str] = None,
    model_version: Optional[str] = None,
    db = Depends(get_db)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    
    # 사용자 확인
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 크레딧 확인
    if user.credits < 1:  # 최소 크레딧 체크
        raise HTTPException(status_code=400, detail="크레딧이 부족합니다")
    
    # UUID 생성 및 파일 저장
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 이미지 메타데이터 저장
    new_image = Image(
        user_id=user_id,
        original_image_url=file_path,
        background_style=background_style,
        model_version=model_version
    )
    db.add(new_image)
    db.flush()
    
    # 사용자 이미지 처리 기록 저장
    user_image = UserImage(
        user_id=user_id,
        image_id=new_image.image_id,
        credits_used=1  # 기본 크레딧 사용량
    )
    db.add(user_image)
    
    # 사용자 크레딧 차감
    user.credits -= 1
    
    db.commit()
    
    return {
        "image_id": new_image.image_id,
        "file_path": file_path,
        "remaining_credits": user.credits,
        "message": "이미지가 성공적으로 업로드되었습니다"
    }

@app.get("/test-db")
async def test_db(db = Depends(get_db)):
    try:
        # 데이터베이스에 간단한 쿼리 실행
        result = db.execute("SELECT 1").fetchone()
        # 비밀번호 가림 처리
        sanitized_db_url = SQLALCHEMY_DATABASE_URL.replace(
            os.getenv('DB_PASSWORD', ''), '********'
        )
        return {
            "message": "데이터베이스 연결 성공!",
            "result": result[0] if result else None,
            "database_url": sanitized_db_url
        }
    except Exception as e:
        # 비밀번호 가림 처리
        sanitized_db_url = SQLALCHEMY_DATABASE_URL.replace(
            os.getenv('DB_PASSWORD', ''), '********'
        )
        raise HTTPException(
            status_code=500, 
            detail={
                "error": str(e),
                "type": str(type(e)),
                "database_url": sanitized_db_url
            }
        )

app.include_router(epics.router)
@app.get("/")
def read_root():
    return{"hello":"in world"}

## def st():
##    return FileResponse('index.html')

@app.get("/data")
def st2():
    return {'Hello, :1234'}

#from pydantic import BaseModel
#class Model(BaseModel):
#    name = str
#    phone = int* 
