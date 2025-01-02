from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.template.manager import TemplateManager

router = APIRouter()
template_manager = TemplateManager()

@router.post("/templates", response_model=Dict[str, str])
async def create_template(template_data: Dict[str, Any]):
    """Crée un nouveau template de scraping"""
    try:
        template_id = await template_manager.create_template(template_data)
        return {"template_id": template_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_templates(skip: int = 0, limit: int = 10):
    """Liste les templates disponibles"""
    templates = await template_manager.get_templates(skip, limit)
    return templates

@router.get("/templates/match")
async def find_matching_template(url: str):
    """Trouve un template compatible avec l'URL donnée"""
    template = await template_manager.find_matching_template(url)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Aucun template compatible trouvé"
        )
    return template

@router.put("/templates/{template_id}")
async def update_template(template_id: str, updates: Dict[str, Any]):
    """Met à jour un template existant"""
    success = await template_manager.update_template(template_id, updates)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Template non trouvé"
        )
    return {"message": "Template mis à jour avec succès"} 