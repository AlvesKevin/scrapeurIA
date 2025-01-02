from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List
from app.services.scraping.manager import ScrapingManager
from app.models.scraping_task import ScrapingTask, ScrapingTaskCreate
from app.models.scraping_result import ScrapingResult
from app.database.mongodb import MongoDB

router = APIRouter()

async def get_scraping_manager():
    """Dépendance pour obtenir une instance de ScrapingManager"""
    # Obtient la connexion à la base de données
    client = MongoDB.get_client()
    # Sélectionne la base de données scraping_db
    db = client.scraping_db
    return await ScrapingManager.create(db)

@router.post("/tasks")
async def create_scraping_task(
    task: ScrapingTaskCreate,
    manager: ScrapingManager = Depends(get_scraping_manager)
) -> Dict[str, str]:
    """Crée une nouvelle tâche de scraping"""
    try:
        task_id = await manager.create_task({
            "url": str(task.url),
            "description": task.description,
            "config": task.config or {},
            "export_format": task.export_format
        })
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors de la création de la tâche: {str(e)}"
        )

@router.post("/tasks/{task_id}/execute")
async def execute_scraping_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    manager: ScrapingManager = Depends(get_scraping_manager)
):
    """Lance l'exécution d'une tâche de scraping"""
    background_tasks.add_task(manager.execute_task, task_id)
    return {"message": "Tâche lancée avec succès"}

@router.get("/tasks/{task_id}", response_model=ScrapingTask)
async def get_task_status(
    task_id: str,
    manager: ScrapingManager = Depends(get_scraping_manager)
):
    """Récupère le statut d'une tâche"""
    task = await manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    return task

@router.get("/tasks/{task_id}/results", response_model=ScrapingResult)
async def get_task_results(
    task_id: str,
    manager: ScrapingManager = Depends(get_scraping_manager)
):
    """Récupère les résultats d'une tâche"""
    results = await manager.get_results(task_id)
    if not results:
        raise HTTPException(status_code=404, detail="Résultats non trouvés")
    return results 

@router.get("/tasks", response_model=List[ScrapingTask])
async def list_tasks(
    manager: ScrapingManager = Depends(get_scraping_manager)
):
    """Liste toutes les tâches de scraping"""
    return await manager.get_all_tasks() 

@router.post("/tasks/{task_id}/retry")
async def retry_task(
    task_id: str,
    manager: ScrapingManager = Depends(get_scraping_manager)
):
    """Relance une tâche échouée"""
    await manager.retry_task(task_id)
    return {"message": "Tâche relancée avec succès"}

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    manager: ScrapingManager = Depends(get_scraping_manager)
):
    """Supprime une tâche"""
    await manager.delete_task(task_id)
    return {"message": "Tâche supprimée avec succès"}

@router.get("/tasks/{task_id}/logs")
async def get_task_logs(
    task_id: str,
    manager: ScrapingManager = Depends(get_scraping_manager)
):
    """Récupère les logs d'une tâche"""
    return await manager.get_task_logs(task_id) 