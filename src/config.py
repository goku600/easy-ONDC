from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    CHROMA_DB_DIR: str = "data/vector_store"
    # Using the models proven to work in Phase 1
    GEMINI_MODEL_NAME: str = "models/gemini-flash-latest"  
    EMBEDDING_MODEL_NAME: str = "models/gemini-embedding-001"

    # Twilio Settings
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
