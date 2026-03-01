from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from app.services.pest_service import detect_disease, get_disease_info, list_known_diseases
from app.schemas.pest import PestDetectionResult

router = APIRouter()


@router.post("/detect", response_model=PestDetectionResult)
async def detect(image: UploadFile = File(...)):
    if image.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are supported")
    return detect_disease()


@router.get("/diseases", response_model=List[str])
def diseases():
    return list_known_diseases()


@router.get("/diseases/{disease_key}", response_model=PestDetectionResult)
def disease_info(disease_key: str):
    result = get_disease_info(disease_key)
    if not result:
        raise HTTPException(status_code=404, detail="Disease not found")
    return result
