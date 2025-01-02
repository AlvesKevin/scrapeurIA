from typing import Dict, Type, BinaryIO, List, Any
from .base import ExportStrategy
from .csv_exporter import CSVExporter
from .excel_exporter import ExcelExporter
from .json_exporter import JSONExporter

class ExportManager:
    def __init__(self):
        self.exporters: Dict[str, Type[ExportStrategy]] = {
            "csv": CSVExporter,
            "excel": ExcelExporter,
            "json": JSONExporter
        }
    
    async def export_data(
        self,
        data: List[Dict[str, Any]],
        format: str
    ) -> tuple[BinaryIO, str, str]:
        """
        Exporte les données dans le format demandé
        Retourne: (données binaires, type MIME, extension de fichier)
        """
        if format not in self.exporters:
            raise ValueError(f"Format d'export non supporté: {format}")
            
        exporter = self.exporters[format]()
        output = await exporter.export_data(data)
        
        return (
            output,
            exporter.get_content_type(),
            exporter.get_file_extension()
        ) 