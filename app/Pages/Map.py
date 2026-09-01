import pandas as pd
import plotly.express as px
import streamlit as st
from utils.data import load_weather_data

st.set_page_config(
    page_title="Météo France",
    page_icon="🌦️",
    layout="wide",
)
st.title("Carte des prévisions météorologiques")
st.markdown(
    """
    Explorez les prévisions météorologiques à travers la France en utilisant
    des données provenant de l'API Open-Meteo.
    """
)

df = load_weather_data()

# Filters
col1, col2 = st.columns(2)

with col1:
    timestamps = sorted(
        df["timestamp"].unique()
    )

    selected_timestamp = st.selectbox(
        "Forecast time",
        timestamps,
        format_func=lambda x: x.strftime(
            "%d/%m/%Y %H:%M"
        ),
    )

with col2:
    variable = st.selectbox(
        "Variable",
        [
            "temperature",
            "precipitation",
            "wind_speed",
            "humidity",
            "cloud_cover",
        ],
    )

cities = sorted(df["city"].unique())
selected_city = st.selectbox("Search for a city", ["All cities"] + cities)

# Filter data
map_data = df[df["timestamp"] == selected_timestamp].copy()

if selected_city != "All cities":
    map_data = map_data[map_data["city"] == selected_city]

if selected_city != "All cities":

    city_weather = map_data.iloc[0]
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🌡️ Temperature", f"{city_weather['temperature']:.1f} °C")
    col2.metric("💧 Humidity", f"{city_weather['humidity']:.0f} %")
    col3.metric("🌧️ Precipitation", f"{city_weather['precipitation']:.1f} mm")
    col4.metric("💨 Wind", f"{city_weather['wind_speed']:.1f} km/h")

# Labels
variable_labels = {
    "temperature": "Temperature (°C)",
    "precipitation": "Precipitation (mm)",
    "wind_speed": "Wind speed (km/h)",
    "humidity": "Humidity (%)",
    "cloud_cover": "Cloud cover (%)",
}

# Map
fig = px.scatter_map(
    map_data,
    lat="latitude",
    lon="longitude",
    color=variable,
    size="population",
    hover_name="city",
    hover_data={
        "temperature": ":.1f",
        "precipitation": ":.1f",
        "wind_speed": ":.1f",
        "humidity": True,
        "cloud_cover": True,
        "latitude": False,
        "longitude": False,
        "population": False,
    },
    zoom=5,
    height=700,
    labels={
        variable: variable_labels[variable],
    },
)

fig.update_layout(
    map_style="open-street-map",
    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0,
    },
)

st.plotly_chart(fig, use_container_width=True)