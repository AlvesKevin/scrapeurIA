from typing import List, Dict, Any, BinaryIO
from io import BytesIO
import pandas as pd
from .base import ExportStrategy

class ExcelExporter(ExportStrategy):
    async def export_data(self, data: List[Dict[str, Any]]) -> BinaryIO:
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Données')
            
            # Ajuste automatiquement la largeur des colonnes
            worksheet = writer.sheets['Données']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.set_column(idx, idx, max_length + 2)
        
        output.seek(0)
        return output
    
    def get_content_type(self) -> str:
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    def get_file_extension(self) -> str:
        return "xlsx" 