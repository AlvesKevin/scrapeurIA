from typing import List, Dict, Any, BinaryIO
from io import BytesIO
import json
from .base import ExportStrategy

class JSONExporter(ExportStrategy):
    async def export_data(self, data: List[Dict[str, Any]]) -> BinaryIO:
        output = BytesIO()
        json.dump(data, output, ensure_ascii=False, indent=2)
        output.seek(0)
        return output
    
    def get_content_type(self) -> str:
        return "application/json"
    
    def get_file_extension(self) -> str:
        return "json" 