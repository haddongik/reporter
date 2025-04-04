# Battle Analysis Reporter

전투 데이터를 분석하고 리포트를 생성하는 AI 기반 분석 서비스입니다.

## 주요 기능

- 전투 데이터 분석 및 리포트 생성
- 다중 AI 모델 지원 (OpenAI GPT-4, Google Gemini, Anthropic Claude)
- 비동기 작업 처리 및 상태 관리
- Battle Verifier 서버와의 연동

## 시스템 구조

```
app/
├── api/            # API 라우터
├── config/         # 설정 관리
├── models/         # 데이터 모델
├── services/       # 비즈니스 로직
└── utils/          # 유틸리티 함수
```

## API 엔드포인트

### POST /analysis
전투 데이터 분석 요청을 처리합니다.

요청 예시:
```json
{
    "elk_id": "document_id",
    "ai_model": "gemini",
    "battle_data": {
        "result_info": {},
        "user_record_minimal": {},
        "verify_record_minimal": {}
    }
}
```

응답 예시:
```json
{
    "task_id": "uuid-string",
    "status": "processing"
}
```

### GET /analysis/{task_id}
분석 작업의 상태를 조회합니다.

응답 예시:
```json
{
    "status": "completed",
    "started_at": "2024-03-25T10:00:00",
    "completed_at": "2024-03-25T10:01:00",
    "result": {}
}
```

## 설치 및 실행

### 도커를 이용한 실행

1. 도커 이미지 빌드
```bash
docker-compose build
```

2. 서비스 실행
```bash
docker-compose up
```

### 환경 변수 설정

```bash
# AI 모델 API 키
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# AI 모델 설정
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.0-flash
CLAUDE_MODEL=claude-3-7-sonnet-max

# Battle Verifier 서버 설정
BATTLE_VERIFIER_HOST=localhost
BATTLE_VERIFIER_PORT=3000
BATTLE_VERIFIER_PROTOCOL=http
```

## 의존성

- Python 3.11+
- FastAPI
- LangChain
- httpx
- pydantic

## 에러 처리

- 400 Bad Request: 잘못된 입력 데이터
- 404 Not Found: 존재하지 않는 작업 ID
- 500 Internal Server Error: 서버 내부 오류

## 개발 가이드

1. 새로운 AI 모델 추가
   - `app/services/langchain_service.py`에 모델 설정 추가
   - `app/config/app_config.py`에 모델 설정 추가

2. 분석 로직 수정
   - `app/services/analysis_service.py`의 `process_analysis_in_background` 함수 수정

3. 새로운 API 엔드포인트 추가
   - `app/api/routes.py`에 새로운 라우터 추가
   - `app/models/request_models.py`에 요청 모델 추가 