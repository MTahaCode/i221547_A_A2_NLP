"""
structured_data_collector.py

Fetches:
  - OHLCV daily data via yfinance
  - Saves directly to MongoDB in the historical_data collection

Usage:
    python structured_data_collector.py --ticker AAPL --days 90

Dependencies:
    pip install yfinance pandas pymongo
"""

import argparse
from datetime import datetime
import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from typing import List

# -----------------------
# MongoDB Connection
# -----------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/fintech_forecasting?authSource=admin"
DB_NAME = "fintech_forecasting"
COLLECTION_NAME = "historical_data"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# -----------------------
# Schema class
# -----------------------
class OHLCVData:
    """Schema for OHLCV data"""
    
    def __init__(self, symbol: str, timestamp: datetime, open: float, 
                 high: float, low: float, close: float, volume: float):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'source': 'yfinance',
            'collected_at': datetime.now()
        }

# -----------------------
# Fetch OHLCV
# -----------------------
def fetch_ohlcv(ticker: str, period_days: int = 180) -> List[OHLCVData]:
    """Fetch daily OHLCV via yfinance"""
    tk = yf.Ticker(ticker)
    df = tk.history(period=f"{period_days}d", interval="1d", auto_adjust=False)

    if df.empty:
        print(f"No data returned for {ticker}")
        return []

    df.index = pd.to_datetime(df.index)

    records = []
    for idx, row in df.iterrows():
        try:
            record = OHLCVData(
                symbol=ticker,
                timestamp=idx.to_pydatetime(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row["Volume"])
            )
            records.append(record)
        except Exception as e:
            print(f"Error processing row for {ticker}: {e}")
            continue

    return records

# -----------------------
# Save to MongoDB
# -----------------------
def save_to_mongo(records: List[OHLCVData]):
    inserted, updated = 0, 0
    for r in records:
        res = collection.update_one(
            {'symbol': r.symbol, 'timestamp': r.timestamp},
            {'$set': r.to_dict()},
            upsert=True
        )
        if res.upserted_id:
            inserted += 1
        elif res.modified_count > 0:
            updated += 1

    print(f"Inserted: {inserted}, Updated: {updated}, Total: {inserted+updated}")

# -----------------------
# CLI
# -----------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Fetch OHLCV data and store in MongoDB")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol, e.g., AAPL or BTC-USD")
    parser.add_argument("--days", type=int, default=180, help="Number of historical days to fetch")
    return parser.parse_args()

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    args = parse_args()
    print(f"Fetching {args.days} days of OHLCV for {args.ticker}...")
    ohlcv_records = fetch_ohlcv(args.ticker, args.days)
    print(f"Fetched {len(ohlcv_records)} records.")
    
    if ohlcv_records:
        save_to_mongo(ohlcv_records)
        print("Data saved to MongoDB successfully.")
