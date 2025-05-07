#!/usr/bin/env python3
# test_bria_api.py - S3 업로드 및 BRIA API 테스트 스크립트

import requests
import os
from dotenv import load_dotenv
import sys
import json
from datetime import datetime
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bria_test")

# .env 파일 로드
load_dotenv()

# 서버 URL 설정
SERVER_URL = "http://localhost:8001"  # FastAPI 서버 URL

def test_replace_bg(image_path, bg_prompt=None, num_results=4):
    """배경 교체 API 테스트"""
    if not os.path.exists(image_path):
        logger.error(f"오류: 파일을 찾을 수 없습니다 - {image_path}")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    endpoint = f"{SERVER_URL}/api/replace-bg"
    
    print(f"\n===== [{timestamp}] 배경 교체 API 요청 =====")
    print(f"이미지 경로: {image_path}")
    print(f"배경 프롬프트: '{bg_prompt}'")
    print(f"생성 이미지 수: {num_results}")
    
    # 파일 준비
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/png')}
        
        # 요청 데이터 준비 (Form 데이터로 명시적 전송)
        data = {}
        if bg_prompt:
            data['bg_prompt'] = bg_prompt
        data['num_results'] = str(num_results)
        
        # API 요청 보내기
        print(f"\n요청 전송 중: {endpoint}")
        logger.info(f"요청 데이터: {data}")
        
        start_time = time.time()
        response = requests.post(endpoint, files=files, data=data)
        elapsed_time = time.time() - start_time
    
    # 응답 처리
    if response.status_code == 200:
        result = response.json()
        
        # 요약 정보만 출력
        print(f"\n✅ 성공! 처리 시간: {elapsed_time:.2f}초")
        print(f"원본 이미지 URL: {result['original_url']}")
        print(f"요청 프롬프트: '{result.get('request_prompt', '알 수 없음')}'")
        
        # 프롬프트 검증
        if bg_prompt and bg_prompt != result.get('request_prompt'):
            print(f"\n⚠️ 주의: 요청한 프롬프트와 응답의 프롬프트가 다릅니다!")
            print(f"요청 프롬프트: '{bg_prompt}'")
            print(f"응답 프롬프트: '{result.get('request_prompt')}'")
        
        if 'bria_results' in result and 'result' in result['bria_results']:
            image_pairs = result['bria_results']['result']
            print(f"\n총 {len(image_pairs)}개의 이미지가 생성되었습니다:")
            
            # 결과 이미지 URL만 간략히 출력
            for i, image_pair in enumerate(image_pairs, 1):
                print(f"이미지 {i}: {image_pair[0]}")
            
            # 상세 결과를 로그 파일에 저장
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            log_filename = f"{log_dir}/bria_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(log_filename, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\n상세 결과가 저장되었습니다: {log_filename}")
        
        return result
    else:
        print(f"\n❌ 오류 발생: HTTP {response.status_code}")
        print(f"오류 내용: {response.text}")
        return None

if __name__ == "__main__":
    # 명령행 인수 처리
    if len(sys.argv) < 2:
        print("사용법: python test_bria_api.py <이미지_파일_경로> [배경_프롬프트] [결과_개수]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    bg_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    num_results = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    
    # 테스트 실행
    test_replace_bg(image_path, bg_prompt, num_results) 