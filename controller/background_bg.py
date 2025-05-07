from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
import os
import uuid
import shutil
import base64
from typing import Optional, Dict, Any
from datetime import datetime
import cv2
import numpy as np
from model.database import get_db, User, Image, UserImage

router = APIRouter(
    prefix="/api/backgroundBG",
    tags=["backgroundBG"],
    responses={404: {"description": "Not found"}},
)

# 업로드 및 결과 저장 디렉토리
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
RESULT_BG_DIR = os.path.join(os.getcwd(), "uploads", "bg_results")

# 디렉토리 생성
for directory in [UPLOAD_DIR, RESULT_BG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

@router.post("/save")
async def save_processed_image(
    image_data: Dict[str, Any] = Body(...),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    클라이언트에서 배경이 제거된 이미지 데이터를 받아 서버에 저장
    """
    try:
        # Base64 이미지 데이터 추출
        if "imageData" not in image_data:
            raise HTTPException(status_code=400, detail="이미지 데이터가 제공되지 않았습니다.")
        
        base64_data = image_data["imageData"].split(",")[1] if "," in image_data["imageData"] else image_data["imageData"]
        image_bytes = base64.b64decode(base64_data)
        
        # 이미지 타입과 처리 방식 추출
        processing_type = image_data.get("processingType", "selectable-object-bg-removal")
        
        # 파일 저장
        file_id = str(uuid.uuid4())
        output_file_path = os.path.join(RESULT_BG_DIR, f"{file_id}_nobg.png")
        
        # 이미지 데이터 저장
        with open(output_file_path, "wb") as file:
            file.write(image_bytes)
        
        # 사용자 정보 업데이트 (인증된 사용자의 경우)
        if user_id:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
            
            # 크레딧 확인
            if user.credits < 1:
                raise HTTPException(status_code=400, detail="크레딧이 부족합니다.")
            
            # 이미지 메타데이터 저장
            new_image = Image(
                user_id=user_id,
                original_image_url=image_data.get("originalImageUrl", ""),
                generated_image_url=output_file_path,
                background_style="removed",
                model_version=processing_type,
                processing_time=image_data.get("processingTime", 0.0),
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
            
            return {
                "status": "success",
                "message": "배경 제거 이미지가 성공적으로 저장되었습니다.",
                "image_id": new_image.image_id,
                "result_image_url": f"/uploads/bg_results/{file_id}_nobg.png",  # 클라이언트에서 접근 가능한 URL
                "remaining_credits": user.credits
            }
        
        # 비인증 사용자의 경우
        return {
            "status": "success",
            "message": "배경 제거 이미지가 성공적으로 저장되었습니다.",
            "result_image_url": f"/uploads/bg_results/{file_id}_nobg.png"  # 클라이언트에서 접근 가능한 URL
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 저장 중 오류 발생: {str(e)}")

@router.get("/result/{file_id}")
async def get_result_image(file_id: str):
    """
    배경 제거 결과 이미지 반환
    """
    result_file_path = os.path.join(RESULT_BG_DIR, f"{file_id}_nobg.png")
    if not os.path.exists(result_file_path):
        raise HTTPException(status_code=404, detail="결과 이미지를 찾을 수 없습니다.")
    
    return FileResponse(result_file_path)

@router.post("/upload-and-save")
async def upload_and_save_image(
    file: UploadFile = File(...),
    processing_type: str = Form("selectable-object-bg-removal"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    원본 이미지 업로드 후 처리된 이미지를 서버에 저장
    """
    try:
        # 원본 파일 저장
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        input_file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")
        
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "status": "success",
            "message": "이미지가 성공적으로 업로드되었습니다.",
            "file_id": file_id,
            "original_image_url": f"/uploads/{file_id}{file_extension}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 업로드 중 오류 발생: {str(e)}") 