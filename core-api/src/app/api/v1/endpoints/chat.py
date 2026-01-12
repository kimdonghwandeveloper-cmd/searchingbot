from fastapi import APIRouter, Depends
from app.models.mall import MallConfig
from app.middleware.security import get_current_mall

router = APIRouter()

@router.post("/")
async def chat_endpoint(
    # [Junior Dev Note]
    # get_current_mall 함수가 성공적으로 실행되어야만 이 함수가 호출됩니다.
    # 실패 시 401/403 에러가 자동으로 리턴됩니다.
    current_mall: MallConfig = Depends(get_current_mall)
):
    return {
        "message": f"Hello, {current_mall.shop_name}!",
        "plan": current_mall.plan_tier,
        "remaining_quota": current_mall.monthly_limit
    }
