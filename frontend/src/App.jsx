import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import DocumentHistory from './components/DocumentHistory';
import { uploadDocument } from './services/documentService';
import ConfidenceIndicator from './components/ConfidenceIndicator';

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    setLoading(true);
    setError(null);
    try {
      const response = await uploadDocument(acceptedFiles);
      setResults(response);
    } catch (err) {
      setError('Failed to process documents');
    } finally {
      setLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: true
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">A1 Smart Doc Classifier</h1>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
      >
        <input {...getInputProps()} multiple accept=".txt,.pdf,.docx" />
        {isDragActive ? (
          <p>Drop the files here ...</p>
        ) : (
          <p>Drag and drop documents here, or click to select multiple files<br/>
          <span className="text-sm text-gray-500">
            (Hold Shift to select multiple files • Supported formats: TXT, PDF, DOCX)
          </span></p>
        )}
      </div>

      {loading && (
        <div className="mt-4 text-center">
          <p>Processing documents...</p>
        </div>
      )}

      {error && (
        <div className="mt-4 text-center text-red-500">
          <p>{error}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="mt-8 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-6">Classification Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((result, index) => (
              <div key={index} className="p-4 border rounded-lg bg-gray-50 hover:shadow-md transition-shadow">
                <div className="flex flex-col space-y-3">
                  {/* Filename with truncation */}
                  <p className="font-medium text-gray-900 truncate" title={result.filename}>
                    {result.filename}
                  </p>
                  
                  {result.error ? (
                    <p className="text-red-500">{result.error}</p>
                  ) : (
                    <>
                      {/* Category */}
                      <div className="flex flex-col">
                        <span className="text-sm text-gray-500">Category</span>
                        <span className={`font-medium ${result.confidence_level === 'low' ? 'text-red-600' : 'text-gray-900'}`}>
                          {result.predicted_category}
                        </span>
                      </div>

                      {/* Confidence Indicator */}
                      <div className="flex flex-col">
                        <span className="text-sm text-gray-500">Confidence</span>
                        <ConfidenceIndicator 
                          score={result.confidence_score} 
                          level={result.confidence_level} 
                        />
                      </div>

                      {/* Warning for low confidence */}
                      {result.confidence_level === 'low' && (
                        <div className="text-sm text-red-600 flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                          Manual review recommended
                        </div>
                      )}

                      {/* Show all category scores in a collapsible section */}
                      <details className="mt-2">
                        <summary className="text-sm text-blue-600 cursor-pointer hover:text-blue-800">
                          Show all scores
                        </summary>
                        <div className="mt-2 space-y-1">
                          {Object.entries(result.category_scores).map(([category, score]) => (
                            <div key={category} className="text-sm flex justify-between">
                              <span className="text-gray-600">{category}:</span>
                              <span className="font-medium">{(score * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                        </div>
                      </details>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <DocumentHistory />
    </div>
  );
}

export default App; 