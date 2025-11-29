import express from 'express';
import cors from 'cors';
import { MongoClient } from 'mongodb';

const app = express();
app.use(cors());

const mongoUri = 'mongodb://localhost:27017';
const client = new MongoClient(mongoUri);

app.get('/api/ohlcv/:symbol', async (req, res) => {
  const { symbol } = req.params;

  try {
    await client.connect();
    const db = client.db('finance_db');

    // Find OHLCV data for this symbol, sorted by date ascending
    const data = await db
      .collection('ohlcv')
      .find({ symbol })
      .sort({ timestamp: 1 })
      .toArray();

    if (!data || data.length === 0) {
      return res.status(404).json({ message: `No OHLCV data found for ${symbol}` });
    }

    res.json({ status: 'success', data });
  } catch (error) {
    console.error('❌ Error fetching OHLCV:', error);
    res.status(500).json({ error: 'Database fetch failed' });
  }
});

app.get('/api/forecast/:symbol', async (req, res) => {
  const { symbol } = req.params;
  try {
    await client.connect();
    const db = client.db('finance_db');
    const forecast = await db.collection('forecasts').findOne({ symbol });
    res.json({ status: 'success', data: forecast });
  } catch (error) {
    console.error('❌ Error fetching forecast:', error);
    res.status(500).json({ error: 'Database fetch failed' });
  }
});

const PORT = 6000;
app.listen(PORT, () => console.log(`✅ Express proxy running on http://localhost:${PORT}`));
