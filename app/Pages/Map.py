import pandas as pd
import plotly.express as px
import streamlit as st
from utils.data import load_weather_data

# Configuration de la page
st.set_page_config(
    page_title="Météo France",
    page_icon="🌦️",
    layout="wide",
)

# Titre
st.title("Carte des prévisions météorologiques")

st.markdown(
    """
    Explorez les prévisions météorologiques à travers la France.
    Les données sont issues de l'API Open-Meteo et sont présentées
    par période de la journée.
    """
)

# Chargement des données
df = load_weather_data()

if df.empty:
    st.error("Aucune donnée météorologique disponible.")
    st.stop()

# Normalisation des timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

# Heure locale française utilisée pour l'affichage
df["local_timestamp"] = (df["timestamp"].dt.tz_convert("Europe/Paris"))

# Création des créneaux météo
def get_forecast_slots(dataframe):

    available_local = dataframe["local_timestamp"]
    available_dates = sorted(available_local.dt.normalize().drop_duplicates().tolist())

    # Aujourd'hui en France
    today = pd.Timestamp.now(tz="Europe/Paris").normalize()
    slots = []

    for current_day in available_dates:

        # On ignore les journées trop anciennes
        if current_day < today:
            continue

        day_offset = (current_day.date() - today.date()).days

        # Maximum 8 jours : aujourd'hui + 7 jours
        if day_offset > 7:
            continue

        # Libellé du jour
        if day_offset == 0:
            day_label = "Aujourd'hui"

        elif day_offset == 1:
            day_label = "Demain"

        else:
            weekdays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            day_label = (f"{weekdays[current_day.dayofweek]} {current_day.strftime('%d/%m')}")

        # Créneaux affichés
        periods = [("Matin", 8), ("Après-midi", 14), ("Soir", 20)]

        for period_name, hour in periods:

            slot_local = (current_day + pd.Timedelta(hours=hour))

            # Vérifie que cette heure existe réellement dans les données
            available = (dataframe["local_timestamp"].dt.floor("h")== slot_local).any()

            if available:

                label = (f"{day_label} - {period_name}")
                slots.append({"label": label, "timestamp": slot_local,})

    return slots

forecast_slots = get_forecast_slots(df)

if not forecast_slots:
    st.warning(
        "Aucun créneau de prévision disponible."
    )
    st.stop()

# Filtres
col1, col2 = st.columns(2)

with col1:
    selected_label = st.selectbox(
        "Prévision",
        options=[
            slot["label"]
            for slot in forecast_slots
        ],
    )

with col2:
    variable = st.selectbox(
        "Variable",
        options=[
            "temperature",
            "precipitation",
            "wind_speed",
            "humidity",
            "cloud_cover",
        ],
        format_func=lambda value: {
            "temperature": "Température",
            "precipitation": "Précipitations",
            "wind_speed": "Vent",
            "humidity": "Humidité",
            "cloud_cover": "Couverture nuageuse",
        }[value],
    )

# Timestamp sélectionné
selected_timestamp_local = next(
    slot["timestamp"]
    for slot in forecast_slots
    if slot["label"] == selected_label
)

selected_timestamp_utc = (selected_timestamp_local.tz_convert("UTC"))

# Sélection de la ville
cities = sorted(df["city"].dropna().unique())
selected_city = st.selectbox(
    "Rechercher une ville", ["Toutes les villes"] + cities,
)

# Filtrage des données
map_data = df[df["timestamp"] == selected_timestamp_utc].copy()

if selected_city != "Toutes les villes":
    map_data = map_data[map_data["city"] == selected_city].copy()

if map_data.empty:
    st.warning("Aucune donnée disponible pour ce créneau.")
    st.stop()

# Informations sur la période sélectionnée
st.caption(f"Prévisions sélectionnées : **{selected_label}**")

# Météo d'une ville
if selected_city != "Toutes les villes":

    city_weather = map_data.iloc[0]
    st.subheader(f"Conditions prévues à {selected_city}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Température", f"{city_weather['temperature']:.1f} °C",)

    with col2:
        st.metric("Humidité", f"{city_weather['humidity']:.0f} %",)

    with col3:
        st.metric("Précipitations", f"{city_weather['precipitation']:.1f} mm",)

    with col4:
        st.metric("Vent", f"{city_weather['wind_speed']:.1f} km/h",)

# Labels des variables
variable_labels = {
    "temperature": "Température (°C)",
    "precipitation": "Précipitations (mm)",
    "wind_speed": "Vent (km/h)",
    "humidity": "Humidité (%)",
    "cloud_cover": "Couverture nuageuse (%)",
}

# Carte
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
        "humidity": ":.0f",
        "cloud_cover": ":.0f",
        "latitude": False,
        "longitude": False,
        "population": False,
    },
    center={"lat": 46.5, "lon": 2.5},
    zoom=5,
    height=700,
    labels={variable: variable_labels[variable]},
)

fig.update_layout(
    map_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

st.plotly_chart(fig, use_container_width=True)

# Informations complémentaires
if selected_city == "Toutes les villes":
    st.caption(f"{len(map_data):,} communes disponibles pour {selected_label}.")