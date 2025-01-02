from typing import Dict, Any
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "AI Scraping Platform"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "scraping_db")
    
    # Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Scraping
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Proxy
    USE_PROXY: bool = False
    PROXY_ROTATION_INTERVAL: int = 300  # 5 minutes
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_PERIOD: int = 60  # 1 minute

    class Config:
        case_sensitive = True

settings = Settings() 