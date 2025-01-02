import httpx
import logging
from typing import Dict, Any
from bs4 import BeautifulSoup
from app.core.config import settings
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        logger.info(f"Initialisation OllamaClient avec URL: {self.base_url} et modèle: {self.model}")
        
    async def _generate(self, prompt: str) -> str:
        """Génère une réponse à partir d'un prompt en utilisant Ollama"""
        try:
            logger.info(f"Envoi de la requête à Ollama: {self.base_url}/api/generate")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info("Tentative de connexion à Ollama...")
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                logger.info(f"Réponse d'Ollama reçue avec status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    return result["response"]
                else:
                    logger.error(f"Erreur Ollama: {response.status_code} - {response.text}")
                    raise Exception(f"Erreur Ollama: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de la communication avec Ollama: {str(e)}")
            raise

    async def _get_page_content(self, url: str) -> str:
        """Récupère le contenu HTML de la page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.text
                else:
                    raise Exception(f"Erreur HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la page: {str(e)}")
            raise

    async def analyze_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la requête et génère une configuration de scraping appropriée"""
        try:
            # Récupère le contenu de la page
            html_content = await self._get_page_content(request['url'])
            
            # Analyse le HTML avec BeautifulSoup pour obtenir la structure
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Crée un résumé de la structure HTML
            structure_summary = self._get_structure_summary(soup)
            
            prompt = f"""You are a web scraping expert. Analyze this HTML structure and create a scraping configuration.

URL: {request['url']}
Description: {request['description']}

HTML Structure Summary:
{structure_summary}

Create a JSON configuration with precise CSS selectors that will extract clean, well-formatted data.
For therapist data, ensure:
1. Each field is extracted separately (name, title, address, etc.)
2. Text is properly cleaned (remove extra spaces, newlines)
3. Structured data is preserved (specialties as arrays, etc.)

Return a JSON object with this structure:
{{
    "selectors": {{
        "item_container": "selector_for_each_therapist",
        "name": "selector_for_name",
        "titles": "selector_for_professional_titles",
        "address": "selector_for_address",
        "phone": "selector_for_phone",
        "specialties": "selector_for_specialties",
        "description": "selector_for_description"
    }},
    "pagination": false,
    "max_pages": 1,
    "extraction_method": "static",
    "restrictions": []
}}

IMPORTANT:
1. Do NOT include any comments in the JSON
2. Do NOT include any explanatory text
3. Only use double quotes for strings
4. Return ONLY the JSON object"""

            response = await self._generate(prompt)
            try:
                # Nettoie la réponse
                cleaned_response = response.strip()
                
                # Supprime tout ce qui n'est pas entre les accolades du JSON
                start = cleaned_response.find('{')
                end = cleaned_response.rfind('}') + 1
                if start >= 0 and end > start:
                    cleaned_response = cleaned_response[start:end]
                
                # Supprime les commentaires en ligne
                cleaned_response = re.sub(r'//.*$', '', cleaned_response, flags=re.MULTILINE)
                
                # Supprime les blocs de code markdown
                if "```" in cleaned_response:
                    parts = cleaned_response.split("```")
                    for i, part in enumerate(parts):
                        if i % 2 == 1:  # Partie entre ```
                            if part.startswith('json'):
                                part = part[4:]
                            parts[i] = part.strip()
                    cleaned_response = ''.join(parts)
                
                logger.info(f"Réponse nettoyée: {cleaned_response}")
                
                config = json.loads(cleaned_response)
                logger.info(f"Configuration générée: {config}")
                
                # Validation des sélecteurs
                if not config.get("selectors"):
                    raise ValueError("La configuration doit contenir des sélecteurs")
                
                # Vérifie que les sélecteurs sont des chaînes non vides
                for key, value in config["selectors"].items():
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError(f"Le sélecteur '{key}' est invalide")
                
                return config
                
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de parsing JSON: {str(e)}")
                logger.error(f"Réponse brute: {response}")
                raise ValueError("La réponse de l'IA n'est pas un JSON valide")

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la requête: {str(e)}")
            raise

    def _get_structure_summary(self, soup: BeautifulSoup) -> str:
        """Crée un résumé de la structure HTML pertinente"""
        summary = []
        
        # Trouve les éléments qui pourraient contenir des données
        for tag in soup.find_all(['div', 'span', 'p', 'a', 'h1', 'h2', 'h3', 'section']):
            classes = tag.get('class', [])
            if classes:
                class_str = '.'.join(classes)
                summary.append(f"{tag.name}.{class_str}")
        
        return "\n".join(sorted(set(summary)))[:1500]  # Limite la taille du résumé

    def _validate_selectors(self, soup: BeautifulSoup, selectors: Dict[str, str]):
        """Valide que les sélecteurs existent dans le HTML"""
        for key, selector in selectors.items():
            if key != "item_container":  # Le conteneur peut être le body
                elements = soup.select(selector)
                if not elements:
                    logger.warning(f"Le sélecteur '{selector}' pour '{key}' ne trouve aucun élément")