import httpx
from typing import List, Optional

from app.config import settings
from app.schemas.weather import WeatherDay, WeatherForecast, WeatherAlert


def _classify_weather(code: int) -> str:
    mapping = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }
    return mapping.get(code, "Unknown")


async def get_weather_forecast(
    latitude: float, longitude: float, days: int = 10
) -> WeatherForecast:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "Asia/Kolkata",
        "forecast_days": min(days, 16),
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(settings.imd_api_url, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    forecast_days: List[WeatherDay] = []
    dates = daily.get("time", [])
    for i, d in enumerate(dates):
        forecast_days.append(
            WeatherDay(
                date=d,
                temperature_max=daily["temperature_2m_max"][i],
                temperature_min=daily["temperature_2m_min"][i],
                precipitation_mm=daily["precipitation_sum"][i],
                weather_description=_classify_weather(daily["weathercode"][i]),
            )
        )

    return WeatherForecast(
        latitude=latitude,
        longitude=longitude,
        location=f"{latitude},{longitude}",
        forecast=forecast_days,
    )


def generate_weather_alerts(
    forecast: WeatherForecast, crop_name: Optional[str] = None
) -> List[WeatherAlert]:
    alerts: List[WeatherAlert] = []
    for day in forecast.forecast:
        if day.temperature_min < 4:
            alerts.append(
                WeatherAlert(
                    alert_type="frost",
                    severity="high",
                    message=f"Frost warning on {day.date}: min temp {day.temperature_min}°C",
                    message_hi=f"पाला चेतावनी {day.date}: न्यूनतम तापमान {day.temperature_min}°C",
                    recommended_action="Cover crops with mulch or plastic sheets tonight",
                    recommended_action_hi="आज रात फसल को मल्च या प्लास्टिक शीट से ढकें",
                    crop_affected=crop_name,
                )
            )
        if day.precipitation_mm > 50:
            alerts.append(
                WeatherAlert(
                    alert_type="heavy_rain",
                    severity="high",
                    message=f"Heavy rain expected on {day.date}: {day.precipitation_mm}mm",
                    message_hi=f"भारी बारिश की संभावना {day.date}: {day.precipitation_mm}mm",
                    recommended_action="Ensure drainage channels are clear. Delay fertiliser application.",
                    recommended_action_hi="जल निकासी नालियाँ साफ रखें। उर्वरक डालना टालें।",
                    crop_affected=crop_name,
                )
            )
        if day.temperature_max > 42:
            alerts.append(
                WeatherAlert(
                    alert_type="heat_wave",
                    severity="high",
                    message=f"Heat wave on {day.date}: max temp {day.temperature_max}°C",
                    message_hi=f"लू चेतावनी {day.date}: अधिकतम तापमान {day.temperature_max}°C",
                    recommended_action="Increase irrigation frequency. Apply mulch to retain moisture.",
                    recommended_action_hi="सिंचाई बढ़ाएं। नमी बनाए रखने के लिए मल्च लगाएं।",
                    crop_affected=crop_name,
                )
            )
    return alerts
