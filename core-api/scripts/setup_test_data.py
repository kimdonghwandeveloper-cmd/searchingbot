import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

async def setup_data():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DB_NAME]
    collection = db.mall_configs
    
    # Test Data
    test_mall = {
        "client_id": "test-client-001",
        "shop_name": "Test Shop",
        "api_key": "test-key-123",  # Simple key for testing
        "allowed_domains": ["localhost", "127.0.0.1"],
        "plan_tier": "pro",
        "is_active": True,
        "scraping_rules": {
            "title": "h1.title", 
            "price": ".price"
        }
    }
    
    # Upsert (Update if exists, Insert if not)
    await collection.replace_one(
        {"api_key": "test-key-123"},
        test_mall,
        upsert=True
    )
    
    print(f"✅ Test Mall inserted successfully!")
    print(f"🔑 API Key: {test_mall['api_key']}")
    print(f"🌐 Allowed Domains: {test_mall['allowed_domains']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_data())
