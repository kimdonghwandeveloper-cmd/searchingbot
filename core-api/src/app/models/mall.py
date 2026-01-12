from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_json_schema import JsonSchemaValue
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.function_plain_schema(ObjectId),
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

class MallConfig(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    client_id: str = Field(..., description="Unique client identifier")
    shop_name: str
    api_key: str = Field(..., description="Hashed API Key")
    allowed_domains: List[str] = Field(default_factory=list, description="CORS allowed origins")
    scraping_rules: dict = Field(default_factory=dict, description="JSON selectors for scraping")
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
