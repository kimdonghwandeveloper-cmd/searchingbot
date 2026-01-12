from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ScrapeRequest(BaseModel):
    """
    Rust Scraper Engine으로 보낼 요청 데이터 규격입니다.
    """
    url: str = Field(..., description="스크래핑할 대상 URL")
    selectors: Dict[str, str] = Field(..., description="추출할 데이터의 CSS 선택자 (예: {'title': '#product-name'})")
    user_agent: Optional[str] = Field(None, description="특정 User-Agent가 필요한 경우 설정")

class ScrapeResponse(BaseModel):
    """
    스크래핑 결과를 담는 공통 응답 규격입니다.
    Rust에서 오든, Playwright에서 오든 이 포맷으로 통일합니다.
    """
    success: bool = Field(..., description="스크래핑 성공 여부")
    data: Dict[str, Any] = Field(default_factory=dict, description="추출된 데이터 (title, price 등)")
    error: Optional[str] = Field(None, description="실패 시 에러 메시지")
    source: str = Field(..., description="데이터 출처 (Rust vs Playwright)")
