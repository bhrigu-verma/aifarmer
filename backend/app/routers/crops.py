from fastapi import APIRouter, Query
from typing import Optional, List

from app.services.crop_service import recommend_crops, get_input_recommendation
from app.schemas.crop import CropAdvisorResponse, InputRecommendation

router = APIRouter()


@router.get("/recommend", response_model=CropAdvisorResponse)
def recommend(
    soil_type: str = Query(...),
    season: Optional[str] = Query(None),
    land_size_acres: float = Query(1.0, gt=0),
):
    return recommend_crops(soil_type, season, land_size_acres)


@router.get("/inputs/{crop_name}", response_model=List[InputRecommendation])
def input_guide(crop_name: str):
    return get_input_recommendation(crop_name)
