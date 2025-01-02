import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class StaticScrapingStrategy:
    async def extract_data(self, url: str, config: Dict[str, Any], proxy: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Extrait les données d'une page web statique"""
        logger.info(f"Extraction des données depuis {url}")
        
        async with httpx.AsyncClient(proxies=proxy) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            data = []
            
            # Utilise les sélecteurs de la configuration
            selectors = config.get('selectors', {})
            
            # Pour Fiverr
            if 'fiverr.com' in url:
                packages = soup.select('.package-content')
                for package in packages:
                    price = package.select_one('.price-wrapper')
                    title = package.select_one('.package-title')
                    description = package.select_one('.package-description')
                    
                    data.append({
                        'title': title.text.strip() if title else None,
                        'price': price.text.strip() if price else None,
                        'description': description.text.strip() if description else None
                    })
            
            # Pour annuaire-therapeutes
            elif 'annuaire-therapeutes.com' in url:
                therapists = soup.select('.therapist-card')
                for therapist in therapists:
                    name = therapist.select_one('.therapist-name')
                    specialty = therapist.select_one('.specialty')
                    location = therapist.select_one('.location')
                    
                    data.append({
                        'name': name.text.strip() if name else None,
                        'specialty': specialty.text.strip() if specialty else None,
                        'location': location.text.strip() if location else None
                    })
            
            logger.info(f"Données extraites: {len(data)} éléments")
            return data

    async def handle_pagination(self, url: str, config: Dict[str, Any]) -> List[str]:
        """Gère la pagination si nécessaire"""
        if not config.get('pagination', False):
            return [url]
            
        urls = [url]
        max_pages = config.get('max_pages', 1)
        
        # Ajouter la logique de pagination ici si nécessaire
        
        return urls 