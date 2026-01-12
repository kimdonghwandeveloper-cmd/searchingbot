from playwright.async_api import async_playwright
import logging
from app.models.scraping import ScrapeRequest, ScrapeResponse

class PlaywrightFallback:
    """
    최후의 보루(Fallback)인 Playwright 스크래퍼입니다.
    Rust가 실패하거나 강한 보안(Cloudflare, JS 렌더링 필수)이 걸린 사이트를 뚫을 때 사용합니다.
    """
    
    async def scrape(self, request: ScrapeRequest) -> ScrapeResponse:
        logging.info("Starting Playwright Fallback...")
        
        async with async_playwright() as p:
            # [Junior Dev Note]
            # Headless 모드로 브라우저를 띄웁니다. 
            # 리소스를 많이 먹으므로 꼭 필요할 때만 써야 합니다.
            browser = await p.chromium.launch(headless=True)
            
            try:
                page = await browser.new_page()
                
                # [Junior Dev Note]
                # 네트워크가 Idle 상태가 될 때까지 기다려서 JS 로딩을 보장합니다.
                await page.goto(request.url, wait_until="networkidle", timeout=10000)
                
                extracted_data = {}
                
                # 요청받은 셀렉터들을 순회하며 데이터 추출
                for key, selector in request.selectors.items():
                    # [Junior Dev Note]
                    # query_selector 대신 locator를 사용하는 것이 최신 Playwright 권장 방식입니다.
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        if "::attr(src)" in selector: # 이미지 src 추출 등 특수 처리 (간소화됨)
                             extracted_data[key] = await element.get_attribute("src")
                        else:
                            extracted_data[key] = await element.inner_text()
                    else:
                        extracted_data[key] = None
                
                return ScrapeResponse(
                    success=True,
                    data=extracted_data,
                    source="playwright_fallback"
                )
                
            except Exception as e:
                logging.error(f"Playwright failed: {e}")
                return ScrapeResponse(success=False, error=str(e), source="playwright_error")
            finally:
                await browser.close()
