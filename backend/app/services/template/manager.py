from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from app.models.template import ScrapingTemplate
from app.database.mongodb import get_database
from bson import ObjectId

class TemplateManager:
    def __init__(self):
        self.db = get_database()
        
    async def create_template(self, template_data: Dict[str, Any]) -> str:
        """Crée un nouveau template de scraping"""
        template = ScrapingTemplate(
            name=template_data["name"],
            description=template_data["description"],
            site_pattern=template_data["site_pattern"],
            config=template_data["config"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.scraping_templates.insert_one(template.dict())
        return str(result.inserted_id)
    
    async def find_matching_template(self, url: str) -> Optional[Dict[str, Any]]:
        """Trouve un template compatible avec l'URL donnée"""
        templates = await self.db.scraping_templates.find().to_list(None)
        
        for template in templates:
            if re.match(template["site_pattern"], url):
                # Incrémente le compteur d'utilisation
                await self.db.scraping_templates.update_one(
                    {"_id": template["_id"]},
                    {"$inc": {"usage_count": 1}}
                )
                return template
        
        return None
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un template existant"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.db.scraping_templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def get_templates(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère la liste des templates avec pagination"""
        return await self.db.scraping_templates.find() \
            .skip(skip) \
            .limit(limit) \
            .to_list(None) 