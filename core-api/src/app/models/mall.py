from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

from typing import Annotated, Any, Callable
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(value: str) -> ObjectId:
            return ObjectId(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(ObjectId),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

PyObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]

class MallConfig(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    client_id: str = Field(..., description="쇼핑몰 고유 식별자 (UUID)")
    shop_name: str
    api_key: str = Field(..., description="보안을 위해 해싱된 API 키")
    allowed_domains: List[str] = Field(default_factory=list, description="CORS 허용 도메인 목록 (Origin 검사용)")
    scraping_rules: dict = Field(default_factory=dict, description="크롤링용 CSS 선택자 (Title, Price 등)")
    plan_tier: str = Field(default="free", pattern="^(free|basic|pro)$")
    monthly_limit: int = 1000
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UsageLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    mall_id: str
    endpoint: str
    tokens_used: int = 0
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
