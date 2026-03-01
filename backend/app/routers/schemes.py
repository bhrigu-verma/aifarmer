from fastapi import APIRouter, Query
from typing import Optional

from app.services.scheme_service import get_eligible_schemes
from app.schemas.scheme import SchemeResponse

router = APIRouter()


@router.get("/", response_model=SchemeResponse)
def schemes(
    state: str = Query(...),
    land_size_acres: float = Query(1.0, gt=0),
    farmer_name: Optional[str] = Query(""),
):
    return get_eligible_schemes(state, land_size_acres, farmer_name or "")
