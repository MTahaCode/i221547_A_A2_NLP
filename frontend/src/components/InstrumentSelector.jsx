import React from 'react';

const InstrumentSelector = ({ instruments, selected, onChange, loading }) => {
  return (
    <select
      value={selected}
      onChange={(e) => onChange(e.target.value)}
      disabled={loading}
      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <option value="">-- Choose an instrument --</option>
      {instruments.map((instrument) => (
        <option key={instrument.symbol} value={instrument.symbol}>
          {instrument.name} ({instrument.symbol})
        </option>
      ))}
    </select>
  );
};

export default InstrumentSelector;