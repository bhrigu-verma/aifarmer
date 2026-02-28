from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.services.mandi_service import get_today_prices, get_price_trend, get_sell_recommendation
from app.schemas.mandi import MandiPriceResponse, MandiPriceTrend, SellRecommendation

router = APIRouter()


@router.get("/prices", response_model=List[MandiPriceResponse])
def prices(
    crop_name: str = Query(...),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return get_today_prices(db, crop_name, state, district)


@router.get("/trend", response_model=MandiPriceTrend)
def trend(
    crop_name: str = Query(...),
    mandi_name: str = Query(...),
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
):
    return get_price_trend(db, crop_name, mandi_name, days)


@router.get("/sell-recommendation", response_model=SellRecommendation)
def sell_recommendation(
    crop_name: str = Query(...),
    mandi_name: str = Query(...),
    msp_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    return get_sell_recommendation(db, crop_name, mandi_name, msp_price)
