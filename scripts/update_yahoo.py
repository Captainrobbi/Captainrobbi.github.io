import json
from datetime import datetime
import pandas as pd
import yfinance as yf

TICKERS = {
    "btc": "BTC-USD",
    "eth": "ETH-USD"
}

def download(ticker: str, period="180d", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df = df[["Date", "Close"]].rename(columns={"Date": "date", "Close": "close"})
    return df

def main():
    btc = download(TICKERS["btc"])
    eth = download(TICKERS["eth"])

    merged = pd.merge(btc, eth, on="date", suffixes=("_btc", "_eth"))
    merged = merged.rename(columns={"close_btc": "btc_close", "close_eth": "eth_close"})

    merged["btc_pct"] = (merged["btc_close"].pct_change() * 100).round(3).fillna(0)
    merged["eth_pct"] = (merged["eth_close"].pct_change() * 100).round(3).fillna(0)

    records = merged.to_dict(orient="records")

    with open("data/prices.json", "w") as f:
        json.dump(records, f, indent=2)

    with open("data/table.json", "w") as f:
        json.dump(records, f, indent=2)

    meta = {
        "updated_at_utc": datetime.utcnow().isoformat() + "Z",
        "rows": len(records)
    }
    with open("data/meta.json", "w") as f:
        json.dump(meta, f, indent=2)

if __name__ == "__main__":
    main()
