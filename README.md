# 🛒 쇼핑몰 RAG 챗봇 (Polyglot MSA)

Python(FastAPI)과 Rust(Axum)를 결합한 **MSA 기반 B2B 쇼핑몰 챗봇 서비스**입니다.  
보안, 고성능 스크래핑, 그리고 확장성을 고려하여 설계되었습니다.

---

## 🏗️ 아키텍처 (Architecture)

시스템은 크게 두 가지 마이크로서비스로 구성됩니다.

| 서비스 명 | 기술 스택 | 역할 |
|---|---|---|
| **Core API** | Python, FastAPI, Motor | 메인 백엔드, DB 연동, 인증, 오케스트레이션 |
| **Scraper Engine** | Rust, Axum, Reqwest | 고성능 HTML 다운로드 및 파싱 (CPU 집약 작업 담당) |

---

## 🚀 시작하기 (Getting Started)

### 1. 필수 요구사항 (Prerequisites)
*   **Python 3.10+** (Core API용)
*   **Rust (Latest)** (Scraper Engine용)
*   **MongoDB Atlas** (데이터 저장소)

### 2. 설치 및 환경 설정

**Core API (Python)**
1.  폴더 이동: `cd core-api`
2.  가상환경 생성 및 의존성 설치:
    ```bash
    uv pip install -e .
    ```
3.  환경 변수 설정: `.env` 파일을 생성하고 DB 주소를 입력합니다.
    ```env
    MONGODB_URL=mongodb+srv://...
    PROJECT_NAME=Mall Chatbot
    DB_NAME=mall_chatbot_db
    API_KEY_SECRET=secret
    OPENAI_API_KEY=sk-...
    ```

**Scraper Engine (Rust)**
1.  폴더 이동: `cd scraper-engine`
2.  빌드 확인: `cargo check`

---

## ▶️ 실행 방법 (How to Run)

두 개의 터미널을 열어서 각각 실행해야 합니다.

**터미널 1: Rust Scraper 실행**
```powershell
cd scraper-engine
cargo run
# Rust Scraper Engine listening on 0.0.0.0:3000
```

**터미널 2: Python Core 실행**
```powershell
cd core-api
uvicorn app.main:app --reload
# Uvicorn running on http://127.0.0.1:8000
```

---

## ✅ 테스트 방법 (Integration Test)

프론트엔드 없이 터미널에서 바로 테스트할 수 있도록 스크립트를 제공합니다.

**1. 테스트 데이터 주입** (최초 1회 필수)
DB에 테스트용 API Key를 등록합니다.
```powershell
python core-api/scripts/setup_test_data.py
```

**2. API 호출 테스트**
실제로 챗봇 API에 메시지를 보내봅니다.
```powershell
python core-api/scripts/test_chat_api.py
```
> 성공 시: `✅ Test Passed!` 와 함께 JSON 응답이 출력됩니다.

---

## 📂 프로젝트 구조

```
searchingbot/
├── core-api/           # Python FastAPI Server
│   ├── src/app/
│   │   ├── api/        # Endpoints
│   │   ├── db/         # MongoDB Connection
│   │   ├── middleware/ # Security (API Key, CORS)
│   │   ├── models/     # Pydantic Models
│   │   └── services/   # Business Logic (Scraper)
│   └── scripts/        # Test Scripts
│
└── scraper-engine/     # Rust Axum Server
    └── src/main.rs     # Scraping Logic
```
