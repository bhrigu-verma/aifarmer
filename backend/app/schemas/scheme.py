from pydantic import BaseModel
from typing import List, Optional


class GovernmentScheme(BaseModel):
    scheme_name: str
    scheme_name_hi: str
    description: str
    description_hi: str
    eligibility: List[str]
    eligibility_hi: List[str]
    benefits: str
    benefits_hi: str
    how_to_apply: List[str]
    how_to_apply_hi: List[str]
    website: Optional[str] = None
    helpline: Optional[str] = None
    is_eligible: bool = True


class SchemeResponse(BaseModel):
    farmer_name: str
    state: str
    total_schemes: int
    schemes: List[GovernmentScheme]
