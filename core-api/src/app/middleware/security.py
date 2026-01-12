from fastapi import Depends, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from app.db.mongodb import get_db
from app.core.config import settings

# ... (omitted)

async def get_current_mall(
    request: Request,
    api_key: str = Security(api_key_header),
    db: AsyncIOMotorClient = Depends(get_db)
) -> MallConfig:
    # ...
    
    # 2. DB 조회
    # [Junior Dev Note]
    # db는 Client 객체이므로, 데이터베이스명(settings.DB_NAME)을 먼저 선택해야 합니다.
    row = await db[settings.DB_NAME].mall_configs.find_one({"api_key": api_key})
    
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
