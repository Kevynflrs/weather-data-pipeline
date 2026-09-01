import pandas as pd
import streamlit as st
from utils.data import load_weather_data

st.set_page_config(
    page_title="Météo France",
    page_icon="🌦️",
    layout="wide",
)

st.title("Météo France")

df = load_weather_data()
latest_data = df.tail(1)

# KPIs
average_temperature = (latest_data["temperature"].mean())
max_temperature = (latest_data["temperature"].max())
min_temperature = (latest_data["temperature"].min())
total_precipitation = (latest_data["precipitation"].sum())

# Visualize KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("🌡️ Average temperature", f"{average_temperature:.1f} °C")
col2.metric("🔥 Maximum temperature", f"{max_temperature:.1f} °C")
col3.metric("❄️ Minimum temperature", f"{min_temperature:.1f} °C")
col4.metric("🌧️ Precipitation", f"{total_precipitation:.1f} mm")

st.divider()

st.subheader("Données disponibles")
st.write(f"Communes suivies : **{df['city'].nunique()}**")
st.write(f"Observations : **{len(df):,}**")
st.write(f"Début des prévisions : **{df['timestamp'].min()}**")
st.write(f"Fin des prévisions : **{df['timestamp'].max()}**")