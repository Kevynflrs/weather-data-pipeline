import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.transformation.accuracy import compare_forecast_with_reference, calculate_accuracy_metrics
from src.ingestion.observations import fetch_historical_weather

st.set_page_config(
    page_title="Météo France",
    page_icon="🌦️",
    layout="wide",
)

# Chargement des données
@st.cache_data
def load_forecast():

    df = pd.read_parquet("data/processed/weather_history.parquet")
    df["forecast_run"] = pd.to_datetime(df["forecast_run"], utc=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df
forecast = load_forecast()

# Interface
st.title("Comparaison des prévisions avec la référence historique")
st.markdown(
    """
    Cette page compare les prévisions météorologiques
    avec une référence historique indépendante.
    """
)

# Sélection ville
cities = sorted(forecast["city"].dropna().unique())
selected_city = st.selectbox("Ville", cities)
city_forecast = forecast[forecast["city"] == selected_city].copy()

# Coordonnées
latitude = city_forecast["latitude"].iloc[0]
longitude = city_forecast["longitude"].iloc[0]
insee_code = city_forecast["insee_code"].iloc[0]

# Période disponible
now = pd.Timestamp.now(tz="UTC")
past_forecast = city_forecast[city_forecast["timestamp"] <= now].copy()

if past_forecast.empty:

    st.warning("Aucune prévision passée disponible pour cette ville.")
    st.stop()

start_date = (past_forecast["timestamp"].min().strftime("%Y-%m-%d"))
end_date = (past_forecast["timestamp"].max().strftime("%Y-%m-%d"))

# Référence historique
with st.spinner(
    "Chargement des données historiques..."
):

    reference = fetch_historical_weather(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        insee_code=insee_code,
        city=selected_city,
    )

# Comparaison
comparison = compare_forecast_with_reference(city_forecast, reference)

if comparison.empty:

    st.warning("Impossible de construire une comparaison pour cette période.")
    st.stop()

# Métriques
metrics = calculate_accuracy_metrics(comparison)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "MAE",
        f"{metrics['mae']:.2f} °C",
    )

with col2:
    st.metric(
        "RMSE",
        f"{metrics['rmse']:.2f} °C",
    )

with col3:
    st.metric(
        "Bias",
        f"{metrics['bias']:.2f} °C",
    )

st.divider()

# Graphique prévision vs référence
st.subheader("Prévision vs référence")

chart_data = comparison[
    [
        "timestamp",
        "temperature_forecast",
        "temperature_reference",
    ]
].copy()

chart_data = chart_data.rename(
    columns={
        "timestamp": "Timestamp",
        "temperature_forecast": "Prévision",
        "temperature_reference": "Référence",
    }
)

fig = px.line(
    chart_data,
    x="Timestamp",
    y=["Prévision", "Référence"],
    labels={
        "value": "Température (°C)",
        "Timestamp": "Date",
        "variable": "Type",
    },
)

st.plotly_chart(fig, use_container_width=True)

# Erreur selon l'horizon
st.subheader("Erreur selon l'horizon de prévision")

comparison["horizon_days"] = (comparison["forecast_horizon_hours"] / 24)
comparison["horizon_bucket"] = pd.cut(
    comparison["horizon_days"],
    bins=[0, 1, 2, 3, 5, 8,],
    labels=["0–24h", "24–48h", "48–72h", "72h–5j", "5j+"],
)

accuracy_by_horizon = (
    comparison
    .groupby(
        "horizon_bucket",
        observed=True,
    )["absolute_error"]
    .mean()
    .reset_index()
)

accuracy_by_horizon.columns = ["Horizon", "MAE"]

fig_horizon = px.bar(
    accuracy_by_horizon,
    x="Horizon",
    y="MAE",
    labels={
        "MAE": "Erreur absolue moyenne (°C)",
        "Horizon": "Horizon",
    },
)

st.plotly_chart(fig_horizon, use_container_width=True)

# Données
with st.expander("Voir les données de comparaison"):

    st.dataframe(comparison, use_container_width=True)