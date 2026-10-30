import os
from pathlib import Path
from pydantic_settings import BaseSettings

_current_dir = Path(__file__).resolve().parent
_backend_dir = _current_dir.parent.parent
_root_dir = _backend_dir.parent

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/multimodal_ai"
    
    LLM_API_KEY: str = ""
    EMBEDDING_API_KEY: str = ""
    WEB_SEARCH_API_KEY: str = ""
    
    LLM_MODEL: str = "gemini-3.5-flash-lite"
    VISION_MODEL: str = "gemini-3.5-flash-lite"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5
    
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    class Config:
        env_file = [
            str(_root_dir / ".env"),
            str(_backend_dir / ".env"),
            ".env",
        ]
        env_file_encoding = 'utf-8'
        extra = "ignore"

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
