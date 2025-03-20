import React, { useState, useEffect } from 'react';
import { getDocumentHistory } from '../services/documentService';

function DocumentHistory() {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        try {
            const data = await getDocumentHistory();
            setDocuments(data || []);
            setLoading(false);
        } catch (err) {
            console.error('Error loading documents:', err);
            setDocuments([]);
            setError('Failed to load documents');
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Document History</h2>
                <div>Loading...</div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Document History</h2>
            {error && <div className="text-red-500 mb-4">{error}</div>}
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Filename</th>
                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Category</th>
                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Confidence</th>
                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Size</th>
                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Tokens</th>
                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Chunks</th>
                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Upload Date</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {documents.length === 0 ? (
                            <tr>
                                <td colSpan="7" className="px-4 py-2 text-center text-gray-500">
                                    No documents found
                                </td>
                            </tr>
                        ) : (
                            documents.map((doc) => (
                                <tr key={doc.id} className="hover:bg-gray-50">
                                    <td className="px-4 py-2 max-w-xs truncate" title={doc.original_filename}>
                                        {doc.original_filename}
                                    </td>
                                    <td className="px-4 py-2">{doc.predicted_category}</td>
                                    <td className={`px-4 py-2 ${
                                        doc.confidence_score >= 0.60 ? 'text-green-600 font-bold' :
                                        doc.confidence_score >= 0.40 ? 'text-yellow-600' :
                                        'text-red-600'
                                    }`}>
                                        {(doc.confidence_score * 100).toFixed(1)}%
                                    </td>
                                    <td className="px-4 py-2">
                                        {(doc.file_size / 1024).toFixed(1)} KB
                                    </td>
                                    <td className="px-4 py-2">
                                        {doc.token_count || 'N/A'}
                                    </td>
                                    <td className="px-4 py-2">
                                        {doc.num_chunks || '1'}
                                    </td>
                                    <td className="px-4 py-2 whitespace-nowrap">
                                        {new Date(doc.created_at).toLocaleString()}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default DocumentHistory; 