import React from 'react';

const MetricsDisplay = ({ metrics, modelType }) => {
  const formatMetric = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return typeof value === 'number' ? value.toFixed(4) : value;
  };

  const metricLabels = {
    rmse: 'RMSE',
    mae: 'MAE',
    mape: 'MAPE',
    r2_score: 'R² Score',
    directional_accuracy: 'Direction Accuracy'
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 shadow">
      <h3 className="text-lg font-semibold text-white mb-3">
        Performance Metrics
      </h3>
      <div className="text-xs text-gray-400 mb-3 capitalize">{modelType} Model</div>
      <div className="space-y-2">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="flex justify-between items-center text-sm">
            <span className="text-gray-400">{metricLabels[key] || key}:</span>
            <span className="font-mono text-green-400">{formatMetric(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsDisplay;