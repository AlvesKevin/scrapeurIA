from abc import ABC, abstractmethod
from typing import List, Dict, Any, BinaryIO, Protocol

class ExportStrategy(ABC):
    @abstractmethod
    async def export_data(self, data: List[Dict[str, Any]]) -> BinaryIO:
        """Exporte les données dans le format spécifique"""
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Retourne le type MIME du format d'export"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Retourne l'extension de fichier pour ce format"""
        pass 