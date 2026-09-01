import pandas as pd

REQUIRED_COLUMNS = [
    "insee_code",
    "city",
    "latitude",
    "longitude",
    "timestamp",
    "temperature",
    "humidity",
    "precipitation",
    "wind_speed",
    "weather_code",
]

def validate_weather_data(df: pd.DataFrame) -> None:
    # Required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    # Empty dataset
    if df.empty:
        raise ValueError("Weather dataset is empty.")

    # Missing values
    critical_columns = [
        "insee_code",
        "city",
        "latitude",
        "longitude",
        "timestamp",
    ]

    missing_values = df[critical_columns].isna().sum()

    if missing_values.any():
        raise ValueError(f"Missing critical values:\n{missing_values}")

    # Coordinates
    if not df["latitude"].between(-90, 90).all():
        raise ValueError("Invalid latitude detected.")

    if not df["longitude"].between(-180, 180).all():
        raise ValueError("Invalid longitude detected.")

    # Temperature
    if not df["temperature"].between(-50, 60).all():
        raise ValueError("Unrealistic temperature detected.")

    # Humidity
    if not df["humidity"].between(0, 100).all():
        raise ValueError("Invalid humidity detected.")

    # Precipitation
    if (df["precipitation"] < 0).any():
        raise ValueError("Negative precipitation detected.")

    # Duplicates
    duplicates = df.duplicated(subset=["insee_code", "timestamp"])

    if duplicates.any():
        raise ValueError(f"{duplicates.sum()} duplicate weather records detected.")

    print("Weather data validation passed.")