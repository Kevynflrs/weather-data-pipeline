import streamlit as st

def display_weather_metrics(temperature: float, humidity: float, precipitation: float, wind_speed: float) -> None:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🌡️ Temperature", f"{temperature:.1f} °C")
    col2.metric("💧 Humidity", f"{humidity:.0f} %")
    col3.metric("🌧️ Precipitation", f"{precipitation:.1f} mm")
    col4.metric("💨 Wind", f"{wind_speed:.1f} km/h")