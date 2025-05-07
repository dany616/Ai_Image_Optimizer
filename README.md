# Background Removal & Generation Backend Server

## Overview

This project provides the backend for an image‑background removal and generation service built with FastAPI. Core features include background removal, new background generation, and background replacement.

## Key Features

* Image background‑removal API
* New background‑generation API
* BRIA background‑replacement API
* User authentication management
* Processing‑history tracking

## System Requirements

* Python ≥ 3.8
* PostgreSQL database
* Sufficient memory and disk space for image processing

## Installation

### 1. Clone the repository

```bash
git clone <repository‑URL>
cd Backend_server
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the project root and add:

```
# Database
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_photo_db

# API keys
REMOVE_BG_API_KEY=your_remove_bg_api_key
BRIA_API_TOKEN=your_bria_api_token

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# File‑upload limit
MAX_FILE_SIZE=10485760   # 10 MB
```

#### Important Notes on Environment Variables

- **All sensitive information** (API keys, database credentials) is managed through environment variables.
- The system looks for these variables in the `.env` file (not committed to Git).
- If environment variables are not set, default connection values are used for development (but APIs won't work).
- You can manage API keys through the web interface at `/api/keys` once the server is running.
- **Never hardcode credentials** in your code.

### 5. Configure API keys

The app stores replacement images in AWS S3.

**AWS**

1. Create an AWS account if you don't have one.
2. Create an S3 bucket named `briadownload` (or change the bucket name in the code).
3. Create an IAM user with S3 access.
4. Generate an access‑key ID and secret‑access key.
5. Add these credentials to your environment variables.

**BRIA**

1. Sign up / log in at [https://platform.bria.ai/login](https://platform.bria.ai/login).
2. In **Image Generation**, click **COPY API TOKEN**.

**REMOVE.BG**

1. Sign up at [https://accounts.kaleido.ai/users/sign\_up](https://accounts.kaleido.ai/users/sign_up).
2. Go to **My Account → API Keys**.
3. Click **+ New API Key** and copy it.

### 6. Set up the database

Create a database in PostgreSQL:

```bash
psql -U postgres
CREATE DATABASE ai_photo_db;
CREATE USER your_db_user WITH ENCRYPTED PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE ai_photo_db TO your_db_user;
\q
```

## Running the Server

```bash
cd Backend_server
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The server runs at **[http://localhost:8001](http://localhost:8001)**.
Interactive docs: **[http://localhost:8001/docs](http://localhost:8001/docs)**

## API Endpoints

* `/api/health` – health check
* `/api/remove-background` – remove an image background
* `/api/background-bria` – replace background via BRIA API
* `/api/background-replace` – remove & generate background in one step
* `/api/keys` – manage API keys

### API Keys Management

The system provides a web interface and API endpoints to manage API keys:

* GET `/api/keys` - Get the list of currently configured API keys (values are masked)
* POST `/api/keys` - Set/update API keys
* GET `/api/keys/check/{key}` - Check if a specific API key is set

This allows you to manage API keys without restarting the server or modifying the `.env` file.

## Project Structure

```
Backend_server/
├── controller/         # API routers & controllers
├── model/              # Database models
├── config/             # Configuration files
├── uploads/            # Uploaded‑image storage
├── venv/               # Virtual environment (not in Git)
├── main.py             # Application entry point
├── config.py           # Settings
└── README.md           # This file
```

## GitHub Checklist

### .gitignore

Be sure the following are ignored:

```
# Sensitive data
.env
*.pem
*.key
*.cert

# Virtual envs
venv/
env/
ENV/

# Logs
*.log
logs/

# Uploaded files
uploads/
uploads/bg_results/

# Python cache
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# System files
.DS_Store
Thumbs.db

# IDE configs
.idea/
.vscode/
*.swp
*.swo

# Local DB files
*.db
*.sqlite3
```

### Security Tips

1. Store API keys and passwords only in `.env`; never commit them.
2. If credentials are hard‑coded (e.g., in `config/config.py`), replace them with environment variables.
3. Avoid committing development DB credentials.
4. **Never commit AWS credentials or share them in a public repo.**
5. Use the built-in API key management interface instead of hardcoding API keys.

## Main Dependencies

See `requirements.txt` for the full list. Key packages:

* fastapi == 0.99.1
* uvicorn == 0.22.0
* sqlalchemy == 2.0.17
* pydantic == 1.10.8
* python‑multipart == 0.0.6
* python‑dotenv == 1.0.0
* requests == 2.31.0
* pillow == 9.5.0
* psycopg2‑binary == 2.9.6
* boto3 == 1.28.38  # AWS S3 integration

## Generating `requirements.txt`

```bash
pip freeze > requirements.txt
```

## License

This project is licensed under the MIT License.

## Contact

Open an issue if you encounter problems or have questions.

# 배경 제거 및 생성 백엔드 서버

## 개요
이 프로젝트는 FastAPI를 사용한 이미지 배경 제거 및 생성 서비스의 백엔드 서버입니다. 주요 기능으로는 이미지 배경 제거, 새 배경 생성, 배경 교체 등이 있습니다.

## 주요 기능
- 이미지 배경 제거 API
- 새로운 배경 생성 API
- BRIA 배경 교체 API
- 사용자 인증 관리
- 이미지 처리 기록 관리

## 시스템 요구사항
- Python 3.8 이상
- PostgreSQL 데이터베이스
- 충분한 메모리와 디스크 공간 (이미지 처리용)

## 설치 방법

### 1. 저장소 클론
```bash
git clone <저장소 URL>
cd Backend_server
```

### 2. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows의 경우: venv\Scripts\activate
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 다음 내용을 추가합니다:

```
# 데이터베이스 설정
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_photo_db

# API 키
REMOVE_BG_API_KEY=your_remove_bg_api_key
BRIA_API_TOKEN=your_bria_api_token

# AWS S3 설정
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# 파일 업로드 설정
MAX_FILE_SIZE=10485760  # 10MB
```

#### 환경 변수 설정에 관한 중요 참고사항

- **모든 민감한 정보**(API 키, 데이터베이스 자격 증명)는 환경 변수를 통해 관리됩니다.
- 시스템은 `.env` 파일에서 이러한 변수를 찾습니다(Git에 커밋되지 않음).
- 환경 변수가 설정되지 않은 경우 개발용 기본 연결 값이 사용됩니다(단, API는 작동하지 않음).
- 서버가 실행된 후 웹 인터페이스 `/api/keys`를 통해 API 키를 관리할 수 있습니다.
- **코드에 자격 증명을 하드코딩하지 마세요**.

### 5. API KEY 설정
애플리케이션은 배경 교체를 위한 이미지 저장에 AWS S3를 사용합니다:

AWS
1. AWS 계정이 없다면 계정 생성
2. "briadownload"라는 이름의 S3 버킷 생성 (또는 코드에서 버킷 이름 수정)
3. S3 접근 권한이 있는 IAM 사용자 생성
4. 액세스 키 ID와 비밀 액세스 키 발급
5. 이 자격 증명을 API키관리에 추가

BRIA 
1. 계정 생성 및 로그인 https://platform.bria.ai/login
2. 이미지 생성 - COPY API TOKEN

REMOVE.BG
1.https://accounts.kaleido.ai/users/sign_up
2.My account - API Keys
3.+New API Key
4. COPY


### 6. 데이터베이스 설정
PostgreSQL에 데이터베이스를 생성합니다:
```bash
psql -U postgres
CREATE DATABASE ai_photo_db;
CREATE USER your_db_user WITH ENCRYPTED PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE ai_photo_db TO your_db_user;
\q
```

## 서버 실행 방법
```bash
cd Backend_server
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

서버는 기본적으로 http://localhost:8001 에서 실행됩니다.
API 문서는 http://localhost:8001/docs 에서 확인할 수 있습니다.

## API 엔드포인트
- `/api/health` - 서버 상태 확인
- `/api/remove-background` - 이미지 배경 제거
- `/api/background-bria` - BRIA API를 사용한 배경 교체
- `/api/background-replace` - 배경 제거 및 생성
- `/api/keys` - API 키 관리

### API 키 관리

시스템은 API 키를 관리하기 위한 웹 인터페이스와 API 엔드포인트를 제공합니다:

* GET `/api/keys` - 현재 구성된 API 키 목록 가져오기 (값은 마스킹 처리됨)
* POST `/api/keys` - API 키 설정/업데이트
* GET `/api/keys/check/{key}` - 특정 API 키가 설정되어 있는지 확인

이를 통해 서버를 재시작하거나 `.env` 파일을 수정하지 않고도 API 키를 관리할 수 있습니다.

## 프로젝트 구조
```
Backend_server/
├── controller/           # API 라우터 및 컨트롤러
├── model/                # 데이터베이스 모델
├── config/               # 설정 파일
├── uploads/              # 업로드된 이미지 저장소
├── venv/                 # 가상환경 (git에 포함하지 않음)
├── main.py               # 메인 애플리케이션 진입점
├── config.py             # 환경설정
└── README.md             # 이 파일
```

## GitHub에 올릴 때 주의사항

### .gitignore 설정
다음 파일/디렉토리는 GitHub에 올리지 않도록 .gitignore에 추가해야 합니다:

```
# 환경변수 및 보안 정보
.env
*.pem
*.key
*.cert

# 가상환경
venv/
env/
ENV/

# 로그 파일
*.log
logs/

# 업로드된 파일 및 결과물
uploads/
uploads/bg_results/

# 파이썬 캐시 파일
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# 시스템 파일
.DS_Store
Thumbs.db

# IDE 설정
.idea/
.vscode/
*.swp
*.swo

# 데이터베이스 파일
*.db
*.sqlite3
```

### 보안 주의사항
1. API 키, 비밀번호 등 민감한 정보는 `.env` 파일에 저장하고 GitHub에 올리지 마세요.
2. `config/config.py`와 같은 파일에 하드코딩된 비밀번호나 API 키가 있다면 환경변수로 대체해야 합니다.
3. 개발용 데이터베이스 계정 정보가 코드에 포함되지 않도록 주의하세요.
4. **AWS 자격 증명을 절대 공개 저장소에 공유하거나 버전 관리에 커밋하지 마세요.**
5. 하드코딩된 API 키 대신 내장된 API 키 관리 인터페이스를 사용하세요.

## 의존성 패키지 목록
주요 패키지 목록입니다. 전체 목록은 `requirements.txt`를 참조하세요:

- fastapi==0.99.1
- uvicorn==0.22.0
- sqlalchemy==2.0.17
- pydantic==1.10.8
- python-multipart==0.0.6
- python-dotenv==1.0.0
- requests==2.31.0
- pillow==9.5.0
- psycopg2-binary==2.9.6
- boto3==1.28.38  # AWS S3 통합용

## 필요한 requirements.txt 파일 생성
```bash
pip freeze > requirements.txt
```

## 라이센스
이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 문의사항
문제가 발생하거나 질문이 있으면 이슈를 등록해주세요. 