import pandas as pd
import plotly.express as px
import streamlit as st
from utils.data import load_weather_data

st.set_page_config(
    page_title="Météo France",
    page_icon="🌦️",
    layout="wide",
)
st.title("Prévisions météorologiques par ville")
st.markdown(
    """
    Explorez les prévisions météorologiques à travers la France en utilisant
    des données provenant de l'API Open-Meteo.
    """
)

df = load_weather_data()

# City selection
cities = sorted(df["city"].unique())
selected_city = st.selectbox("Select a city", cities)
city_data = df[df["city"] == selected_city].copy()

# Date selection
available_dates = sorted(city_data["timestamp"].dt.date.unique())
selected_date = st.selectbox("Select a date", available_dates)
day_data = city_data[city_data["timestamp"].dt.date == selected_date].copy()

# Summary
col1, col2, col3 = st.columns(3)

col1.metric("Minimum", f"{day_data['temperature'].min():.1f} °C")
col2.metric("Maximum", f"{day_data['temperature'].max():.1f} °C")
col3.metric("Rain",  f"{day_data['precipitation'].sum():.1f} mm")

st.divider()

# Temperature
fig = px.line(
    day_data,
    x="timestamp",
    y="temperature",
    markers=True,
    title=(f"Temperature : {selected_city}"),
    labels={
        "temperature": "Temperature (°C)",
        "timestamp": "Time",
    },
)

st.plotly_chart(fig, use_container_width=True)

# Weather table
st.subheader("Météo détaillée")

display_columns = [
    "timestamp",
    "temperature",
    "apparent_temperature",
    "precipitation",
    "humidity",
    "wind_speed",
    "cloud_cover",
]

st.dataframe(day_data[display_columns], use_container_width=True, hide_index=True)