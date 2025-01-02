import csv
from io import StringIO, BytesIO
from typing import List, Dict, Any, BinaryIO
from .base import ExportStrategy

class CSVExporter(ExportStrategy):
    async def export_data(self, data: List[Dict[str, Any]]) -> BinaryIO:
        if not data:
            return BytesIO()
            
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        
        writer.writeheader()
        writer.writerows(data)
        
        # Convertit en BytesIO pour le retour
        binary_output = BytesIO(output.getvalue().encode('utf-8'))
        output.close()
        
        return binary_output
    
    def get_content_type(self) -> str:
        return "text/csv"
    
    def get_file_extension(self) -> str:
        return "csv" 