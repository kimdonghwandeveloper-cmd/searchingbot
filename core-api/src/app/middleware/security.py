from fastapi import Depends, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from app.db.mongodb import get_db
from app.models.mall import MallConfig
from motor.motor_asyncio import AsyncIOMotorClient
import logging

# [Junior Dev Note]
# API Key는 헤더의 "X-API-KEY" 필드 값을 참조합니다.
# auto_error=False로 설정하여 미들웨어에서 직접 에러를 처리할 수 있게 합니다.
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def get_current_mall(
    request: Request,
    api_key: str = Security(api_key_header),
    db: AsyncIOMotorClient = Depends(get_db)
) -> MallConfig:
    """
    API 요청의 보안을 담당하는 핵심 함수입니다.
    1. API Key 존재 여부 확인
    2. DB에서 MallConfig 조회 및 유효성 검사
    3. Origin (도메인) 검사 (CORS 우회 방지)
    """
    
    # 1. API Key 검사
    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-KEY header"
        )
    
    # 2. DB 조회
    # [Junior Dev Note]
    # 실제 프로덕션에서는 API Key를 해싱해서 비교해야 하지만, 초기 개발 단계에서는 평문 비교를 합니다.
    # 추후 bcrypt 등으로 업그레이드할 예정입니다.
    row = await db.mall_configs.find_one({"api_key": api_key})
    
    if not row:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    mall = MallConfig(**row)
    
    if not mall.is_active:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This mall account is inactive."
        )

    # 3. Domain (Origin) 검사
    # [Junior Dev Note]
    # 요청을 보낸 곳(Origin)이 허용된 도메인 리스트에 있는지 확인합니다.
    # API Key가 유출되더라도, 해커가 자신의 로컬호스트나 다른 사이트에서 사용하는 것을 막습니다.
    origin = request.headers.get("origin")
    
    # Origin이 없는 경우(배포 전 테스트 툴 등)는 개발 모드에서만 허용하거나, 정책을 결정해야 합니다.
    # 여기서는 Origin이 있으면 무조건 검사합니다.
    if origin:
        # http://myshop.com -> myshop.com (프로토콜 제거 등 정규화 로직이 필요할 수 있음)
        # 현재는 단순 문자열 포함 여부로 체크
        is_allowed = any(allowed in origin for allowed in mall.allowed_domains)
        if not is_allowed:
            logging.warning(f"Blocked request from unauthorized origin: {origin}")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Origin '{origin}' is not whitelisted for this API Key."
            )
            
    return mall
