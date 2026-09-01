from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path("data/processed/weather")

@st.cache_data
def load_weather_data() -> pd.DataFrame:

    files = sorted(DATA_DIR.glob("*.parquet"))

    if not files:
        raise FileNotFoundError("No processed weather data found.")

    dataframes = [
        pd.read_parquet(file)
        for file in files
    ]
    df = pd.concat(dataframes, ignore_index=True)
    df["forecast_run"] = pd.to_datetime(df["forecast_run"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df