from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from app.services.export.manager import ExportManager
from app.database.mongodb import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()
export_manager = ExportManager()

@router.get("/export/{task_id}")
async def export_results(task_id: str, format: str = "json"):
    """Exporte les résultats d'une tâche dans le format spécifié"""
    db = get_database()
    
    # Récupère les résultats
    result = await db.scraping_results.find_one({"task_id": task_id})
    if not result:
        raise HTTPException(status_code=404, detail="Résultats non trouvés")
    
    try:
        # Exporte les données
        output, content_type, extension = await export_manager.export_data(
            result["data"],
            format
        )
        
        # Génère le nom du fichier
        filename = f"export_{task_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{extension}"
        
        # Retourne le fichier
        return StreamingResponse(
            output,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 