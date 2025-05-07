# S3 및 BRIA API 배경 생성 기능 사용 안내

## 개요
이 기능은 배경이 제거된 이미지를 AWS S3에 업로드한 후, BRIA AI API를 사용하여 새로운 배경을 생성하는 기능입니다.

## 환경 설정

1. `.env` 파일에 AWS 인증 정보와 BRIA API 키 설정
```
AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
BRIA_API_TOKEN="YOUR_BRIA_API_TOKEN"
```

2. AWS S3 버킷 설정이 필요합니다 (이미 "briadownload" 버킷이 생성되어 있어야 함)

3. 필요한 Python 패키지 설치
```bash
pip install boto3 requests fastapi python-multipart python-dotenv
```

## API 사용법

### 배경 교체 API

**엔드포인트**: `/api/replace-bg`
**HTTP 메소드**: POST
**요청 형식**: multipart/form-data

**매개변수**:
- `file`: 배경이 제거된 이미지 파일 (필수)
- `bg_prompt`: 새 배경을 위한 프롬프트 (선택, 기본값: "beautiful natural scenery")
- `num_results`: 생성할 이미지 결과 개수 (선택, 기본값: 4, 최대: 10)

**응답 형식**:
```json
{
  "status": "success",
  "original_url": "https://briadownload.s3.ap-northeast-2.amazonaws.com/uploaded_image.png",
  "bria_results": {
    // BRIA API 응답 내용
  },
  "result_count": 4
}
```

## 테스트 스크립트 사용법

`test_bria_api.py` 스크립트를 사용하여 API를 테스트할 수 있습니다:

```bash
python test_bria_api.py <이미지_파일_경로> [배경_프롬프트] [결과_개수]
```

예시:
```bash
# 기본 4개 이미지 생성
python test_bria_api.py ./uploads/bg_results/removed_bg.png "modern kitchen interior"

# 6개 이미지 생성
python test_bria_api.py ./uploads/bg_results/removed_bg.png "modern kitchen interior" 6
```

## 주의사항

1. 이미지 파일 크기는 10MB 이하로 유지하는 것이 좋습니다.
2. 배경이 이미 제거된 이미지(투명 배경)를 사용하는 것이 좋은 결과를 얻을 수 있습니다.
3. AWS S3와 BRIA API 사용에 따른 요금이 발생할 수 있으니 주의하세요.
4. 결과 이미지 개수를 많이 요청할수록 API 응답 시간이 길어질 수 있습니다. 