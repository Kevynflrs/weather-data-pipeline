import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(
    page_title="Météo France",
    page_icon="🌦️",
    layout="wide",
)

HISTORICAL_FORECAST_URL = ("https://historical-forecast-api.open-meteo.com/v1/forecast")
ARCHIVE_URL = ("https://archive-api.open-meteo.com/v1/archive")

@st.cache_data
def load_forecast_data():

    df = pd.read_parquet("data/processed/weather_history.parquet")
    df["forecast_run"] = pd.to_datetime(df["forecast_run"], utc=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df

forecast_data = load_forecast_data()

st.title("Carte des prévisions météorologiques")
st.markdown(
    """
    Explorez les prévisions météorologiques à travers la France.
    Les données sont issues de l'API Open-Meteo et sont présentées
    par période de la journée.
    """
)

city_names = sorted(forecast_data["city"].dropna().unique())
selected_city = st.selectbox("Ville", city_names)
city_forecast = forecast_data[forecast_data["city"] == selected_city].copy()
latitude = float(city_forecast["latitude"].iloc[0])
longitude = float(city_forecast["longitude"].iloc[0])
insee_code = str(city_forecast["insee_code"].iloc[0])

# Sélection période
st.subheader("Période analysée")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Début",
        value=pd.Timestamp.now()
        .normalize()
        - pd.Timedelta(days=7),
    )

with col2:
    end_date = st.date_input(
        "Fin",
        value=pd.Timestamp.now()
        .normalize()
        - pd.Timedelta(days=1),
    )

if start_date >= end_date:

    st.error("La date de début doit être antérieure à la date de fin.")
    st.stop()

# Récupération des prévisions historiques
@st.cache_data
def load_historical_forecast(latitude, longitude, start_date, end_date):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "timezone": "Europe/Paris",
    }

    response = requests.get(HISTORICAL_FORECAST_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data["hourly"])
    df = df.rename(
        columns={
            "time": "timestamp",
            "temperature_2m": "temperature_forecast",
            "relative_humidity_2m": "humidity_forecast",
            "precipitation": "precipitation_forecast",
            "wind_speed_10m": "wind_forecast",
        }
    )
    df["timestamp"] = (pd.to_datetime(df["timestamp"]).dt.tz_localize("Europe/Paris").dt.tz_convert("UTC"))

    return df

# Récupération référence historique
@st.cache_data
def load_reference(latitude, longitude, start_date, end_date):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "timezone": "Europe/Paris",
    }

    response = requests.get(ARCHIVE_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data["hourly"])
    df = df.rename(
        columns={
            "time": "timestamp",
            "temperature_2m": "temperature_reference",
            "relative_humidity_2m": "humidity_reference",
            "precipitation": "precipitation_reference",
            "wind_speed_10m": "wind_reference",
        }
    )
    df["timestamp"] = (pd.to_datetime(df["timestamp"]).dt.tz_localize("Europe/Paris").dt.tz_convert("UTC"))

    return df

# Chargement
try:

    forecast = load_historical_forecast(
        latitude,
        longitude,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )

    reference = load_reference(
        latitude,
        longitude,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )

except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")
    st.stop()

# Jointure
comparison = forecast.merge(
    reference,
    on="timestamp",
    how="inner",
)

if comparison.empty:
    st.warning("Aucune donnée commune trouvée pour cette période.")
    st.stop()

# Calcul des erreurs
comparison["temperature_error"] = (comparison["temperature_forecast"] - comparison["temperature_reference"])
comparison["absolute_error"] = (comparison["temperature_error"].abs())
comparison["squared_error"] = (comparison["temperature_error"] ** 2)

# Métriques
mae = (comparison["absolute_error"].mean())
rmse = (comparison["squared_error"].mean()** 0.5)
bias = (comparison["temperature_error"].mean())

# KPIs
st.subheader("Indicateurs de précision")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "MAE",
        f"{mae:.2f} °C",
    )

with col2:
    st.metric(
        "RMSE",
        f"{rmse:.2f} °C",
    )

with col3:
    st.metric(
        "Bias",
        f"{bias:+.2f} °C",
    )

# Explication des métriques
with st.expander(
    "Que signifient ces métriques ?",
    expanded=False,
):

    st.markdown(
        """
        **MAE : Mean Absolute Error**

        Le MAE représente l'erreur absolue moyenne entre la
        température prévue et la température de référence.

        Exemple : un MAE de **1,2 °C** signifie qu'en moyenne,
        la prévision s'écarte de 1,2 °C de la référence.

        **RMSE : Root Mean Squared Error**

        Le RMSE mesure également l'erreur moyenne, mais pénalise
        davantage les grosses erreurs.

        Plus le RMSE est élevé par rapport au MAE, plus certaines
        prévisions présentent de grosses erreurs.

        **Bias**

        Le Bias mesure l'erreur moyenne signée.

        Une valeur **positive** signifie que le modèle a tendance
        à surestimer la température.

        Une valeur **négative** signifie qu'il a tendance à
        sous-estimer la température.

        **Pour les trois métriques, plus la valeur est proche de
        zéro, meilleure est la précision.**
        """
    )

# Graphique température
st.subheader("Température prévue vs référence")
chart_df = comparison[["timestamp", "temperature_forecast", "temperature_reference"]].copy()
chart_df = chart_df.rename(columns={"timestamp": "Date", "temperature_forecast": "Prévision", "temperature_reference": "Référence"})

fig = px.line(
    chart_df,
    x="Date",
    y=["Prévision", "Référence"],
    labels={"value": "Température (°C)", "variable": "Type"},
)

fig.update_layout(height=500,)
st.plotly_chart(fig, use_container_width=True)

# Erreur au cours du temps
st.subheader("Erreur de prévision")

error_df = comparison[["timestamp", "temperature_error",]].copy()
error_df = error_df.rename(columns={"timestamp": "Date", "temperature_error": "Erreur",})

fig_error = px.line(
    error_df,
    x="Date",
    y="Erreur",
    labels={"Erreur": "Erreur (°C)",},
)
fig_error.add_hline(y=0, line_dash="dash")
fig_error.update_layout(height=350)

st.plotly_chart(fig_error, use_container_width=True)

# Résumé
st.subheader("Résumé")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Points comparés",
        f"{len(comparison):,}",
    )

with col2:
    st.metric(
        "Période",
        f"{start_date} à {end_date}",
    )

with col3:
    st.metric(
        "Ville",
        selected_city,
    )

# Données
with st.expander("Voir les données"):
    st.dataframe(comparison, use_container_width=True)