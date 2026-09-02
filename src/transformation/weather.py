import pandas as pd

def transform_weather_data(df: pd.DataFrame) -> pd.DataFrame:

    result = df.copy()
    result["forecast_run"] = pd.to_datetime(result["forecast_run"], utc=True)

    # Timestamp
    result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True)

    # Date information
    result["date"] = (result["timestamp"].dt.date)
    result["hour"] = (result["timestamp"].dt.hour)
    result["day_of_week"] = (result["timestamp"].dt.day_name())

    # Temperature categories
    result["temperature_category"] = pd.cut(
        result["temperature"],
        bins=[
            -float("inf"),
            0,
            10,
            20,
            30,
            float("inf"),
        ],
        labels=[
            "Freezing",
            "Cold",
            "Mild",
            "Warm",
            "Hot",
        ],
    )

    # Wind category
    result["wind_category"] = pd.cut(
        result["wind_speed"],
        bins=[
            -float("inf"),
            10,
            30,
            50,
            float("inf"),
        ],
        labels=[
            "Low",
            "Moderate",
            "Strong",
            "Very strong",
        ],
    )

    # Rain flag
    result["is_raining"] = (result["precipitation"] > 0)

    # Sort
    result = result.sort_values(["insee_code", "timestamp"])

    result["forecast_horizon_hours"] = ((result["timestamp"] - result["forecast_run"]).dt.total_seconds() / 3600)
    result["forecast_horizon_days"] = (result["forecast_horizon_hours"] / 24)

    return result