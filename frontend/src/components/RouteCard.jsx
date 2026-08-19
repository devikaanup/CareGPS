import React from 'react';
import { Clock, Navigation, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import ScoreChart from './ScoreChart';

export default function RouteCard({ route, isSelected, onClick }) {
  const formatTime = (seconds) => {
    const mins = Math.round(seconds / 60);
    if (mins > 60) {
      return `${Math.floor(mins / 60)}h ${mins % 60}m`;
    }
    return `${mins} min`;
  };

  const formatDist = (meters) => {
    return `${(meters / 1000).toFixed(1)} km`;
  };

  return (
    <div 
      className={`route-card ${isSelected ? 'selected' : ''} ${route.recommended ? 'recommended' : ''}`}
      onClick={onClick}
    >
      <div className="route-header">
        <div className="route-title">
          <div className="route-name">
            {route.label}
            {route.recommended && <span className="badge badge-recommended">Recommended</span>}
          </div>
          <div className="route-stats">
            <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}>
              <Clock size={14} /> {formatTime(route.duration_seconds)}
            </span>
            <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}>
              <Navigation size={14} /> {formatDist(route.distance_meters)}
            </span>
          </div>
        </div>
        <div className="route-score">
          <span className="score-value">{Math.round(route.scores.overall)}</span>
          <span className="score-label">Overall Match</span>
        </div>
      </div>

      <ScoreChart scores={route.scores} />

      <div className="route-details">
        {route.advantages.length > 0 && (
          <ul className="detail-list pro">
            {route.advantages.map((adv, i) => (
              <li key={`adv-${i}`}><CheckCircle size={14} /> {adv}</li>
            ))}
          </ul>
        )}
        
        {route.warnings && route.warnings.length > 0 && (
          <ul className="detail-list warn">
            {route.warnings.map((warn, i) => (
              <li key={`warn-${i}`}><AlertTriangle size={14} /> {warn}</li>
            ))}
          </ul>
        )}

        {route.disadvantages.length > 0 && (
          <ul className="detail-list con">
            {route.disadvantages.map((dis, i) => (
              <li key={`dis-${i}`}><XCircle size={14} /> {dis}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
