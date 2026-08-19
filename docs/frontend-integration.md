# Frontend Integration Guide

> For the frontend developer building the RouteEase React UI.

---

## Quick Start

1. **Backend URL**: `http://localhost:8000`
2. **API Docs (interactive)**: `http://localhost:8000/docs`
3. **Full mock response**: `backend/data/mock_route_response.json`

---

## Getting Started Without Backend

You can start building immediately using the **demo endpoint**:

```js
const response = await fetch("http://localhost:8000/api/demo");
const data = await response.json();
```

This returns a complete response with 3 routes, scores, hazards, pitstops, and a recommendation — all demo data.

---

## Primary Flow

### 1. User enters challenge + origin/destination

```js
const result = await fetch("http://localhost:8000/api/routes/plan", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    origin: { latitude: 13.0827, longitude: 80.2707 },
    destination: { latitude: 13.0674, longitude: 80.2376 },
    challenge_text: "I'm a new driver and highways make me nervous."
  })
});
const plan = await result.json();
```

### 2. Display routes from `plan.routes`

Each route has:
- `route_id` — unique identifier
- `label` — "Fastest", "Recommended", "Alternative"
- `recommended` — boolean
- `distance_meters`, `duration_seconds`
- `scores` — breakdown (overall, safety, accessibility, comfort, traffic, convenience, time)
- `traffic` — availability, level, delay
- `hazards` — list of hazards affecting this route
- `pitstops` — relevant stops along route
- `advantages` / `disadvantages` — human-readable lists
- `polyline` — encoded polyline for Google Maps display

### 3. Display recommendation from `plan.recommendation`

```json
{
  "route_id": "route_002",
  "reason": "Avoids highways and difficult merges..."
}
```

### 4. Display metadata from `plan.metadata`

Show data source badges so users know what's live vs demo.

---

## Map Display

The backend returns **encoded polylines** in each route's `polyline` field.

To display on Google Maps JavaScript API:

```js
const decodedPath = google.maps.geometry.encoding.decodePath(route.polyline);
const routeLine = new google.maps.Polyline({
  path: decodedPath,
  strokeColor: route.recommended ? "#4CAF50" : "#999",
  strokeWeight: route.recommended ? 5 : 3,
});
routeLine.setMap(map);
```

---

## Hazard Markers

```js
plan.routes.forEach(route => {
  route.hazards.forEach(h => {
    new google.maps.Marker({
      position: { lat: h.hazard.latitude, lng: h.hazard.longitude },
      map: map,
      title: `${h.hazard.type}: ${h.hazard.description}`,
      icon: getHazardIcon(h.hazard.type, h.hazard.severity),
    });
  });
});
```

---

## Pitstop Markers

```js
route.pitstops.forEach(p => {
  new google.maps.Marker({
    position: { lat: p.latitude, lng: p.longitude },
    map: map,
    title: `${p.name} (${p.category})`,
  });
});
```

**Important**: `p.accessibility_info` is `null` when not available. Never show "Wheelchair accessible" unless the API actually returned it.

---

## Score Display

Each route has scores 0-100:

```json
{
  "overall": 91.5,
  "safety": 96.0,
  "accessibility": 92.0,
  "comfort": 94.0,
  "traffic": 85.0,
  "convenience": 82.0,
  "time": 78.0
}
```

Suggested display: radial chart, progress bars, or score cards. The `overall` score determines the recommended route.

---

## Error Handling

All errors return:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "request_id": "req_123"
  }
}
```

Handle HTTP status codes:
- `200` — Success
- `422` — Validation error (bad coordinates, missing fields)
- `404` — No routes found
- `502` — External service error (Google, LLM)
- `500` — Internal error

---

## Challenge Text Handling

- `challenge_text` is **optional** in `/api/routes/plan`
- If empty: balanced routing with no special constraints
- If provided: AI extracts constraints automatically
- You can also call `/api/challenges/parse` separately to preview constraints

---

## CORS

Backend allows these origins by default:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

If using a different port, update `CORS_ORIGINS` in the backend `.env`.

---

## TypeScript Types (Reference)

```typescript
interface Coordinate {
  latitude: number;
  longitude: number;
}

interface RoutePlanRequest {
  origin: Coordinate;
  destination: Coordinate;
  challenge_text?: string;
}

interface RouteScores {
  overall: number;
  safety: number;
  accessibility: number;
  comfort: number;
  traffic: number;
  convenience: number;
  time: number;
}

interface TrafficInfo {
  available: boolean;
  level: "low" | "moderate" | "high" | "severe" | null;
  delay_seconds: number | null;
  source: string;
}

interface Hazard {
  id: string;
  type: "pothole" | "roadblock" | "construction" | "unpaved_segment" | "flooded_road" | "dangerous_intersection";
  severity: "low" | "medium" | "high" | "critical";
  latitude: number;
  longitude: number;
  radius_meters: number;
  description: string;
  confidence: number;
  reported_at: string;
  status: "active" | "resolved" | "unverified";
}

interface HazardOnRoute {
  hazard: Hazard;
  distance_from_route_meters: number;
  penalty: number;
}

interface Pitstop {
  place_id: string;
  name: string;
  category: string;
  latitude: number;
  longitude: number;
  distance_from_route_meters: number;
  rating: number | null;
  accessibility_info: string | null;
  source: string;
}

interface RouteCandidate {
  route_id: string;
  label: string;
  recommended: boolean;
  distance_meters: number;
  duration_seconds: number;
  traffic: TrafficInfo;
  scores: RouteScores;
  hazards: HazardOnRoute[];
  pitstops: Pitstop[];
  advantages: string[];
  disadvantages: string[];
  warnings: string[];
  polyline: string;
}

interface Recommendation {
  route_id: string;
  reason: string;
}

interface ResponseMetadata {
  routing_source: string;
  traffic_source: string;
  places_source: string;
  hazard_source: string;
  parser_source: string;
}

interface RoutePlanResponse {
  request_id: string;
  challenge: {
    raw_text: string;
    parsed_constraints: Record<string, any>;
  };
  recommendation: Recommendation | null;
  routes: RouteCandidate[];
  metadata: ResponseMetadata;
}
```
