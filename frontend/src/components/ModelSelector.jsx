import React from 'react';

const ModelSelector = ({ selected, onChange, disabled }) => {
  const models = [
    { value: 'arima', label: 'ARIMA' },
    { value: 'lstm', label: 'LSTM' },
    { value: 'gru', label: 'GRU' },
    { value: 'transformer', label: 'Transformer' },
    { value: 'ensemble', label: 'Ensemble' },
  ];
  
  return (
    <div className="space-y-2">
      {models.map((model) => (
        <button
          key={model.value}
          onClick={() => onChange(model.value)}
          disabled={disabled}
          className={`w-full px-3 py-2 rounded-md text-sm font-medium transition-colors text-left ${
            selected === model.value
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {model.label}
        </button>
      ))}
    </div>
  );
};

export default ModelSelector;