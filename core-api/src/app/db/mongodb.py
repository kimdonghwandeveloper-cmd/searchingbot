from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_db() -> AsyncIOMotorClient:
    return db.client

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Send a ping to confirm a successful connection
        await db.client.admin.command('ping')
        logging.info("Successfully connected to MongoDB Atlas")
    except Exception as e:
        logging.error(f"Could not connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logging.info("MongoDB connection closed")
