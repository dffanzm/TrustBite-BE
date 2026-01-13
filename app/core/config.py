import os
from pydantic_settings import BaseSettings

# ✅ FIX: Import 'ai_engine' SUDAH DIHAPUS dari sini biar gak muter-muter (circular import).

class Settings(BaseSettings):
    PROJECT_NAME: str = "TrustBite AI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Karena di .env kamu sudah ada API_SECRET_KEY, 
    # di sini cukup definisikan tipe datanya aja (str).
    API_SECRET_KEY: str 
    
    # AI SETTINGS 
    OCR_LANGUAGES: list = ['en', 'id']
    CONFIDENCE_THRESHOLD: int = 80 

    class Config:
        env_file = ".env"
        extra = "ignore" 

settings = Settings()