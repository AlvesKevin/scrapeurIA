from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.services.llm.ollama_client import OllamaClient
from app.models.scraping_task import ScrapingTask, ScrapingConfig
from app.models.scraping_result import ScrapingResult
from app.services.scraping.strategies.static_strategy import StaticStrategy

logger = logging.getLogger(__name__)

class ScrapingManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.ollama_client = OllamaClient()
        self.db = db
        self.static_strategy = StaticStrategy()  # Initialise la stratégie statique
        logger.info(f"ScrapingManager initialisé avec la base de données: {db.name}")

    @classmethod
    async def create(cls, db: AsyncIOMotorDatabase) -> 'ScrapingManager':
        """Factory method pour créer une instance avec initialisation asynchrone"""
        instance = cls(db)
        await instance._ensure_collections()
        return instance

    async def _ensure_collections(self):
        """S'assure que les collections nécessaires existent"""
        collections = await self.db.list_collection_names()
        logger.info(f"Collections existantes: {collections}")
        
        if "scraping_tasks" not in collections:
            await self.db.create_collection("scraping_tasks")
            logger.info("Collection scraping_tasks créée")
            
        if "scraping_results" not in collections:
            await self.db.create_collection("scraping_results")
            logger.info("Collection scraping_results créée")

    async def create_task(self, request: Dict[str, Any]) -> str:
        try:
            logger.info(f"Création d'une nouvelle tâche: {request}")
            
            # Crée un nouvel ObjectId pour la tâche
            task_id = ObjectId()
            
            # Analyse de la requête par le LLM
            config = await self.ollama_client.analyze_request(request)
            
            # Création de la tâche avec l'ID
            task = ScrapingTask(
                id=str(task_id),  # Convertit l'ObjectId en string
                url=request["url"],
                description=request["description"],
                status="pending",
                created_at=datetime.utcnow(),
                config=ScrapingConfig(**config),
                template_id=None
            )
            
            # Convertit l'objet en dictionnaire
            task_dict = task.dict(by_alias=True)
            task_dict['_id'] = task_id  # Utilise l'ObjectId pour MongoDB
            
            try:
                # Sauvegarde dans MongoDB
                await self.db.scraping_tasks.insert_one(task_dict)
                
                # Vérifie que la tâche a bien été sauvegardée
                saved_task = await self.db.scraping_tasks.find_one({"_id": task_id})
                if not saved_task:
                    raise Exception("La tâche n'a pas été sauvegardée correctement")
                    
                logger.info(f"Tâche sauvegardée avec succès. ID: {str(task_id)}")
                return str(task_id)
                
            except Exception as db_error:
                logger.error(f"Erreur lors de la sauvegarde dans MongoDB: {str(db_error)}")
                raise
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de la tâche: {str(e)}")
            raise

    async def get_task(self, task_id: str) -> Optional[ScrapingTask]:
        """Récupère une tâche par son ID"""
        try:
            result = await self.db.scraping_tasks.find_one({"_id": ObjectId(task_id)})
            return ScrapingTask.from_mongo(result)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la tâche {task_id}: {str(e)}")
            raise

    async def get_results(self, task_id: str) -> Optional[ScrapingResult]:
        """Récupère les résultats d'une tâche"""
        try:
            # Récupère d'abord la tâche pour vérifier l'existence du results_id
            task = await self.get_task(task_id)
            if not task:
                raise ValueError("Tâche non trouvée")
            
            if not task.results_id:
                raise ValueError("Aucun résultat disponible pour cette tâche")
            
            # Récupère les résultats
            result = await self.db.scraping_results.find_one({"_id": ObjectId(task.results_id)})
            if not result:
                raise ValueError("Résultats non trouvés")
            
            return ScrapingResult.from_mongo(result)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des résultats: {str(e)}")
            raise

    async def execute_task(self, task_id: str):
        """Exécute une tâche de scraping"""
        try:
            # Met à jour le statut
            await self.db.scraping_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"status": "running", "updated_at": datetime.utcnow()}}
            )
            
            # Récupère la tâche
            task = await self.get_task(task_id)
            if not task:
                raise ValueError("Tâche non trouvée")
            
            logger.info(f"Exécution de la tâche {task_id}")
            
            # Utilise la configuration fournie par l'IA via ollama_client
            scraping_config = task.config.dict()
            logger.info(f"Configuration de scraping: {scraping_config}")
            
            # Exécute le scraping avec la stratégie appropriée
            start_time = datetime.utcnow()
            data = await self.static_strategy.extract_data(
                str(task.url),
                scraping_config
            )
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Sauvegarde les résultats
            result = {
                "task_id": task_id,
                "data": data,
                "status": "completed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": {
                    "total_items": len(data),
                    "extraction_date": datetime.utcnow().isoformat(),
                    "processing_time": processing_time,
                    "url": str(task.url),
                    "config_used": scraping_config
                }
            }
            
            results_id = await self.db.scraping_results.insert_one(result)
            
            # Met à jour la tâche
            await self.db.scraping_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {
                    "$set": {
                        "status": "completed",
                        "updated_at": datetime.utcnow(),
                        "results_id": str(results_id.inserted_id)
                    }
                }
            )
            
            logger.info(f"Tâche {task_id} terminée avec succès. {len(data)} éléments extraits.")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la tâche {task_id}: {str(e)}")
            await self.db.scraping_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {
                    "$set": {
                        "status": "failed",
                        "updated_at": datetime.utcnow(),
                        "metadata.error": str(e)
                    }
                }
            )
            raise

    async def get_all_tasks(self) -> List[ScrapingTask]:
        """Récupère toutes les tâches"""
        try:
            cursor = self.db.scraping_tasks.find()
            tasks = []
            async for doc in cursor:
                # Convertit l'ObjectId en string et l'inclut dans le document
                doc['_id'] = str(doc['_id'])
                # Crée un dictionnaire avec toutes les données nécessaires
                task_dict = {
                    'id': doc['_id'],  # Utilise 'id' au lieu de '_id'
                    'url': doc['url'],
                    'description': doc['description'],
                    'status': doc['status'],
                    'created_at': doc['created_at'],
                    'updated_at': doc.get('updated_at'),
                    'config': doc.get('config', {}),
                    'results_id': doc.get('results_id'),
                    'template_id': doc.get('template_id'),
                    'metadata': doc.get('metadata', {})
                }
                tasks.append(ScrapingTask(**task_dict))
            
            logger.info(f"Nombre de tâches récupérées: {len(tasks)}")
            return tasks
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tâches: {str(e)}")
            raise

    async def delete_task(self, task_id: str):
        """Supprime une tâche et ses résultats associés"""
        try:
            # Vérifie si la tâche existe
            task = await self.get_task(task_id)
            if not task:
                raise ValueError("Tâche non trouvée")

            # Supprime les résultats associés si ils existent
            if task.results_id:
                try:
                    await self.db.scraping_results.delete_one({"_id": ObjectId(task.results_id)})
                    logger.info(f"Résultats de la tâche {task_id} supprimés")
                except Exception as e:
                    logger.warning(f"Erreur lors de la suppression des résultats: {str(e)}")

            # Supprime la tâche
            try:
                result = await self.db.scraping_tasks.delete_one({"_id": ObjectId(task_id)})
                if result.deleted_count == 0:
                    raise ValueError("Tâche non trouvée")
                logger.info(f"Tâche {task_id} supprimée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de la tâche: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la tâche {task_id}: {str(e)}")
            raise 

    async def retry_task(self, task_id: str):
        """Relance une tâche échouée"""
        try:
            # Vérifie si la tâche existe et est en état d'échec
            task = await self.get_task(task_id)
            if not task:
                raise ValueError("Tâche non trouvée")
            
            if task.status != "failed":
                raise ValueError("Seules les tâches en échec peuvent être relancées")
            
            # Réinitialise le statut et les métadonnées d'erreur
            await self.db.scraping_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {
                    "$set": {
                        "status": "pending",
                        "updated_at": datetime.utcnow()
                    },
                    "$unset": {
                        "metadata.error": ""
                    }
                }
            )
            
            logger.info(f"Tâche {task_id} réinitialisée pour nouvelle tentative")
            
            # Exécute la tâche
            await self.execute_task(task_id)
            
        except Exception as e:
            logger.error(f"Erreur lors de la relance de la tâche {task_id}: {str(e)}")
            # Met à jour le statut en cas d'erreur
            await self.db.scraping_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {
                    "$set": {
                        "status": "failed",
                        "updated_at": datetime.utcnow(),
                        "metadata.error": str(e)
                    }
                }
            )
            raise 