import pandas as pd

from src.transformation.accuracy import (
    compare_forecast_with_reference,
    calculate_accuracy_metrics,
)


# --------------------------------------------------
# 1. Charger les prévisions
# --------------------------------------------------

forecast_file = "data/processed/weather_history.parquet"

forecast = pd.read_parquet(forecast_file)

forecast["forecast_run"] = pd.to_datetime(
    forecast["forecast_run"]
)

forecast["timestamp"] = pd.to_datetime(
    forecast["timestamp"]
)


print("Prévisions chargées :", len(forecast))
print()


# --------------------------------------------------
# 2. Créer une référence temporaire
# --------------------------------------------------
#
# Pour le moment, on utilise une copie des données
# de prévision afin de tester la logique de comparaison.
#
# Ce n'est PAS encore une vraie référence météo.
#

reference = forecast[
    [
        "insee_code",
        "city",
        "latitude",
        "longitude",
        "timestamp",
        "temperature",
        "humidity",
        "precipitation",
        "wind_speed",
        "weather_code",
    ]
].copy()


# --------------------------------------------------
# 3. Comparer prévisions et référence
# --------------------------------------------------

comparison = compare_forecast_with_reference(
    forecast,
    reference,
)


print("Comparaison créée :", len(comparison))
print()


# --------------------------------------------------
# 4. Afficher quelques résultats
# --------------------------------------------------

print(
    comparison[
        [
            "forecast_run",
            "city",
            "timestamp",
            "forecast_horizon_hours",
            "temperature_forecast",
            "temperature_reference",
            "temperature_error",
        ]
    ].head(10)
)

print()


# --------------------------------------------------
# 5. Calculer les métriques
# --------------------------------------------------

metrics = calculate_accuracy_metrics(
    comparison
)


print("Métriques :")
print(
    f"MAE  : {metrics['mae']:.2f} °C"
)

print(
    f"RMSE : {metrics['rmse']:.2f} °C"
)

print(
    f"Bias : {metrics['bias']:.2f} °C"
)

print()
print("Horizons de prévision :")
print(
    comparison["forecast_horizon_hours"]
    .describe()
)