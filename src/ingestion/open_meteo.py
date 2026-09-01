import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "precipitation_probability",
    "rain",
    "showers",
    "snowfall",
    "cloud_cover",
    "pressure_msl",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "uv_index",
    "weather_code",
]

def get_weather(
    latitudes: list[float],
    longitudes: list[float],
) -> list[dict]:

    params = {
        "latitude": ",".join(map(str, latitudes)),
        "longitude": ",".join(map(str, longitudes)),
        "hourly": ",".join(HOURLY_VARIABLES),
        "forecast_days": 7,
        "timezone": "Europe/Paris",
    }

    response = requests.get(BASE_URL, params=params, timeout=60)
    response.raise_for_status()

    return response.json()