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
btc_data = get_historical_prices("bitcoin", 3600)
eth_data = get_historical_prices("ethereum", 3600)

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


from datetime import datetime, timedelta


# Prédictions:
days_to_predict = 30

def predict_next_days(series, n_days):
   
    trend = series.diff().tail(3000).mean()
    last_value = series.iloc[-1]
    predictions = []
    for i in range(n_days):
        last_value += trend
        predictions.append(round(last_value, 2))
    return predictions


# Générer les dates futures
last_date = datetime.strptime(df['Date'].iloc[-1], "%Y-%m-%d")
future_dates = [(last_date + timedelta(days=i+1)).strftime("%Y-%m-%d") for i in range(days_to_predict)]


btc_pred = predict_next_days(df['BTC'], days_to_predict)
eth_pred = predict_next_days(df['ETH'], days_to_predict)


predictions = []
for i in range(days_to_predict):
    predictions.append({
        "date": future_dates[i],
        "btc_pred": btc_pred[i],
        "eth_pred": eth_pred[i]
    })


with open("data/predictions.json", "w") as f:
    json.dump(predictions, f, indent=2)

print("✅ predictions.json créé avec", days_to_predict, "jours de prédiction !")
