const ConfidenceIndicator = ({ score, level }) => {
  const colors = {
    high: {
      bg: "bg-green-500",
      text: "text-green-700",
      light: "bg-green-100"
    },
    medium: {
      bg: "bg-yellow-500",
      text: "text-yellow-700",
      light: "bg-yellow-100"
    },
    low: {
      bg: "bg-red-500",
      text: "text-red-700",
      light: "bg-red-100"
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`flex-shrink-0 w-2 h-2 rounded-full ${colors[level].bg}`} />
      <div className={`text-sm flex flex-wrap items-center ${colors[level].text}`}>
        <span className="font-medium">{(score * 100).toFixed(1)}%</span>
        <div className={`ml-2 px-2 py-0.5 rounded-full ${colors[level].light} text-xs`}>
          {level.charAt(0).toUpperCase() + level.slice(1)} confidence
        </div>
      </div>
    </div>
  );
};

export default ConfidenceIndicator; 