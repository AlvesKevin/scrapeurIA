from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional, List
from datetime import datetime

class ScrapingTemplate(BaseModel):
    name: str
    description: str
    site_pattern: str  # Regex pattern pour matcher les URLs compatibles
    config: Dict[str, Any]  # Configuration de scraping
    created_at: datetime
    updated_at: Optional[datetime] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 