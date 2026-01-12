import httpx
import logging
from app.models.scraping import ScrapeRequest, ScrapeResponse

# [Junior Dev Note]
# Rust 서비스의 주소입니다. Docker Compose 등을 쓸 때는 'http://scraper-engine:3000'이 될 수 있습니다.
RUST_SERVICE_URL = "http://localhost:3000/scrape"

class RustScraperClient:
    """
    Rust Scraper Engine ("The Muscle") 과 통신하는 클라이언트입니다.
    httpx(비동기 HTTP 클라이언트)를 사용하여 네트워크 I/O 동안 메인 스레드가 멈추지 않게 합니다.
    """
    
    async def scrape(self, request: ScrapeRequest) -> ScrapeResponse:
        async with httpx.AsyncClient() as client:
            try:
                # [Junior Dev Note]
                # Pydantic 모델(.model_dump())을 사용해 JSON으로 직렬화하여 전송합니다.
                response = await client.post(
                    RUST_SERVICE_URL, 
                    json=request.model_dump(), 
                    timeout=3.0  # 3초 안에 응답 없으면 바로 Fail (Fail-Fast 전략)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ScrapeResponse(
                        success=data.get("success", False),
                        data=data.get("data", {}),
                        error=data.get("error"),
                        source="auth_rust_engine"
                    )
                else:
                    logging.warning(f"Rust Scraper returned status {response.status_code}")
                    return ScrapeResponse(success=False, error=f"Status {response.status_code}", source="rust_error")
                    
            except Exception as e:
                # 연결 거부 등 네트워크 에러 시
                logging.error(f"Failed to connect to Rust Scraper: {e}")
                return ScrapeResponse(success=False, error=str(e), source="rust_network_error")
