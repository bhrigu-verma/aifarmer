from pydantic import BaseModel
from typing import List, Optional


class WeatherDay(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    precipitation_mm: float
    humidity: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    weather_description: str


class WeatherForecast(BaseModel):
    latitude: float
    longitude: float
    location: str
    forecast: List[WeatherDay]


class WeatherAlert(BaseModel):
    alert_type: str
    severity: str
    message: str
    message_hi: str
    recommended_action: str
    recommended_action_hi: str
    crop_affected: Optional[str] = None
