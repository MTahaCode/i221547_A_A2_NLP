import React from 'react';

const ForecastHorizonSelector = ({ selected, onChange, disabled }) => {
  const horizons = [
    { value: '1hr', label: '1 Hour' },
    { value: '3hrs', label: '3 Hours' },
    { value: '24hrs', label: '24 Hours' },
    { value: '72hrs', label: '72 Hours' },
  ];
  
  return (
    <div className="grid grid-cols-2 gap-2">
      {horizons.map((horizon) => (
        <button
          key={horizon.value}
          onClick={() => onChange(horizon.value)}
          disabled={disabled}
          className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            selected === horizon.value
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {horizon.label}
        </button>
      ))}
    </div>
  );
};

export default ForecastHorizonSelector;