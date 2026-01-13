from pydantic import BaseModel
from typing import List, Optional

# Struktur Detail per Bahan
class IngredientDetail(BaseModel):
    name: str           # Contoh: "Sugar"
    category: str       # Contoh: "Plant Based", "Chemical", "Animal"
    status: str         # "SAFE", "WARNING", "HARAM"
    description: str    # "Pemanis alami dari tebu."

class AnalysisResult(BaseModel):
    status: str          
    score: float         
    # Kita upgrade ini jadi list of objects
    ingredients_analysis: List[IngredientDetail] 
    explanation: str
    raw_text: str