import React from 'react';

interface ConsoleProps {
  output: string;
}

const Console: React.FC<ConsoleProps> = ({ output }) => {
  return (
    <div className="bg-black text-white p-4 rounded mt-4 h-48 overflow-y-auto">
      <h2 className="text-lg font-bold mb-2">Console Output</h2>
      <pre>{output}</pre>
    </div>
  );
};

export default Console;
