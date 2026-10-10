import os
import httpx
from datetime import date
from app.model import WeatherResponseModel
from app.services.cache import get_cache, set_cache


async def fetch_weather(
    destination: str,
    start_date: date,
    end_date: date,
) -> list[WeatherResponseModel]:

    cache_key = f"weather_{destination}_{start_date}_{end_date}"
    cached_data = get_cache(cache_key)

    if cached_data is not None:
        return cached_data

    api_key = os.getenv("WEATHER_API_KEY") or os.getenv("WEATHERAPI_KEY")

    if not api_key:
        raise RuntimeError(
            "WEATHER_API_KEY (or WEATHERAPI_KEY) is not configured"
        )

    today = date.today()

    if start_date < today:
        raise ValueError("Historical dates require a supported history endpoint")

    days = (end_date - today).days + 1

    if days < 1 or days > 14:
        raise ValueError(
            "Requested forecast range is outside the supported limit"
        )

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            "https://api.weatherapi.com/v1/forecast.json",
            params={
                "key": api_key,
                "q": destination,
                "days": days,
            },
        )

        response.raise_for_status()
        data = response.json()

    forecasts = []

    for day in data["forecast"]["forecastday"]:
        forecast_date = date.fromisoformat(day["date"])

        if start_date <= forecast_date <= end_date:
            forecasts.append(
                WeatherResponseModel(
                    date=forecast_date.isoformat(),
                    condition=day["day"]["condition"]["text"],
                    temperature_high=day["day"]["maxtemp_c"],
                    temperature_low=day["day"]["mintemp_c"],
                    humidity=day["day"]["avghumidity"],
                    rain_chance=day["day"]["daily_chance_of_rain"],
                )
            )

    set_cache(cache_key, forecasts, ttl=3600)
    return forecasts
