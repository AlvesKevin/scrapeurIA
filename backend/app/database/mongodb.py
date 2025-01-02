from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            connection_string = "mongodb://root:aWOTQxNcHV4Sc5FoQjmdAhV5iZQQjoISdDWMz2xEVublZEf1VXCMBAwPN0sz759i@62.72.18.21:27017/"
            logger.info(f"Tentative de connexion à MongoDB: {connection_string}")
            cls._client = AsyncIOMotorClient(connection_string)
            logger.info("Connexion à MongoDB établie avec succès")
        return cls._client

    @classmethod
    def get_db(cls):
        client = cls.get_client()
        return client.scraping_db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.info("Connexion à MongoDB fermée") 