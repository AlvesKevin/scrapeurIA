from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ScrapingStrategy(ABC):
    @abstractmethod
    async def extract_data(self, url: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les données selon la configuration fournie"""
        pass
    
    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """Valide l'URL avant le scraping"""
        pass
    
    @abstractmethod
    async def handle_pagination(self, url: str, config: Dict[str, Any]) -> List[str]:
        """Gère la pagination si nécessaire"""
        pass 