import requests
import pandas as pd

BASE_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"

def fetch_historical_weather(latitude: float, longitude: float, start_date: str, end_date: str, insee_code: str, city: str) -> pd.DataFrame:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "timezone": "Europe/Paris",
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data["hourly"])

    df = df.rename(
        columns={
            "time": "timestamp",
            "temperature_2m": "temperature",
            "relative_humidity_2m": "humidity",
            "wind_speed_10m": "wind_speed",
            "weather_code": "weather_code",
        }
    )

    df["timestamp"] = (
        pd.to_datetime(df["timestamp"])
        .dt.tz_localize("Europe/Paris")
        .dt.tz_convert("UTC")
    )
    df["insee_code"] = insee_code
    df["city"] = city
    df["latitude"] = latitude
    df["longitude"] = longitude

    return df