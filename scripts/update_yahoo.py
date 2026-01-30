import requests
import pandas as pd
from datetime import datetime
import json

def get_historical_prices(coin_id, days=60):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["prices"]

# Récupérer BTC et ETH
btc_data = get_historical_prices("bitcoin", 60)
eth_data = get_historical_prices("ethereum", 60)

# Créer DataFrame
df = pd.DataFrame({
    "Date": [datetime.fromtimestamp(ts/1000).strftime("%Y-%m-%d") for ts, _ in btc_data],
    "BTC": [price for _, price in btc_data],
    "ETH": [price for _, price in eth_data]
})

# Calcul % journalier
df["BTC_pct"] = df["BTC"].pct_change().fillna(0) * 100
df["ETH_pct"] = df["ETH"].pct_change().fillna(0) * 100
df["BTC_pct"] = df["BTC_pct"].round(3)
df["ETH_pct"] = df["ETH_pct"].round(3)

# Convertir en JSON
records = df.rename(columns={"Date": "date", "BTC": "btc_close", "ETH": "eth_close"}).to_dict(orient="records")
for r in records:
    r["btc_pct"] = r.pop("BTC_pct")
    r["eth_pct"] = r.pop("ETH_pct")

# Écrire dans les fichiers JSON
with open("data/prices.json", "w") as f:
    json.dump(records, f, indent=2)

with open("data/table.json", "w") as f:
    json.dump(records, f, indent=2)

print("✅ prices.json et table.json mis à jour !")
