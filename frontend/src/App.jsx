import React, { useState, useEffect } from 'react';
import { Search, Loader2 } from 'lucide-react';
import RouteCard from './components/RouteCard';
import MapDisplay from './components/MapDisplay';

export default function App() {
  const [challenge, setChallenge] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedRouteId, setSelectedRouteId] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Using relative path for Vercel deployment compatibility
      const response = await fetch('/api/demo');
      const json = await response.json();
      setData(json);
      if (json.routes && json.routes.length > 0) {
        setSelectedRouteId(json.routes[0].route_id);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch initial demo data
    fetchData();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchData(); // For MVP, we just reload the demo data
  };

  const selectedRoute = data?.routes?.find(r => r.route_id === selectedRouteId);

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>CareGPS</h1>
          <p style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>
            Routes built around you, not just the fastest route.
          </p>
          
          <form className="search-form" onSubmit={handleSearch}>
            <div className="input-group">
              <label>Challenge or Preference</label>
              <input 
                type="text" 
                placeholder="e.g. I'm a new driver and nervous about highways"
                value={challenge}
                onChange={(e) => setChallenge(e.target.value)}
              />
            </div>
            <button type="submit" className="search-btn" disabled={loading}>
              {loading ? <Loader2 className="loader" size={18} /> : <Search size={18} />}
              Find Safe Routes
            </button>
          </form>
        </div>

        <div className="routes-list">
          {loading ? (
            <div className="empty-state">
              <Loader2 className="loader" size={32} />
              <p style={{marginTop: '1rem'}}>Analyzing safe routes...</p>
            </div>
          ) : data ? (
            <>
              {data.recommendation && (
                <div className="recommendation-banner">
                  <h3>Recommendation</h3>
                  <p>{data.recommendation.reason}</p>
                </div>
              )}
              
              {data.routes.map(route => (
                <RouteCard 
                  key={route.route_id}
                  route={route}
                  isSelected={selectedRouteId === route.route_id}
                  onClick={() => setSelectedRouteId(route.route_id)}
                />
              ))}
            </>
          ) : (
            <div className="empty-state">
              <p>Enter a challenge to get started.</p>
            </div>
          )}
        </div>
      </div>
      
      <MapDisplay route={selectedRoute} />
    </div>
  );
}
