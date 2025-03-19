import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import DocumentHistory from './components/DocumentHistory';
import { uploadDocument } from './services/documentService';
import ConfidenceIndicator from './components/ConfidenceIndicator';
import StatsOverview from './components/StatsOverview';

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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">A1 Smart Doc Classifier</h1>
          <p className="text-gray-500 mt-1">Automatically classify your documents using AI</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Upload Area */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'}`}
          >
            <input {...getInputProps()} multiple accept=".txt,.pdf,.docx" />
            {isDragActive ? (
              <div className="text-blue-500">
                <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p>Drop files to classify...</p>
              </div>
            ) : (
              <div>
                <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3-3m0 0l3 3m-3-3v12" />
                </svg>
                <p>Drag and drop documents here, or click to select</p>
                <p className="text-sm text-gray-500 mt-2">
                  Supported formats: TXT, PDF, DOCX
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Processing Status & Results */}
        {loading && (
          <div className="bg-blue-50 text-blue-700 p-4 rounded-lg mb-8 flex items-center justify-center">
            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Processing documents...
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-8">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-xl font-semibold mb-6">Classification Results</h2>
            <div className="grid grid-cols-1 gap-4">
              {results.map((result, index) => (
                <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
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

        {/* Stats Section */}
        <div className="mb-8">
          <StatsOverview />
        </div>

        {/* Document History */}
        <DocumentHistory />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-gray-500 text-sm">
            Powered by Hugging Face's BART model for zero-shot classification
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App; 