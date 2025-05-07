from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from controller import background_removal, background_bg, background_bria, background_replace, api_keys
from model.database import create_tables

app = FastAPI()

# BRIA 배경 교체 API 라우터 등록
app.include_router(background_bria.router, prefix="/api")

# 배경 제거 및 생성 API 라우터 등록
app.include_router(background_replace.router, prefix="/api")

# CORS 미들웨어 설정 업데이트
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3000"],  # 프론트엔드 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
    expose_headers=["*"],  # 모든 응답 헤더 노출
)

# 데이터베이스 테이블 생성
create_tables()

# 업로드 폴더 확인 및 생성
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 배경 제거 결과 폴더 생성
RESULT_BG_DIR = os.path.join(os.getcwd(), "uploads", "bg_results")
if not os.path.exists(RESULT_BG_DIR):
    os.makedirs(RESULT_BG_DIR)

# 정적 파일 서빙 설정
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# API 키 관리 라우터 등록
app.include_router(api_keys.router)

# 새로운 배경 제거 API 라우터 등록
app.include_router(background_bg.router)

app.include_router(background_removal.router)

from fastapi import APIRouter


@app.get("/")
def read_root():
    return {"Hello": "world"}

@app.get("/api/health")
def health_check():
    """서버 상태 확인 엔드포인트"""
    return {"status": "ok", "message": "서버가 정상적으로 동작 중입니다."}
