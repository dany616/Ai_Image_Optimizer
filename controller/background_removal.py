from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import requests
import uuid
import shutil
from typing import Optional
from datetime import datetime
import cv2
import numpy as np
from dotenv import load_dotenv
from model.database import get_db, User, Image, UserImage

load_dotenv()

router = APIRouter(
    prefix="/api/background",
    tags=["background"],
    responses={404: {"description": "Not found"}},
)

# 업로드 및 결과 저장 디렉토리
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
RESULT_DIR = os.path.join(os.getcwd(), "uploads", "results")
EDGE_DIR = os.path.join(os.getcwd(), "uploads", "edges")

# 디렉토리 생성
for directory in [UPLOAD_DIR, RESULT_DIR, EDGE_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Remove.bg API 키 가져오기
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY", "")
if not REMOVE_BG_API_KEY:
    print("경고: REMOVE_BG_API_KEY가 설정되지 않았습니다.")
else:
    print(f"Remove.bg API 키 로드됨: {REMOVE_BG_API_KEY[:5]}...")

@router.post("/remove")
async def remove_background(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Remove.bg API를 사용하여 배경 제거
    """
    print(f"배경 제거 API 호출됨: 파일명={file.filename}, 크기={file.size if hasattr(file, 'size') else '알 수 없음'}")
    
    if not REMOVE_BG_API_KEY:
        raise HTTPException(status_code=500, detail="API 키가 설정되지 않았습니다.")
    
    # 사용자 확인 (실제 구현에서는 인증 시스템에서 가져올 것)
    if user_id:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # 크레딧 확인
        if user.credits < 1:
            raise HTTPException(status_code=400, detail="크레딧이 부족합니다.")
    
    # 파일 저장
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    input_file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")
    output_file_path = os.path.join(RESULT_DIR, f"{file_id}_nobg.png")
    
    print(f"파일 저장 경로: {input_file_path}")
    
    with open(input_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        print(f"Remove.bg API 호출 시작")
        # Remove.bg API 호출
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': open(input_file_path, 'rb')},
            data={'size': 'auto'},
            headers={'X-Api-Key': REMOVE_BG_API_KEY},
        )
        
        print(f"Remove.bg API 응답 코드: {response.status_code}")
        
        if response.status_code != 200:
            error_detail = f"Remove.bg API 오류: {response.text}"
            print(error_detail)
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        # 결과 저장
        with open(output_file_path, 'wb') as out:
            out.write(response.content)
            
        print(f"결과 이미지 저장됨: {output_file_path}")
        
        # 사용자 정보 업데이트 (인증된 사용자의 경우)
        if user_id and user:
            # 이미지 메타데이터 저장
            new_image = Image(
                user_id=user_id,
                original_image_url=input_file_path,
                generated_image_url=output_file_path,
                background_style="removed",
                model_version="remove.bg-api",
                processing_time=0.0,  # 실제 API 응답 시간을 측정할 수 있습니다
                created_at=datetime.utcnow()
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
            
            # Edge 감지 작업 백그라운드로 실행
            background_tasks.add_task(detect_edges, input_file_path, file_id)
            
            return {
                "status": "success",
                "message": "배경이 성공적으로 제거되었습니다.",
                "image_id": new_image.image_id,
                "result_image_url": f"/uploads/results/{file_id}_nobg.png",  # 클라이언트에서 접근 가능한 URL
                "remaining_credits": user.credits
            }
        
        # 비인증 사용자의 경우 Edge 감지 작업 백그라운드로 실행
        background_tasks.add_task(detect_edges, input_file_path, file_id)
        
        return {
            "status": "success",
            "message": "배경이 성공적으로 제거되었습니다.",
            "result_image_url": f"/uploads/results/{file_id}_nobg.png"  # 클라이언트에서 접근 가능한 URL
        }
    
    except Exception as e:
        # 오류 발생 시 파일 정리
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        raise HTTPException(status_code=500, detail=f"배경 제거 중 오류 발생: {str(e)}")

@router.get("/result/{file_id}")
async def get_result_image(file_id: str):
    """
    배경 제거 결과 이미지 반환
    """
    result_file_path = os.path.join(RESULT_DIR, f"{file_id}_nobg.png")
    if not os.path.exists(result_file_path):
        raise HTTPException(status_code=404, detail="결과 이미지를 찾을 수 없습니다.")
    
    return FileResponse(result_file_path)

@router.get("/edge/{file_id}")
async def get_edge_image(file_id: str):
    """
    Edge 감지 결과 이미지 반환
    """
    edge_file_path = os.path.join(EDGE_DIR, f"{file_id}_edge.png")
    if not os.path.exists(edge_file_path):
        raise HTTPException(status_code=404, detail="윤곽선 이미지를 찾을 수 없습니다.")
    
    return FileResponse(edge_file_path)

def detect_edges(image_path: str, file_id: str):
    """
    OpenCV를 사용하여 윤곽선(Edge Map) 추출
    """
    try:
        # 이미지 로드
        image = cv2.imread(image_path)
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 가우시안 블러 적용 (노이즈 제거)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 캐니 에지 감지
        edges = cv2.Canny(blurred, 50, 150)
        
        # 결과 저장
        edge_file_path = os.path.join(EDGE_DIR, f"{file_id}_edge.png")
        cv2.imwrite(edge_file_path, edges)
        
        print(f"Edge detection completed for {file_id}")
        return edge_file_path
    
    except Exception as e:
        print(f"Edge detection failed: {str(e)}")
        return None 