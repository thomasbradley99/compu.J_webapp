import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

const API_URL = 'http://localhost:8000/api';  // Match your existing API_URL from documentService.js

const COLORS = {
  'Technical Documentation': '#0088FE',
  'Business Proposal': '#00C49F',
  'Legal Document': '#FFBB28',
  'Academic Paper': '#FF8042',
  'General Article': '#8884d8',
  'Other': '#82ca9d'
};

const StatsOverview = () => {
  const [stats, setStats] = useState({
    total_documents: 0,
    category_distribution: {},
    documents: []
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_URL}/stats`);
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
        // Fallback to fetching documents directly
        try {
          const docsResponse = await axios.get(`${API_URL}/documents`);
          const documents = docsResponse.data;
          
          // Calculate stats from documents
          const distribution = documents.reduce((acc, doc) => {
            acc[doc.predicted_category] = (acc[doc.predicted_category] || 0) + 1;
            return acc;
          }, {});

          setStats({
            total_documents: documents.length,
            category_distribution: distribution,
            documents: documents
          });
        } catch (fallbackError) {
          console.error('Error fetching documents:', fallbackError);
        }
      }
    };

    fetchStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const getMostCommonCategory = () => {
    return Object.entries(stats.category_distribution)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A';
  };

  const getAverageFileSize = () => {
    if (!stats.documents.length) return '0 KB';
    const avgSize = stats.documents.reduce((acc, doc) => acc + doc.file_size, 0) / stats.documents.length;
    return `${(avgSize / 1024).toFixed(1)} KB`;
  };

  const getHighConfidenceCount = () => {
    const highConfDocs = stats.documents.filter(doc => doc.confidence_score >= 0.5);
    return {
      count: highConfDocs.length,
      percentage: stats.documents.length ? 
        ((highConfDocs.length / stats.documents.length) * 100).toFixed(0) : 0
    };
  };

  // Transform category distribution for PieChart
  const chartData = Object.entries(stats.category_distribution).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex gap-4 mb-8 overflow-x-auto pb-2">
        {/* Total Documents */}
        <div className="bg-blue-50 p-4 rounded-lg min-w-[200px]">
          <h3 className="text-lg font-semibold text-blue-800">Total Documents</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.total_documents}</p>
        </div>
        
        {/* Most Common Category */}
        <div className="bg-green-50 p-4 rounded-lg min-w-[200px]">
          <h3 className="text-lg font-semibold text-green-800">Most Common</h3>
          <p className="text-xl font-bold text-green-600">{getMostCommonCategory()}</p>
        </div>

        {/* Average File Size */}
        <div className="bg-purple-50 p-4 rounded-lg min-w-[200px]">
          <h3 className="text-lg font-semibold text-purple-800">Avg File Size</h3>
          <p className="text-3xl font-bold text-purple-600">{getAverageFileSize()}</p>
        </div>

        {/* High Confidence Docs */}
        <div className="bg-yellow-50 p-4 rounded-lg min-w-[200px]">
          <h3 className="text-lg font-semibold text-yellow-800">High Confidence</h3>
          <p className="text-3xl font-bold text-yellow-600">{getHighConfidenceCount().count}</p>
          <p className="text-sm text-yellow-600">({getHighConfidenceCount().percentage}%)</p>
        </div>
      </div>

      {/* Category Distribution in a table format */}
      <h3 className="text-lg font-semibold mb-4">Category Distribution</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Count
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Percentage
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Visualization
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {chartData.map((entry) => (
              <tr key={entry.name} className="hover:bg-gray-50">
                <td className="px-4 py-2">
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[entry.name] }} />
                    {entry.name}
                  </div>
                </td>
                <td className="px-4 py-2">{entry.value}</td>
                <td className="px-4 py-2">
                  {((entry.value / stats.total_documents) * 100).toFixed(1)}%
                </td>
                <td className="px-4 py-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full" 
                      style={{ 
                        width: `${(entry.value / stats.total_documents) * 100}%`,
                        backgroundColor: COLORS[entry.name]
                      }} 
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StatsOverview; 