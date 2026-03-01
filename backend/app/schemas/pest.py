from pydantic import BaseModel
from typing import List, Optional


class PestDetectionResult(BaseModel):
    disease_name: str
    disease_name_hi: Optional[str]
    confidence: float
    crop_name: str
    description: str
    description_hi: Optional[str]
    treatment: List[str]
    treatment_hi: Optional[List[str]]
    products_available: List[str]
    severity: str  # mild, moderate, severe
    prevention_tips: List[str]
