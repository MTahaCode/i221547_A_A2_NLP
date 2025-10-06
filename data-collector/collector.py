import time
import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCollector:
    """Data collection service using yfinance and MongoDB (no .env needed)"""
    
    def __init__(
        self,
        mongo_uri="mongodb://admin:admin123@localhost:27017/fintech_forecasting?authSource=admin",
        instruments=None,
        collection_interval=60
    ):
        self.mongo_uri = mongo_uri
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.get_database()
        self.collection = self.db.historical_data

        # Instruments to collect
        self.instruments = instruments or ["BTC-USD", "ETH-USD", "AAPL", "GOOGL"]
        
        # Collection interval in seconds
        self.interval = collection_interval
        
        logger.info(f"Data Collector initialized")
        logger.info(f"Instruments: {self.instruments}")
        logger.info(f"Collection interval: {self.interval} seconds")
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        try:
            self.collection.create_index([('symbol', 1), ('timestamp', -1)])
            self.collection.create_index([('timestamp', -1)])
            logger.info("Database indexes created/verified")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def fetch_historical_data(self, ticker, period_days=30):
        logger.info(f"Fetching {period_days} days of daily data for {ticker}")
        try:
            tk = yf.Ticker(ticker)
            df = tk.history(period=f"{period_days}d", interval="1d", auto_adjust=False)
            
            if df.empty:
                logger.warning(f"No data returned for {ticker}")
                return []
            
            df.index = pd.to_datetime(df.index)
            
            records = []
            for idx, row in df.iterrows():
                record = {
                    'symbol': ticker,
                    'timestamp': idx.to_pydatetime(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume']),
                    'source': 'yfinance',
                    'collected_at': datetime.now()
                }
                if record['close'] > 0:
                    records.append(record)
            
            logger.info(f"Processed {len(records)} daily records for {ticker}")
            return records
        except Exception as e:
            logger.error(f"Error fetching daily data for {ticker}: {e}")
            return []
    
    def fetch_hourly_data(self, ticker, days=7):
        logger.info(f"Fetching {days} days of hourly data for {ticker}")
        try:
            tk = yf.Ticker(ticker)
            df = tk.history(period=f"{days}d", interval="1h", auto_adjust=False)
            
            if df.empty:
                logger.warning(f"No hourly data returned for {ticker}")
                return []
            
            df.index = pd.to_datetime(df.index)
            records = []
            for idx, row in df.iterrows():
                record = {
                    'symbol': ticker,
                    'timestamp': idx.to_pydatetime(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume']),
                    'source': 'yfinance',
                    'collected_at': datetime.now()
                }
                if record['close'] > 0:
                    records.append(record)
            
            logger.info(f"Processed {len(records)} hourly records for {ticker}")
            return records
        except Exception as e:
            logger.error(f"Error fetching hourly data for {ticker}: {e}")
            return []
    
    def save_data(self, records):
        if not records:
            return 0
        inserted, updated = 0, 0
        for record in records:
            try:
                result = self.collection.update_one(
                    {'symbol': record['symbol'], 'timestamp': record['timestamp']},
                    {'$set': record},
                    upsert=True
                )
                if result.upserted_id:
                    inserted += 1
                elif result.modified_count > 0:
                    updated += 1
            except Exception as e:
                logger.error(f"Error saving record for {record.get('symbol')}: {e}")
        logger.info(f"Saved {inserted} new, updated {updated} existing records")
        return inserted + updated
    
    def seed_initial_data(self, ticker):
        logger.info(f"Seeding initial data for {ticker}")
        total_saved = 0
        daily_records = self.fetch_historical_data(ticker, period_days=365)
        if daily_records:
            total_saved += self.save_data(daily_records)
        time.sleep(1)
        hourly_records = self.fetch_hourly_data(ticker, days=7)
        if hourly_records:
            total_saved += self.save_data(hourly_records)
        return total_saved
    
    def collect_all(self):
        logger.info("Starting data collection cycle")
        total_saved = 0
        for ticker in self.instruments:
            logger.info(f"Processing {ticker}")
            total_saved += self.seed_initial_data(ticker)
            time.sleep(2)
        logger.info(f"Collection cycle complete. Total records processed: {total_saved}")
        return total_saved

# --------------------------
# Run locally for testing
# --------------------------
if __name__ == "__main__":
    collector = DataCollector()
    
    # Example: collect all instruments once
    total = collector.collect_all()
    print(f"Total records collected: {total}")
