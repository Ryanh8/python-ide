import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import Console from './Console';
import Terminal from './Terminal';

const CodeEditor: React.FC = () => {
  const [code, setCode] = useState<string>('');
  const [result, setResult] = useState<string>('');
  const [terminalInput, setTerminalInput] = useState<string>('');

  const handleTestCode = async () => {
    const response = await fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });
    const data = await response.json();
    setResult(data.result);
  };

  const handleSubmit = async () => {
    const response = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });
    const data = await response.json();
    if (data.success) {
      setResult('Code submitted successfully');
    }
  };

  const handleExecute = async () => {
    // Execute terminal input code
    const response = await fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: terminalInput }),
    });
    const data = await response.json();
    setResult(data.result);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-center mt-4">Code Execution Site</h1>
      <div className="mt-4 bg-white p-4 rounded shadow">
        <Editor
          height="50vh"
          defaultLanguage="python"
          value={code}
          onChange={(value) => setCode(value || '')}
        />
        <div className="flex space-x-4 mt-4">
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded"
            onClick={handleTestCode}
          >
            Test Code
          </button>
          <button
            className="bg-green-500 text-white px-4 py-2 rounded"
            onClick={handleSubmit}
          >
            Submit
          </button>
        </div>
      </div>
      <Console output={result} />
      <Terminal
        input={terminalInput}
        onInputChange={setTerminalInput}
        onExecute={handleExecute}
      />
    </div>
  );
};

export default CodeEditor;
