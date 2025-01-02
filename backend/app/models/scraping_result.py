from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

class ScrapingResult(BaseModel):
    id: str = Field(alias='_id')
    task_id: str
    data: List[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None  # Rend le champ optionnel
    metadata: Dict[str, Any]

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }

    @classmethod
    def from_mongo(cls, data: Dict):
        """Crée une instance à partir des données MongoDB"""
        if data:
            # Convertit les ObjectId en strings
            if '_id' in data:
                data['_id'] = str(data['_id'])
            if 'task_id' in data and isinstance(data['task_id'], ObjectId):
                data['task_id'] = str(data['task_id'])
            
            # Assure que les dates sont au bon format
            if 'created_at' in data and isinstance(data['created_at'], dict):
                data['created_at'] = datetime.fromisoformat(data['created_at']['$date'].replace('Z', '+00:00'))
            
            if 'updated_at' in data and isinstance(data['updated_at'], dict):
                data['updated_at'] = datetime.fromisoformat(data['updated_at']['$date'].replace('Z', '+00:00'))
            
            return cls(**data)
        return None 