import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import polyline from '@mapbox/polyline';

function MapUpdater({ route, allHazards }) {
  const map = useMap();
  
  useEffect(() => {
    if (route && route.polyline) {
      const decodedPath = polyline.decode(route.polyline);
      // polyline returns [lat, lng] array
      if (decodedPath.length > 0) {
        map.fitBounds(decodedPath, { padding: [50, 50] });
      }
    }
  }, [route, map]);
  
  return null;
}

export default function MapDisplay({ route }) {
  if (!route) {
    return (
      <div className="map-container empty-state">
        <p>Select a route to view on map</p>
      </div>
    );
  }

  const decodedPath = polyline.decode(route.polyline);

  return (
    <div className="map-container">
      <MapContainer 
        center={decodedPath[0] || [13.0827, 80.2707]} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        {decodedPath.length > 0 && (
          <Polyline 
            positions={decodedPath} 
            pathOptions={{ 
              color: route.recommended ? '#10b981' : '#3b82f6', 
              weight: 5,
              opacity: 0.8
            }} 
          />
        )}

        {route.hazards && route.hazards.map((h, i) => (
          <Marker 
            key={`hazard-${i}`} 
            position={[h.hazard.latitude, h.hazard.longitude]}
          >
            <Popup>
              <strong>Hazard: {h.hazard.type}</strong><br/>
              Severity: {h.hazard.severity}<br/>
              {h.hazard.description}
            </Popup>
          </Marker>
        ))}

        {route.pitstops && route.pitstops.map((p, i) => (
          <Marker 
            key={`pitstop-${i}`} 
            position={[p.latitude, p.longitude]}
          >
            <Popup>
              <strong>{p.name}</strong><br/>
              {p.category}
            </Popup>
          </Marker>
        ))}
        
        <MapUpdater route={route} />
      </MapContainer>
    </div>
  );
}
