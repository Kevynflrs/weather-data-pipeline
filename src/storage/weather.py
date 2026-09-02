from pathlib import Path
import pandas as pd

HISTORY_FILE = Path("data/processed/weather_history.parquet")

def append_to_history(new_data: pd.DataFrame) -> pd.DataFrame:

    if HISTORY_FILE.exists():

        history = pd.read_parquet(HISTORY_FILE)
        history["forecast_run"] = pd.to_datetime(history["forecast_run"])
        history["timestamp"] = pd.to_datetime(history["timestamp"])

        df = pd.concat([history, new_data], ignore_index=True)

    else:

        df = new_data.copy()

    # Remove duplicates
    df = df.drop_duplicates(subset=["forecast_run", "insee_code", "timestamp"])

    # Sort
    df = df.sort_values(["forecast_run", "insee_code", "timestamp"])

    # Save
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(HISTORY_FILE, index=False)

    return df