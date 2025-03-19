import React from 'react';

const ConfidenceIndicator = ({ score, level }) => {
  // Default to 'low' if level is undefined
  const confidenceLevel = level || (
    score >= 0.75 ? 'high' :
    score >= 0.50 ? 'medium' : 
    'low'
  );

  const styles = {
    high: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-200'
    },
    medium: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      border: 'border-yellow-200'
    },
    low: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-200'
    }
  };

  // Add safety check for styles
  const style = styles[confidenceLevel] || styles.low;

  return (
    <div className="flex items-center">
      <div className={`px-2 py-1 rounded-full ${style.bg} ${style.text} ${style.border} text-sm font-medium`}>
        {(score * 100).toFixed(1)}%
      </div>
      {confidenceLevel === 'low' && (
        <span className="ml-2 text-red-600 text-sm">
          Low confidence
        </span>
      )}
    </div>
  );
};

export default ConfidenceIndicator; 