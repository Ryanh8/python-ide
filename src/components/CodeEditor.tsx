import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import Console from './Console';

const CodeEditor: React.FC = () => {
  const [code, setCode] = useState<string>('');
  const [result, setResult] = useState<string>('');

  const handleTestCode = async () => {
    try {
      const response = await fetch('http://localhost:8000/executecodetest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setResult(`Error: ${errorData.detail}`);
      } else {
        const data = await response.json();
        setResult(data.result);
      }
    } catch (error) {
      if (error instanceof Error) {
        setResult(`Error: ${error.message}`);
      } else {
        setResult('An unknown error occurred');
      }
    }
  };

  const handleSubmitCode = async () => {
    try {
      const response = await fetch('http://localhost:8000/executeandstorecode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setResult(`Error: ${errorData.detail}`);
      } else {
        const data = await response.json();
        setResult(`Stored with ID: ${data.id}\nResult: ${data.result}`);
      }
    } catch (error) {
      if (error instanceof Error) {
        setResult(`Error: ${error.message}`);
      } else {
        setResult('An unknown error occurred');
      }
    }
  };

  const handleClearCode = () => {
    setCode('');
    setResult('');
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
            onClick={handleSubmitCode}
          >
            Submit Code
          </button>
          <button
            className="bg-red-500 text-white px-4 py-2 rounded"
            onClick={handleClearCode}
          >
            Clear Code
          </button>
        </div>
      </div>
      <Console output={result} />
    </div>
  );
};

export default CodeEditor;
