from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime
from bson import ObjectId

async def cleanup_database():
    # Connexion à MongoDB
    client = AsyncIOMotorClient("mongodb://root:aWOTQxNcHV4Sc5FoQjmdAhV5iZQQjoISdDWMz2xEVublZEf1VXCMBAwPN0sz759i@62.72.18.21:27017/")
    db = client.scraping_db
    
    try:
        # 1. Supprime les anciennes collections si elles existent
        collections = await db.list_collection_names()
        for collection in collections:
            if collection in ['scraping_tasks', 'scraping_results']:
                await db[collection].drop()
                print(f"Collection {collection} supprimée")
        
        # 2. Crée les nouvelles collections avec les bons index
        await db.create_collection('scraping_tasks')
        await db.scraping_tasks.create_index('created_at')
        await db.scraping_tasks.create_index('status')
        
        await db.create_collection('scraping_results')
        await db.scraping_results.create_index('task_id')
        await db.scraping_results.create_index('created_at')
        
        print("Collections recréées avec les index appropriés")
        
        # 3. Insère quelques tâches de test si nécessaire
        test_tasks = [
            {
                "_id": ObjectId(),
                "url": "https://example.com/test1",
                "description": "Tâche de test 1",
                "status": "pending",
                "created_at": datetime.utcnow(),
                "config": {
                    "selectors": {},
                    "pagination": False,
                    "max_pages": 1
                },
                "metadata": {}
            },
            {
                "_id": ObjectId(),
                "url": "https://example.com/test2",
                "description": "Tâche de test 2",
                "status": "completed",
                "created_at": datetime.utcnow(),
                "config": {
                    "selectors": {},
                    "pagination": False,
                    "max_pages": 1
                },
                "metadata": {}
            }
        ]
        
        result = await db.scraping_tasks.insert_many(test_tasks)
        print(f"Tâches de test insérées: {len(result.inserted_ids)}")
        
    except Exception as e:
        print(f"Erreur lors du nettoyage de la base de données: {str(e)}")
    finally:
        client.close()
        print("Connexion fermée")

if __name__ == "__main__":
    asyncio.run(cleanup_database()) 