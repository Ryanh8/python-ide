import React from 'react';

interface TerminalProps {
  input: string;
  onInputChange: (input: string) => void;
  onExecute: () => void;
}

const Terminal: React.FC<TerminalProps> = ({ input, onInputChange, onExecute }) => {
  return (
    <div className="bg-gray-800 text-white p-4 rounded mt-4">
      <h2 className="text-lg font-bold mb-2">Terminal</h2>
      <textarea
        className="w-full h-24 bg-gray-700 text-white p-2 rounded"
        value={input}
        onChange={(e) => onInputChange(e.target.value)}
      ></textarea>
      <button
        className="mt-2 bg-blue-500 text-white px-4 py-2 rounded"
        onClick={onExecute}
      >
        Execute
      </button>
    </div>
  );
};

export default Terminal;
