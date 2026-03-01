from fastapi import APIRouter, Query
from typing import List

from app.services.crop_service import get_input_recommendation
from app.schemas.crop import InputRecommendation

router = APIRouter()


@router.get("/{crop_name}", response_model=List[InputRecommendation])
def get_inputs(crop_name: str):
    return get_input_recommendation(crop_name)
