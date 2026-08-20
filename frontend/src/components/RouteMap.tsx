import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, useMap } from 'react-leaflet';
import L from 'leaflet';
import polylineLib from '@mapbox/polyline';
import 'leaflet/dist/leaflet.css';
import { type RouteOption } from '@/data/mockRoutes';

function MapBounds({ coords }: { coords: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (coords.length > 0) {
      const bounds = L.latLngBounds(coords);
      map.fitBounds(bounds, { padding: [30, 30] });
    }
  }, [coords, map]);
  return null;
}

const startIcon = L.divIcon({
  html: `<div style="width: 14px; height: 14px; background: #1f9d63; border: 2.5px solid #1f2233; border-radius: 50%;"></div>`,
  className: '',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const endIcon = L.divIcon({
  html: `<div style="width: 14px; height: 14px; background: #e8624a; border: 2.5px solid #1f2233; border-radius: 50%;"></div>`,
  className: '',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

import { MapPlaceholder } from './MapPlaceholder';

export function RouteMap({ route }: { route: RouteOption | null }) {
  const [coords, setCoords] = useState<[number, number][]>([]);

  useEffect(() => {
    if (route?.polyline) {
      const decoded = polylineLib.decode(route.polyline);
      setCoords(decoded);
    } else {
      setCoords([]);
    }
  }, [route]);

  if (!route || !route.polyline || coords.length === 0) {
    return <MapPlaceholder />;
  }

  const startCoord = coords[0];
  const endCoord = coords[coords.length - 1];

  return (
    <div className="w-full h-full min-h-[400px] rounded-doodle border-[2.5px] border-ink overflow-hidden relative z-0">
      <MapContainer
        center={startCoord}
        zoom={13}
        style={{ width: '100%', height: '100%', minHeight: '400px', zIndex: 0 }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={coords} color="#2f6fed" weight={5} lineCap="round" lineJoin="round" />
        <Marker position={startCoord} icon={startIcon} />
        <Marker position={endCoord} icon={endIcon} />
        <MapBounds coords={coords} />
      </MapContainer>
    </div>
  );
}
