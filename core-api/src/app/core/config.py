from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mall Chatbot"
    MONGODB_URL: str
    DB_NAME: str = "mall_chatbot_db"
    OPENAI_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
