from pathlib import Path
import pandas as pd
import requests

BASE_URL = "https://geo.api.gouv.fr/communes"
OUTPUT_FILE = Path("data/raw/communes.parquet")

def get_french_communes() -> pd.DataFrame:
    params = {
        "fields": "nom,code,population,centre,codeDepartement,codeRegion",
        "format": "json",
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    communes = response.json()
    rows = []

    for commune in communes:
        centre = commune.get("centre")

        if not centre:
            continue

        longitude, latitude = centre["coordinates"]
        rows.append(
            {
                "insee_code": commune["code"],
                "city": commune["nom"],
                "latitude": latitude,
                "longitude": longitude,
                "population": commune.get("population"),
                "department_code": commune.get("codeDepartement"),
                "region_code": commune.get("codeRegion"),
            }
        )

    return pd.DataFrame(rows)