from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
import os
import json
from dotenv import load_dotenv
from typing import Dict, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_keys")

# 환경 변수 로드
load_dotenv()

# API 키 저장용 임시 파일 설정
TEMP_KEYS_FILE = os.path.join(os.getcwd(), "temp_keys.json")

# 라우터 설정
router = APIRouter(prefix="/api/keys", tags=["API 키 관리"])

# 초기화: 임시 파일에 현재 환경변수의 API 키들을 저장
def initialize_temp_keys():
    # 기본값을 빈 문자열로 설정
    api_keys = {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", ""),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        "REMOVE_BG_API_KEY": os.getenv("REMOVE_BG_API_KEY", ""),
        "BRIA_API_TOKEN": os.getenv("BRIA_API_TOKEN", "")
    }
    
    # 임시 파일에 저장
    try:
        with open(TEMP_KEYS_FILE, "w") as f:
            json.dump(api_keys, f)
        logger.info("임시 API 키 파일 초기화됨")
    except Exception as e:
        logger.error(f"임시 API 키 파일 초기화 실패: {str(e)}")

# 애플리케이션 시작 시 초기화
initialize_temp_keys()

# API 키 가져오기 엔드포인트
@router.get("")
async def get_api_keys():
    """
    현재 설정된 API 키 목록을 반환합니다.
    값은 보안을 위해 마스킹됩니다.
    """
    try:
        # 임시 파일에서 API 키 읽기
        if os.path.exists(TEMP_KEYS_FILE):
            with open(TEMP_KEYS_FILE, "r") as f:
                api_keys = json.load(f)
        else:
            # 파일이 없으면 초기화
            initialize_temp_keys()
            with open(TEMP_KEYS_FILE, "r") as f:
                api_keys = json.load(f)
        
        # 키의 값을 마스킹 처리
        masked_keys = {}
        for key, value in api_keys.items():
            if value and len(value) > 8:
                masked_keys[key] = value[:4] + '*' * (len(value) - 8) + value[-4:]
            elif value:
                masked_keys[key] = '*' * len(value)
            else:
                masked_keys[key] = ''
        
        return {"keys": masked_keys}
    
    except Exception as e:
        logger.error(f"API 키 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API 키 조회 실패: {str(e)}")

# API 키 설정 엔드포인트
@router.post("")
async def set_api_keys(keys: Dict[str, str] = Body(...)):
    """
    API 키를 설정합니다.
    임시 파일에 저장되며, 서버 재시작 시에는 .env 파일의 값으로 초기화됩니다.
    """
    try:
        # 현재 키 읽기
        current_keys = {}
        if os.path.exists(TEMP_KEYS_FILE):
            with open(TEMP_KEYS_FILE, "r") as f:
                current_keys = json.load(f)
        
        # 새로 설정된 키만 업데이트
        for key, value in keys.items():
            if key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "REMOVE_BG_API_KEY", "BRIA_API_TOKEN"]:
                current_keys[key] = value
        
        # 업데이트된 키를 파일에 저장
        with open(TEMP_KEYS_FILE, "w") as f:
            json.dump(current_keys, f)
        
        # 환경변수에도 임시로 설정
        for key, value in current_keys.items():
            os.environ[key] = value
        
        logger.info("API 키가 성공적으로 업데이트되었습니다.")
        return {"status": "success", "message": "API 키가 성공적으로 설정되었습니다."}
    
    except Exception as e:
        logger.error(f"API 키 설정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API 키 설정 실패: {str(e)}")

# 특정 API 키 상태 확인 엔드포인트
@router.get("/check/{key}")
async def check_api_key(key: str):
    """
    특정 API 키가 설정되어 있는지 확인합니다.
    """
    allowed_keys = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "REMOVE_BG_API_KEY", "BRIA_API_TOKEN"]
    
    if key not in allowed_keys:
        raise HTTPException(status_code=400, detail=f"지원되지 않는 API 키입니다: {key}")
    
    try:
        # 임시 파일에서 값 읽기
        if os.path.exists(TEMP_KEYS_FILE):
            with open(TEMP_KEYS_FILE, "r") as f:
                api_keys = json.load(f)
                value = api_keys.get(key, "")
        else:
            # 환경변수에서 직접 읽기
            value = os.getenv(key, "")
        
        # 값이 있는지 여부만 확인하고 실제 값은 반환하지 않음
        return {"key": key, "is_set": bool(value)}
    
    except Exception as e:
        logger.error(f"API 키 상태 확인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API 키 상태 확인 실패: {str(e)}") 