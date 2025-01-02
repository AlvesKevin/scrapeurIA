from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import scraping
from app.database.mongodb import MongoDB
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Scraping Platform API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(scraping.router, prefix="/api/v1", tags=["scraping"])

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    try:
        # Initialise la connexion MongoDB
        MongoDB.get_client()
        logger.info("Application démarrée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Événement d'arrêt de l'application"""
    try:
        # Ferme la connexion MongoDB
        MongoDB.close()
        logger.info("Application arrêtée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt de l'application: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Erreur non gérée: {str(exc)}")
    return {"detail": str(exc)} 