from pathlib import Path
import pandas as pd
from src.ingestion.communes import get_french_communes
from src.ingestion.open_meteo import get_weather
from src.validation.weather import validate_weather_data
from src.transformation.weather import transform_weather_data
from datetime import datetime, timezone

COMMUNES_FILE = Path("data/raw/communes.parquet")
WEATHER_FILE = Path("data/raw/weather.parquet")
PROCESSED_WEATHER_DIR = Path("data/processed/weather")
NUMBER_OF_CITIES = 100

def main() -> None:

    forecast_run = datetime.now(timezone.utc)

    communes = get_french_communes()
    COMMUNES_FILE.parent.mkdir(parents=True, exist_ok=True)
    communes.to_parquet(COMMUNES_FILE, index=False)
    print(f"Retrieved {len(communes)} communes.")

    cities = (
        communes
        .dropna(subset=["population"])
        .sort_values(
            "population",
            ascending=False,
        )
        .head(NUMBER_OF_CITIES)
        .reset_index(drop=True)
    )

    print(f"Selected {len(cities)} cities.")

    weather_data = get_weather(latitudes=cities["latitude"].tolist(), longitudes=cities["longitude"].tolist())

    rows = []
    for city, weather in zip(cities.to_dict("records"), weather_data):

        hourly = weather["hourly"]
        for i in range(len(hourly["time"])):

            rows.append(
                {
                    "forecast_run": forecast_run,
                    "insee_code": city["insee_code"],
                    "city": city["city"],
                    "latitude": city["latitude"],
                    "longitude": city["longitude"],
                    "population": city["population"],
                    "department_code": city["department_code"],
                    "region_code": city["region_code"],
                    "timestamp": hourly["time"][i],
                    "temperature": hourly["temperature_2m"][i],
                    "humidity": hourly["relative_humidity_2m"][i],
                    "apparent_temperature": hourly["apparent_temperature"][i],
                    "precipitation": hourly["precipitation"][i],
                    "precipitation_probability": hourly["precipitation_probability"][i],
                    "rain": hourly["rain"][i],
                    "showers": hourly["showers"][i],
                    "snowfall": hourly["snowfall"][i],
                    "cloud_cover": hourly["cloud_cover"][i],
                    "pressure": hourly["pressure_msl"][i],
                    "wind_speed": hourly["wind_speed_10m"][i],
                    "wind_direction": hourly["wind_direction_10m"][i],
                    "wind_gusts": hourly["wind_gusts_10m"][i],
                    "uv_index": hourly["uv_index"][i],
                    "weather_code": hourly["weather_code"][i],
                }
            )

    df = pd.DataFrame(rows)
    validate_weather_data(df)
    WEATHER_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(WEATHER_FILE, index=False)
    print(f"Saved raw data to {WEATHER_FILE}")

    df = transform_weather_data(df)

    PROCESSED_WEATHER_DIR.mkdir(parents=True, exist_ok=True)
    run_filename = (forecast_run.strftime("%Y-%m-%d_%H%M") + ".parquet")
    processed_file = (PROCESSED_WEATHER_DIR / run_filename)
    df.to_parquet(processed_file, index=False)

    print(f"Saved processed data to {processed_file}")

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

if __name__ == "__main__":
    main()