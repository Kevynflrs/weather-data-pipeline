import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = "data/processed/weather.parquet"

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_parquet(DATA_FILE)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    return df

st.set_page_config(
    page_title="France Map",
    page_icon="🗺️",
    layout="wide",
)
st.title("🗺️ France Météo Map")

df = load_data()

# Filters
col1, col2 = st.columns(2)

with col1:
    timestamps = sorted(
        df["timestamp"].unique()
    )

    selected_timestamp = st.selectbox(
        "🕐 Forecast time",
        timestamps,
        format_func=lambda x: x.strftime(
            "%d/%m/%Y %H:%M"
        ),
    )

with col2:
    variable = st.selectbox(
        "📊 Variable",
        [
            "temperature",
            "precipitation",
            "wind_speed",
            "humidity",
            "cloud_cover",
        ],
    )

# Filter data
map_data = df[df["timestamp"] == selected_timestamp].copy()

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