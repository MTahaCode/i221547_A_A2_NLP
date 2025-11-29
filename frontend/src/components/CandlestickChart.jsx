import React, { useEffect, useMemo, useState } from 'react';
import Plot from 'react-plotly.js';

// Dummy historical and forecast data for initial display
const DUMMY_HISTORICAL = [
  { timestamp: '2025-10-01', open: 100, high: 110, low: 95, close: 105 },
  { timestamp: '2025-10-02', open: 105, high: 115, low: 102, close: 108 },
  { timestamp: '2025-10-03', open: 108, high: 120, low: 107, close: 115 },
  { timestamp: '2025-10-04', open: 115, high: 118, low: 110, close: 112 },
  { timestamp: '2025-10-05', open: 112, high: 117, low: 109, close: 115 },
];

const DUMMY_FORECAST = {
  model_type: 'dummy',
  predictions: [
    { timestamp: '2025-10-06', predicted_close: 117, confidence_lower: 114, confidence_upper: 120 },
    { timestamp: '2025-10-07', predicted_close: 119, confidence_lower: 116, confidence_upper: 122 },
    { timestamp: '2025-10-08', predicted_close: 121, confidence_lower: 118, confidence_upper: 124 },
  ],
};

const CandlestickChart = ({ symbol, forecastData = null, title }) => {
  const [historicalData, setHistoricalData] = useState(DUMMY_HISTORICAL);
  const [forecastToUse, setForecastToUse] = useState(DUMMY_FORECAST);

  // Update forecast if prop changes
  useEffect(() => {
    if (forecastData) setForecastToUse(forecastData);
  }, [forecastData]);

  // Fetch real historical data from Express backend
  useEffect(() => {
    if (!symbol) return;

    const fetchHistorical = async () => {
      try {
        const res = await fetch(`http://localhost:6000/api/ohlcv?symbol=${symbol}`);
        const data = await res.json();
        if (data && data.length > 0) {
          setHistoricalData(data);
        }
      } catch (err) {
        console.error('Error fetching historical data:', err);
      }
    };

    fetchHistorical();
  }, [symbol]);

  const chartData = useMemo(() => {
    const traces = [];

    // Historical candlestick
    if (historicalData.length > 0) {
      traces.push({
        x: historicalData.map(d => d.timestamp),
        open: historicalData.map(d => Number(d.open)),
        high: historicalData.map(d => Number(d.high)),
        low: historicalData.map(d => Number(d.low)),
        close: historicalData.map(d => Number(d.close)),
        type: 'candlestick',
        name: 'Historical',
        increasing: { line: { color: '#10B981' } },
        decreasing: { line: { color: '#EF4444' } },
      });
    }

    // Forecast line
    if (forecastToUse && forecastToUse.predictions?.length > 0) {
      const preds = forecastToUse.predictions;
      const lastHist = historicalData[historicalData.length - 1];

      let x = preds.map(p => p.timestamp);
      let y = preds.map(p => Number(p.predicted_close));

      if (lastHist) {
        x = [lastHist.timestamp, ...x];
        y = [Number(lastHist.close), ...y];
      }

      traces.push({
        x,
        y,
        type: 'scatter',
        mode: 'lines+markers',
        name: `Forecast (${forecastToUse.model_type?.toUpperCase() || ''})`,
        line: { color: '#3B82F6', width: 3, dash: 'dash' },
        marker: { color: '#3B82F6', size: 6, symbol: 'diamond' },
      });

      // Confidence interval
      if (preds[0].confidence_lower && preds[0].confidence_upper) {
        let upper = preds.map(p => Number(p.confidence_upper));
        let lower = preds.map(p => Number(p.confidence_lower));
        if (lastHist) {
          upper = [Number(lastHist.close), ...upper];
          lower = [Number(lastHist.close), ...lower];
        }

        traces.push({
          x,
          y: upper,
          type: 'scatter',
          mode: 'lines',
          line: { width: 0 },
          showlegend: false,
          hoverinfo: 'skip',
        });

        traces.push({
          x,
          y: lower,
          type: 'scatter',
          mode: 'lines',
          fill: 'tonexty',
          fillcolor: 'rgba(59, 130, 246, 0.2)',
          line: { width: 0 },
          name: 'Confidence Interval',
        });
      }
    }

    return traces;
  }, [historicalData, forecastToUse]);

  const layout = {
    title: { text: title || 'Price Chart & Forecast' },
    dragmode: 'zoom',
    showlegend: true,
    xaxis: { type: 'date', rangeslider: { visible: false } },
    yaxis: { autorange: true },
    plot_bgcolor: '#1F2937',
    paper_bgcolor: '#111827',
    font: { color: '#E5E7EB' },
    hovermode: 'x unified',
    margin: { t: 60, b: 60, l: 80, r: 40 },
  };

  const config = { responsive: true, displayModeBar: true, displaylogo: false };

  return (
    <div style={{ width: '100%', height: '500px' }}>
      <Plot data={chartData} layout={layout} config={config} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};

export default CandlestickChart;
