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
        <div className="mt-8">
            <h2 className="text-2xl font-bold mb-4">Document History</h2>
            {error && <div className="text-red-500 mb-4">{error}</div>}
            <div className="w-full overflow-x-auto shadow rounded-lg">
                <table className="min-w-full table-auto">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Filename
                            </th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Category
                            </th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Confidence
                            </th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Upload Date
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {documents.length === 0 ? (
                            <tr>
                                <td colSpan="4" className="px-4 py-2 text-center text-gray-500">
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
                                    <td className="px-4 py-2">
                                        {(doc.confidence_score * 100).toFixed(1)}%
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