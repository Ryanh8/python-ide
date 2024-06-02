import React, { useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import Console from './Console';

const CodeEditor: React.FC = () => {
  const [code, setCode] = useState<string>('');
  const [result, setResult] = useState<string>('');
  const [submissions, setSubmissions] = useState<{ id: number, code: string, output: string }[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<{ id: number, code: string, output: string } | null>(null);

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    try {
      const response = await fetch('http://localhost:8000/submissions');
      const data = await response.json();
      setSubmissions(data);
    } catch (error) {
      console.error('Error fetching submissions:', error);
    }
  };

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
        setResult(`Code submitted successfully.\nStored with ID: ${data.id}\nResult: ${data.result}`);
        fetchSubmissions(); // Refresh submissions list
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

  const handleSubmissionClick = (submission: { id: number, code: string, output: string }) => {
    setSelectedSubmission(submission);
    setResult(submission.output);
    setCode(submission.code);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-center mt-4">Code Execution Site</h1>
      <div className="flex mt-4">
        <div className="w-1/4 bg-gray-200 p-4 rounded shadow">
          <h2 className="text-xl font-bold mb-4">Previous Submissions</h2>
          <ul>
            {submissions.map(submission => (
              <li key={submission.id} className="mb-2">
                <button
                  className="w-full text-left p-2 bg-blue-100 hover:bg-blue-200 rounded"
                  onClick={() => handleSubmissionClick(submission)}
                >
                  Submission ID: {submission.id}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="flex-1 ml-4">
          <div className="bg-white p-4 rounded shadow">
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
      </div>
    </div>
  );
};

export default CodeEditor;
