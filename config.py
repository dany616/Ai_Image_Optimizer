# PostgreSQL 연결 설정
import os
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config")

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ai_photo_db')

# 데이터베이스 연결 문자열
PGSQL_TEST_DATABASE_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 커넥션 풀 설정
PGSQL_TEST_POOL_MIN_SIZE = 1
PGSQL_TEST_POOL_MAX_SIZE = 5
PGSQL_TEST_POOL_MAX_IDLE = 10

# Remove.bg API 설정
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY", "")

# BRIA API 설정
BRIA_API_TOKEN = os.getenv("BRIA_API_TOKEN", "")

# AWS S3 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# API 키가 설정되어 있는지 확인
if not REMOVE_BG_API_KEY:
    logger.warning("경고: REMOVE_BG_API_KEY가 환경변수에 설정되어 있지 않습니다. .env 파일을 확인하세요.")

if not BRIA_API_TOKEN:
    logger.warning("경고: BRIA_API_TOKEN이 환경변수에 설정되어 있지 않습니다. .env 파일을 확인하세요.")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    logger.warning("경고: AWS 자격 증명이 환경변수에 설정되어 있지 않습니다. .env 파일을 확인하세요.") 