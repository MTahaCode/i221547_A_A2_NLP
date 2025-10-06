import React, { useState } from 'react';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from 'react-query';
import CandlestickChart from './components/CandlestickChart';
import InstrumentSelector from './components/InstrumentSelector';
import ForecastHorizonSelector from './components/ForecastHorizonSelector';
import ModelSelector from './components/ModelSelector';
import MetricsDisplay from './components/MetricsDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import { instrumentsAPI, forecastsAPI } from './services/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

function ForecastApp() {
  const [selectedInstrument, setSelectedInstrument] = useState('');
  const [selectedHorizon, setSelectedHorizon] = useState('24hrs');
  const [selectedModel, setSelectedModel] = useState('ensemble');
  const [currentForecast, setCurrentForecast] = useState(null);

  const { data: instrumentsData, isLoading: instrumentsLoading } = useQuery(
    'instruments',
    () => instrumentsAPI.getAll().then(res => res.data.data),
    { staleTime: 300000 }
  );

  const { data: historicalData, isLoading: historicalLoading } = useQuery(
    ['historical', selectedInstrument],
    () => instrumentsAPI.getHistorical(selectedInstrument, { days: 30, interval: '1h' })
      .then(res => res.data.data),
    { enabled: !!selectedInstrument }
  );

  const { data: modelPerformance } = useQuery(
    ['performance', selectedInstrument],
    () => forecastsAPI.getModelPerformance(selectedInstrument)
      .then(res => res.data.data),
    { enabled: !!selectedInstrument }
  );

  const forecastMutation = useMutation(
    (data) => forecastsAPI.create(data).then(res => res.data.data),
    {
      onSuccess: (data) => {
        setCurrentForecast(data);
      },
      onError: (error) => {
        const message = error.response?.data?.message || error.message;
        alert(`Error: ${message}`);
      },
    }
  );

  const handleGenerateForecast = () => {
    if (!selectedInstrument) {
      alert('Please select an instrument');
      return;
    }

    forecastMutation.mutate({
      symbol: selectedInstrument,
      horizon: selectedHorizon,
      model_type: selectedModel,
    });
  };

  const handleInstrumentChange = (symbol) => {
    setSelectedInstrument(symbol);
    setCurrentForecast(null);
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <header className="bg-gray-800 border-b border-gray-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-blue-400">
            FinTech Forecasting Platform
          </h1>
          <p className="text-gray-400 mt-2 text-sm">
            AI-powered financial forecasting with ARIMA, LSTM, GRU, Transformer, and Ensemble models
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Controls Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            
            {/* Instrument Selection */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 shadow">
              <h2 className="text-lg font-semibold text-white mb-4">Select Instrument</h2>
              <InstrumentSelector
                instruments={instrumentsData || []}
                selected={selectedInstrument}
                onChange={handleInstrumentChange}
                loading={instrumentsLoading}
              />
            </div>

            {/* Model Selection */}
            {selectedInstrument && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 shadow">
                <h2 className="text-lg font-semibold text-white mb-4">Model Type</h2>
                <ModelSelector
                  selected={selectedModel}
                  onChange={setSelectedModel}
                  disabled={forecastMutation.isLoading}
                />
              </div>
            )}

            {/* Horizon Selection */}
            {selectedInstrument && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 shadow">
                <h2 className="text-lg font-semibold text-white mb-4">Forecast Horizon</h2>
                <ForecastHorizonSelector
                  selected={selectedHorizon}
                  onChange={setSelectedHorizon}
                  disabled={forecastMutation.isLoading}
                />
              </div>
            )}

            {/* Generate Button */}
            {selectedInstrument && (
              <button
                onClick={handleGenerateForecast}
                disabled={forecastMutation.isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-colors shadow-lg"
              >
                {forecastMutation.isLoading ? (
                  <span className="flex items-center justify-center">
                    <LoadingSpinner size="small" />
                    <span className="ml-2">Generating...</span>
                  </span>
                ) : (
                  'Generate Forecast'
                )}
              </button>
            )}

            {/* Metrics Display */}
            {currentForecast?.metrics && Object.keys(currentForecast.metrics).length > 0 && (
              <MetricsDisplay
                metrics={currentForecast.metrics}
                modelType={currentForecast.model_type}
              />
            )}

            {/* Model Performance */}
            {modelPerformance && modelPerformance.length > 0 && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 shadow">
                <h3 className="text-lg font-semibold text-white mb-3">Model Performance</h3>
                <div className="space-y-2">
                  {modelPerformance.slice(0, 5).map((perf) => (
                    <div key={perf.model_type} className="text-sm border-b border-gray-700 pb-2">
                      <div className="font-medium text-blue-400 capitalize">{perf.model_type}</div>
                      {perf.metrics && Object.keys(perf.metrics).length > 0 && (
                        <div className="text-gray-400 text-xs mt-1">
                          {perf.metrics.rmse && `RMSE: ${perf.metrics.rmse.toFixed(2)}`}
                          {perf.metrics.mae && ` | MAE: ${perf.metrics.mae.toFixed(2)}`}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chart Area */}
          <div className="lg:col-span-3">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 shadow-lg">
              {!selectedInstrument ? (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center text-gray-400">
                    <svg className="mx-auto h-16 w-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                    <p className="text-lg font-medium">Select an instrument to view the chart</p>
                    <p className="text-sm text-gray-500 mt-2">Choose from stocks, cryptocurrencies, or forex pairs</p>
                  </div>
                </div>
              ) : historicalLoading ? (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <LoadingSpinner />
                    <p className="text-gray-400 mt-4">Loading historical data...</p>
                  </div>
                </div>
              ) : (
                <div style={{ height: '600px' }}>
                  <CandlestickChart
                    historicalData={historicalData}
                    forecastData={currentForecast}
                    title={`${selectedInstrument} - Price Chart & Forecast`}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-400 text-sm">
          <p>FinTech Forecasting Platform | Built with React, Flask, PyTorch &amp; MongoDB</p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ForecastApp />
    </QueryClientProvider>
  );
}

export default App;