from pathlib import Path
import pandas as pd
import streamlit as st

HISTORY_FILE = Path("data/processed/weather_history.parquet")

@st.cache_data
def load_weather_data() -> pd.DataFrame:

    if not HISTORY_FILE.exists():

        raise FileNotFoundError("Historical weather dataset not found.")
    
    df = pd.read_parquet(HISTORY_FILE)
    df["forecast_run"] = pd.to_datetime(df["forecast_run"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df