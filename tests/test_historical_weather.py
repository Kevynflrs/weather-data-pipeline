from src.ingestion.observations import fetch_historical_weather


df = fetch_historical_weather(
    latitude=48.8566,
    longitude=2.3522,
    start_date="2026-08-25",
    end_date="2026-08-26",
    insee_code="75056",
    city="Paris",
)

print(df.head())
print()
print(df.columns)
print()
print(df.shape)