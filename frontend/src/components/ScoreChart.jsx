import React from 'react';

export default function ScoreChart({ scores }) {
  const categories = [
    { key: 'safety', label: 'Safety', color: '#10b981' },
    { key: 'accessibility', label: 'Access', color: '#3b82f6' },
    { key: 'comfort', label: 'Comfort', color: '#a855f7' },
    { key: 'traffic', label: 'Traffic', color: '#f59e0b' },
    { key: 'convenience', label: 'Convenience', color: '#06b6d4' },
    { key: 'time', label: 'Time', color: '#ef4444' }
  ];

  return (
    <div className="score-bars">
      {categories.map((cat) => (
        <div key={cat.key} className="score-bar-row">
          <div className="score-bar-label">{cat.label}</div>
          <div className="score-bar-track">
            <div 
              className="score-bar-fill" 
              style={{ 
                width: `${scores[cat.key]}%`,
                backgroundColor: cat.color
              }} 
            />
          </div>
          <div style={{ marginLeft: '8px', width: '25px', textAlign: 'right' }}>
            {Math.round(scores[cat.key])}
          </div>
        </div>
      ))}
    </div>
  );
}
