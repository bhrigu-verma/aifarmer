from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.weather_service import generate_weather_alerts
from app.schemas.weather import WeatherDay, WeatherForecast


def _make_forecast(days):
    return WeatherForecast(
        latitude=22.7,
        longitude=75.8,
        location="22.7,75.8",
        forecast=days,
    )


MOCK_API_RESPONSE = {
    "daily": {
        "time": ["2026-03-01", "2026-03-02"],
        "temperature_2m_max": [32.0, 35.0],
        "temperature_2m_min": [18.0, 20.0],
        "precipitation_sum": [0.0, 5.0],
        "weathercode": [0, 3],
    }
}


def test_weather_forecast_endpoint(client):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("app.services.weather_service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        mock_cls.return_value.__aexit__.return_value = False

        response = client.get(
            "/api/v1/weather/forecast?latitude=22.7&longitude=75.8&days=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["latitude"] == 22.7
        assert len(data["forecast"]) == 2
        assert data["forecast"][0]["temperature_max"] == 32.0
        assert data["forecast"][0]["weather_description"] == "Clear sky"


def test_weather_alerts_endpoint(client):
    frost_response = {
        "daily": {
            "time": ["2026-03-01"],
            "temperature_2m_max": [10.0],
            "temperature_2m_min": [2.0],
            "precipitation_sum": [0.0],
            "weathercode": [0],
        }
    }
    mock_response = MagicMock()
    mock_response.json.return_value = frost_response
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("app.services.weather_service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        mock_cls.return_value.__aexit__.return_value = False

        response = client.get(
            "/api/v1/weather/alerts?latitude=22.7&longitude=75.8&crop=potato"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["alert_type"] == "frost"
        assert data[0]["crop_affected"] == "potato"


def test_generate_frost_alert():
    forecast = _make_forecast([
        WeatherDay(date="2026-01-15", temperature_max=12.0, temperature_min=2.0,
                   precipitation_mm=0.0, weather_description="Clear sky"),
    ])
    alerts = generate_weather_alerts(forecast, "potato")
    assert len(alerts) == 1
    assert alerts[0].alert_type == "frost"
    assert alerts[0].severity == "high"
    assert alerts[0].crop_affected == "potato"
    assert "पाला" in alerts[0].message_hi


def test_generate_heavy_rain_alert():
    forecast = _make_forecast([
        WeatherDay(date="2026-07-20", temperature_max=30.0, temperature_min=24.0,
                   precipitation_mm=80.0, weather_description="Heavy rain"),
    ])
    alerts = generate_weather_alerts(forecast)
    assert len(alerts) == 1
    assert alerts[0].alert_type == "heavy_rain"


def test_generate_heat_wave_alert():
    forecast = _make_forecast([
        WeatherDay(date="2026-05-15", temperature_max=45.0, temperature_min=30.0,
                   precipitation_mm=0.0, weather_description="Clear sky"),
    ])
    alerts = generate_weather_alerts(forecast, "wheat")
    assert len(alerts) == 1
    assert alerts[0].alert_type == "heat_wave"
    assert alerts[0].crop_affected == "wheat"


def test_no_alerts_for_normal_weather():
    forecast = _make_forecast([
        WeatherDay(date="2026-03-01", temperature_max=30.0, temperature_min=18.0,
                   precipitation_mm=5.0, weather_description="Partly cloudy"),
    ])
    alerts = generate_weather_alerts(forecast)
    assert len(alerts) == 0
