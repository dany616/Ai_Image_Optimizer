# controller/background_replace.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import boto3
import requests
import os
import uuid
from dotenv import load_dotenv
import logging
import io
from fastapi.responses import JSONResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("background_replace")

# 환경 변수 로드
load_dotenv()

# 라우터 설정
router = APIRouter(tags=["이미지 배경 제거 및 생성"])

# AWS S3 설정
BUCKET_NAME = "briadownload"
REGION = "ap-northeast-2"  # 서울 리전

# S3 클라이언트 설정
s3_client = boto3.client(
    's3',
    region_name=REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

@router.post("/remove-and-generate")
async def remove_and_generate(
    file: UploadFile = File(...),
    bg_prompt: str = Form("beautiful natural scenery"),
    num_results: int = Form(4)
):
    """
    이미지 배경을 제거한 후 BRIA API를 통해 새로운 배경을 생성합니다.
    
    Args:
        file: 배경을 제거할 원본 이미지 파일
        bg_prompt: 생성할 배경에 대한 설명 프롬프트
        num_results: 생성할 이미지 결과 개수 (기본값: 4)
    
    Returns:
        BRIA API 응답 결과와 원본 이미지 URL 등을 포함한 JSON 응답
    """
    try:
        # 유효한 결과 개수 확인
        if num_results < 1:
            num_results = 1
        elif num_results > 10:
            num_results = 10
            
        # 파일 읽기
        contents = await file.read()
        
        # Remove.bg API를 사용하여 배경 제거
        logger.info("Remove.bg API 호출 시작")
        
        remove_bg_api_key = os.getenv("REMOVE_BG_API_KEY")
        if not remove_bg_api_key:
            raise HTTPException(status_code=500, detail="Remove.bg API 키가 설정되지 않았습니다.")
        
        remove_bg_response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': contents},
            data={'size': 'auto'},
            headers={'X-Api-Key': remove_bg_api_key},
        )
        
        if remove_bg_response.status_code != 200:
            logger.error(f"Remove.bg API 오류: {remove_bg_response.status_code} - {remove_bg_response.text}")
            raise HTTPException(
                status_code=remove_bg_response.status_code,
                detail=f"Remove.bg API 오류: {remove_bg_response.text}"
            )
        
        logger.info("배경 제거 완료, S3 업로드 준비")
        
        # 배경이 제거된 이미지 데이터
        no_bg_image = remove_bg_response.content
        
        # 고유한 파일 이름 생성
        request_id = str(uuid.uuid4())
        original_filename = file.filename
        file_name, file_ext = os.path.splitext(original_filename)
        unique_filename = f"{request_id}_{file_name}_nobg.png"
        
        # S3에 파일 업로드
        logger.info(f"S3 업로드: {unique_filename}")
        
        s3_client.upload_fileobj(
            io.BytesIO(no_bg_image),
            BUCKET_NAME,
            unique_filename,
            ExtraArgs={'ContentType': 'image/png'}
        )
        
        # S3 URL 생성
        file_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{unique_filename}"
        logger.info(f"S3 업로드 완료: {file_url}")
        
        # BRIA API 호출
        logger.info("BRIA API 호출 시작")
        
        bria_api_token = os.getenv("BRIA_API_TOKEN")
        if not bria_api_token:
            raise HTTPException(status_code=500, detail="BRIA API 토큰이 설정되지 않았습니다.")
        
        # 현재 타임스탬프를 포함하여 캐싱 방지
        request_timestamp = int(uuid.uuid1().time)
        
        # API 요청 데이터 준비
        request_data = {
            "image_url": file_url,
            "bg_prompt": bg_prompt,
            "num_results": num_results,
            "sync": True,
            "metadata": {
                "request_id": request_id,
                "timestamp": request_timestamp,
                "prompt": bg_prompt
            }
        }
        
        # 요청 데이터 기록
        logger.info(f"BRIA API 요청 데이터: {request_data}")
        
        bria_response = requests.post(
            "https://engine.prod.bria-api.com/v1/background/replace",
            headers={
                "Content-Type": "application/json",
                "api_token": bria_api_token,
                "Cache-Control": "no-cache"
            },
            json=request_data,
            timeout=60
        )
        
        # API 응답 확인
        if bria_response.status_code != 200:
            logger.error(f"BRIA API 오류: {bria_response.status_code} - {bria_response.text}")
            raise HTTPException(
                status_code=bria_response.status_code,
                detail=f"BRIA API 오류: {bria_response.text}"
            )
        
        result = bria_response.json()
        logger.info(f"BRIA API 응답 성공: {len(result.get('result', []))}개 이미지 생성됨")
        
        # 성공 응답
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "original_url": file_url,
                "bria_results": result,
                "result_count": num_results,
                "request_prompt": bg_prompt,
                "request_id": request_id
            }
        )
        
    except Exception as e:
        logger.error(f"이미지 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"이미지 처리 중 오류 발생: {str(e)}") 