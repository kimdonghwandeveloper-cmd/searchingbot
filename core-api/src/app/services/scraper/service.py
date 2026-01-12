from app.models.scraping import ScrapeRequest, ScrapeResponse
from app.services.scraper.rust_client import RustScraperClient
from app.services.scraper.fallback import PlaywrightFallback
import logging

class HybridScraperService:
    """
    스크래핑 오케스트레이터 (The Relay)
    Rust와 Playwright를 조합하여 최적의 결과를 냅니다.
    """
    def __init__(self):
        self.rust_client = RustScraperClient()
        self.playwright_client = PlaywrightFallback()

    async def scrape_url(self, url: str, selectors: dict) -> ScrapeResponse:
        request = ScrapeRequest(url=url, selectors=selectors)
        
        # 1. Round 1: Rust Engine (Fast)
        # 비용이 저렴하고 빠르므로 먼저 시도합니다.
        logging.info(f"Attempting Rust scrape for {url}")
        result = await self.rust_client.scrape(request)
        
        if result.success:
            # 성공 시 데이터 검증 로직이 추가될 수 있음 (예: 필수 필드 누락 여부)
            if self._validate_data(result.data):
                logging.info("Rust scrape successful")
                return result
            else:
                logging.warning("Rust scrape returned empty/invalid data. Switching to fallback.")
        
        # 2. Round 2: Playwright Fallback (Slow but Robust)
        # Rust가 실패했거나(403 Block), 데이터가 비어있으면(JS Rendering 필요) 실행합니다.
        logging.info(f"Switching to Playwright fallback for {url}")
        return await self.playwright_client.scrape(request)

    def _validate_data(self, data: dict) -> bool:
        """
        데이터가 유효한지 검사합니다.
        예: 모든 필드 값이 None이면 실패로 간주.
        """
        if not data:
            return False
        # 값(value) 중에 하나라도 내용이 있으면 성공으로 간주 (단순화된 로직)
        return any(v for v in data.values())

# 전역 인스턴스
scraper_service = HybridScraperService()
