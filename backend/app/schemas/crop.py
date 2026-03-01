from pydantic import BaseModel
from typing import List, Optional


class CropRecommendation(BaseModel):
    crop_name: str
    crop_name_hi: Optional[str]
    season: str
    expected_yield_per_acre: float
    expected_cost_per_acre: float
    expected_revenue_per_acre: float
    expected_profit_per_acre: float
    risk_level: str  # low, medium, high
    risk_explanation: str
    risk_explanation_hi: str
    suitability_score: float  # 0-100


class CropAdvisorResponse(BaseModel):
    farmer_state: str
    farmer_district: str
    soil_type: str
    season: str
    recommendations: List[CropRecommendation]


class InputRecommendation(BaseModel):
    crop_name: str
    stage_name: str
    fertiliser_type: Optional[str]
    fertiliser_quantity_kg_per_acre: Optional[float]
    water_frequency_days: Optional[int]
    water_quantity_litres_per_acre: Optional[float]
    pesticide_name: Optional[str]
    pesticide_quantity_ml_per_acre: Optional[float]
    care_instructions: str
    care_instructions_hi: Optional[str]
    estimated_cost: float
