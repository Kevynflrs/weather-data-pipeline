import pandas as pd

def compare_forecast_with_reference(forecast: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:

    forecast = forecast.copy()
    reference = reference.copy()
    forecast["timestamp"] = pd.to_datetime(forecast["timestamp"], utc=True)
    forecast["forecast_run"] = pd.to_datetime(forecast["forecast_run"], utc=True)
    reference["timestamp"] = pd.to_datetime(reference["timestamp"], utc=True)

    merged = forecast.merge(
        reference,
        on=[
            "insee_code",
            "city",
            "timestamp",
        ],
        suffixes=(
            "_forecast",
            "_reference",
        ),
        how="inner",
    )

    merged["forecast_horizon_hours"] = ((merged["timestamp"] - merged["forecast_run"]).dt.total_seconds() / 3600)
    merged = merged[merged["forecast_horizon_hours"] >= 0].copy()

    # Calcul de l'erreur de température
    merged["temperature_error"] = (merged["temperature_forecast"] - merged["temperature_reference"])
    merged["absolute_error"] = (merged["temperature_error"].abs())
    merged["squared_error"] = (merged["temperature_error"] ** 2)

    return merged

def calculate_accuracy_metrics(comparison: pd.DataFrame) -> dict:

    mae = comparison["absolute_error"].mean()
    rmse = (comparison["squared_error"].mean() ** 0.5)
    bias = comparison["temperature_error"].mean()

    return {"mae": mae, "rmse": rmse, "bias": bias}