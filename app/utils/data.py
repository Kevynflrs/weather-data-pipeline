from pathlib import Path
import pandas as pd
import streamlit as st

DATA_FILE = Path("data/processed/weather.parquet")

@st.cache_data
def load_weather_data() -> pd.DataFrame:

    df = pd.read_parquet(DATA_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df