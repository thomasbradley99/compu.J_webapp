import axios from 'axios';

const API_URL = 'http://localhost:8000/api';  // FastAPI default port

export const uploadDocument = async (files) => {
    // Convert single file to array if needed
    const fileArray = Array.isArray(files) ? files : [files];
    const formData = new FormData();
    
    // Append all files to formData
    fileArray.forEach((file) => {
        formData.append('files', file);
    });
    
    try {
        const response = await axios.post(`${API_URL}/classify-batch`, formData);
        
        // Add response validation
        if (!response.data || !Array.isArray(response.data)) {
            throw new Error('Invalid response format from server');
        }
        
        return response.data;
    } catch (error) {
        console.error('Error uploading documents:', error);
        if (error.response) {
            // Server responded with an error
            throw new Error(error.response.data.detail || 'Server error');
        } else if (error.request) {
            // Request made but no response
            throw new Error('No response from server');
        } else {
            // Something else went wrong
            throw new Error('Failed to upload documents');
        }
    }
};

export const getDocumentHistory = async () => {
    try {
        const response = await axios.get(`${API_URL}/documents`);
        return response.data;
    } catch (error) {
        console.error('Error fetching document history:', error);
        throw error;
    }
}; 