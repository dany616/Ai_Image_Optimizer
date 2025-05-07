# controller/background_bria.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import boto3
import requests
import os
from dotenv import load_dotenv
import uuid
from fastapi.responses import JSONResponse
import io
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bria_api")

load_dotenv()

router = APIRouter(tags=["배경 교체"])
BUCKET_NAME = "briadownload"
REGION = "ap-northeast-2"  # 서울 리전

# S3 클라이언트 설정
s3_client = boto3.client(
    's3',
    region_name=REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

@router.post("/replace-bg")
async def replace_bg(
    file: UploadFile = File(...), 
    bg_prompt: str = Form("beautiful natural scenery"),
    num_results: int = Form(4)
):
    """
    배경이 제거된 이미지를 S3에 업로드하고 BRIA API를 사용하여 새 배경을 생성합니다.
    
    - file: 배경이 제거된 이미지 파일
    - bg_prompt: 새 배경을 위한 프롬프트 (기본값: "beautiful natural scenery")
    - num_results: 생성할 이미지 결과 개수 (기본값: 4, 최대: 10)
    """
    try:
        # 디버그: 전달된 파라미터 기록
        logger.info(f"요청 받음: 프롬프트='{bg_prompt}', 결과 개수={num_results}")
        
        # 유효한 결과 개수 확인
        if num_results < 1:
            num_results = 1
        elif num_results > 10:  # 최대 개수 제한 (BRIA API에 따라 조정 필요)
            num_results = 10
            
        # 파일 읽기
        contents = await file.read()
        
        # 고유한 파일 이름 생성 (UUID + 원본 파일명)
        # 원본 파일명에서 확장자 분리
        original_filename = file.filename
        file_name, file_ext = os.path.splitext(original_filename)
        
        # UUID와 원본 파일명을 조합하여 고유한 키 생성
        request_id = str(uuid.uuid4())
        unique_filename = f"{request_id}_{file_name}{file_ext}"
        
        # 디버그 로그
        logger.info(f"업로드 파일명: {unique_filename}")
        logger.info(f"배경 프롬프트: '{bg_prompt}'")
        
        # S3에 파일 직접 업로드
        s3_client.upload_fileobj(
            io.BytesIO(contents),
            BUCKET_NAME,
            unique_filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        # S3 URL 생성
        file_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{unique_filename}"
        logger.info(f"S3 업로드 완료: {file_url}")
        
        # BRIA API 호출
        bria_api_token = os.getenv("BRIA_API_TOKEN")
        if not bria_api_token:
            raise HTTPException(status_code=500, detail="BRIA API 토큰이 설정되지 않았습니다.")
        
        # 현재 타임스탬프를 포함하여 캐싱 방지
        request_timestamp = int(uuid.uuid1().time)
        
        # API 요청 데이터 준비
        request_data = {
            "image_url": file_url,
            "bg_prompt": bg_prompt,  # 사용자 입력 프롬프트 그대로 사용
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
        
        response = requests.post(
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
        if response.status_code != 200:
            logger.error(f"BRIA API 오류: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"BRIA API 오류: {response.text}"
            )
        
        result = response.json()
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
