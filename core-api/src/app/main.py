from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.api import api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Secure Mall Chatbot API is running"}
