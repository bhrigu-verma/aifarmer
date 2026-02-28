from fastapi import APIRouter, Query
from typing import List, Optional

from app.services.weather_service import get_weather_forecast, generate_weather_alerts
from app.schemas.weather import WeatherForecast, WeatherAlert

router = APIRouter()


@router.get("/forecast", response_model=WeatherForecast)
async def forecast(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(10, ge=1, le=16),
):
    return await get_weather_forecast(latitude, longitude, days)


@router.get("/alerts", response_model=List[WeatherAlert])
async def alerts(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    crop: Optional[str] = Query(None),
):
    forecast_data = await get_weather_forecast(latitude, longitude, 10)
    return generate_weather_alerts(forecast_data, crop)
