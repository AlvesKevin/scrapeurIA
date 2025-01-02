from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId

class ScrapingConfig(BaseModel):
    selectors: Dict[str, str] = {}
    pagination: bool = False
    max_pages: Optional[int] = None
    navigation_rules: Optional[Dict[str, Any]] = None
    extraction_method: str = "static"
    restrictions: List[str] = []

class ScrapingTask(BaseModel):
    id: str = Field(alias='_id')
    url: str
    description: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    config: ScrapingConfig = ScrapingConfig()
    results_id: Optional[str] = None
    template_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }

    @field_validator('id', 'results_id', 'template_id')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @classmethod
    def from_mongo(cls, data: Dict):
        """Crée une instance à partir des données MongoDB"""
        if data:
            # Convertit les ObjectId en strings
            if '_id' in data:
                data['_id'] = str(data['_id'])
            if 'results_id' in data and isinstance(data['results_id'], ObjectId):
                data['results_id'] = str(data['results_id'])
            if 'template_id' in data and isinstance(data['template_id'], ObjectId):
                data['template_id'] = str(data['template_id'])
            return cls(**data)
        return None

class ScrapingTaskCreate(BaseModel):
    url: str
    description: str
    config: Optional[Dict[str, Any]] = None
    export_format: str = "json" 