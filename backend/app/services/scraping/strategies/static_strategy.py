import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import logging
import re

logger = logging.getLogger(__name__)

class StaticStrategy:
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte extrait"""
        if not text:
            return None
        # Supprime les espaces multiples et les retours à la ligne
        cleaned = ' '.join(text.split())
        # Supprime les espaces avant la ponctuation
        cleaned = re.sub(r'\s+([,.!?])', r'\1', cleaned)
        return cleaned

    async def extract_data(self, url: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les données d'une page web statique"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur HTTP {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    selectors = config.get('selectors', {})
                    logger.info(f"Utilisation des sélecteurs: {selectors}")
                    
                    # Trouve tous les conteneurs
                    containers = soup.select(selectors.get('item_container', 'body'))
                    logger.info(f"Nombre de conteneurs trouvés: {len(containers)}")
                    
                    data = []
                    for container in containers:
                        item_data = {}
                        for field, selector in selectors.items():
                            if field != 'item_container':
                                try:
                                    elements = container.select(selector)
                                    if elements:
                                        if len(elements) > 1:
                                            # Pour les champs qui peuvent avoir plusieurs valeurs
                                            item_data[field] = [self._clean_text(el.get_text()) for el in elements]
                                        else:
                                            item_data[field] = self._clean_text(elements[0].get_text())
                                    else:
                                        item_data[field] = None
                                except Exception as e:
                                    logger.error(f"Erreur lors de l'extraction du champ {field}: {str(e)}")
                                    item_data[field] = None
                        
                        if any(item_data.values()):
                            data.append(item_data)
                    
                    logger.info(f"Données extraites: {data}")
                    return data
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données: {str(e)}")
            raise 