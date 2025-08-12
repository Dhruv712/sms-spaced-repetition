from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# Load .env values into environment variables
load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # LoopMessage
    LOOPMESSAGE_AUTH_KEY: Optional[str] = None
    LOOPMESSAGE_SECRET_KEY: Optional[str] = None
    LOOPMESSAGE_SENDER_NAME: Optional[str] = None
    
    # Test
    TEST_PHONE_NUMBER: Optional[str] = None
    
    # LLM APIs
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # App Settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production!
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()