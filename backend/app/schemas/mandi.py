from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class MandiPriceResponse(BaseModel):
    crop_name: str
    mandi_name: str
    state: str
    district: str
    min_price: Optional[float]
    max_price: Optional[float]
    modal_price: float
    price_unit: str
    price_date: date

    class Config:
        from_attributes = True


class MandiPriceTrend(BaseModel):
    crop_name: str
    mandi_name: str
    prices: List[MandiPriceResponse]
    trend: str  # rising, falling, stable
    recommendation: str
    recommendation_hi: str


class SellRecommendation(BaseModel):
    crop_name: str
    current_price: float
    avg_price_30d: float
    msp_price: Optional[float]
    recommendation: str  # sell_now, wait, hold
    reasoning: str
    reasoning_hi: str
