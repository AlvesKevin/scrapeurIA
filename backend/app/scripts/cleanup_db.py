from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import logging

logger = logging.getLogger(__name__)

async def cleanup_database():
    """Nettoie et réinitialise la base de données"""
    # Connexion à MongoDB
    client = AsyncIOMotorClient("mongodb://root:aWOTQxNcHV4Sc5FoQjmdAhV5iZQQjoISdDWMz2xEVublZEf1VXCMBAwPN0sz759i@62.72.18.21:27017/")
    db = client.scraping_db
    
    try:
        # Liste toutes les collections
        collections = await db.list_collection_names()
        logger.info(f"Collections trouvées: {collections}")
        
        # Supprime toutes les collections existantes
        for collection in collections:
            await db.drop_collection(collection)
            logger.info(f"Collection {collection} supprimée")
        
        # Crée les nouvelles collections avec les index
        await db.create_collection("scraping_tasks")
        await db.scraping_tasks.create_index("created_at")
        await db.scraping_tasks.create_index("status")
        logger.info("Collection scraping_tasks créée avec les index")
        
        await db.create_collection("scraping_results")
        await db.scraping_results.create_index("task_id")
        await db.scraping_results.create_index("created_at")
        logger.info("Collection scraping_results créée avec les index")
        
        logger.info("Nettoyage de la base de données terminé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de la base de données: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(cleanup_database()) 