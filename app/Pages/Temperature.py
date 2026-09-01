import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = "data/processed/weather.parquet"

@st.cache_data
def load_data() -> pd.DataFrame:

    df = pd.read_parquet(DATA_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df

st.set_page_config(
    page_title="Météo France",
    page_icon="🌦️",
    layout="wide",
)

st.title("Température par ville")
st.markdown(
    """
    Explorez les prévisions météorologiques à travers la France en utilisant
    des données provenant de l'API Open-Meteo.
    """
)

df = load_data()


# City
cities = sorted(df["city"].unique())
selected_city = st.selectbox("Select a city", cities)
city_data = df[df["city"] == selected_city].copy()

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Minimum", f"{city_data['temperature'].min():.1f} °C")
col2.metric("Maximum", f"{city_data['temperature'].max():.1f} °C")
col3.metric("Average", f"{city_data['temperature'].mean():.1f} °C")

st.divider()

# Chart
fig = px.line(
    city_data,
    x="timestamp",
    y=["temperature", "apparent_temperature"],
    markers=True,
    labels={
        "value": "Temperature (°C)",
        "timestamp": "Date",
        "variable": "Measure",
    },
    title=(f"Temperature à : " f"{selected_city}"),
)

st.plotly_chart(fig, use_container_width=True)