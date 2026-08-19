# RouteEase API Documentation

> **Version**: 1.0.0  
> **Base URL**: `http://localhost:8000`  
> **Interactive Docs**: `http://localhost:8000/docs`

---

## Overview

RouteEase provides navigation that considers user-specific challenges (disabilities, elderly needs, learner drivers) rather than just optimizing for speed.

**Core flow:**
```
Natural Language Challenge → AI Constraint Extraction → Route Candidates → Hazard Analysis → Scoring → Explainable Recommendation
```

---

## Endpoints

### `GET /health`

Health check.

**Response**: `200 OK`
```json
{"status": "ok"}
```

---

### `POST /api/challenges/parse`

Parse a natural-language challenge into structured constraints.

**Request**:
```json
{
  "challenge_text": "I'm a new driver and highways make me nervous."
}
```

**Response** (`200`):
```json
{
  "raw_text": "I'm a new driver and highways make me nervous.",
  "parsed_constraints": {
    "avoid_highways": true,
    "avoid_tolls": false,
    "avoid_ferries": false,
    "avoid_unpaved": false,
    "avoid_potholes": false,
    "avoid_roadblocks": false,
    "avoid_complex_intersections": true,
    "avoid_roundabouts": false,
    "avoid_heavy_merges": true,
    "avoid_high_traffic": false,
    "avoid_unlit_roads": false,
    "needs_rest_stops": false,
    "needs_accessible_restrooms": false,
    "needs_pharmacy": false,
    "needs_hospital": false,
    "needs_fuel": false,
    "needs_ev_charging": false,
    "mobility_level": "full",
    "driving_experience": "learner",
    "vision_sensitivity": false,
    "priority": "safety",
    "confidence": 0.6,
    "reasoning_summary": "Fallback parser extracted from: ..."
  },
  "parser_source": "fallback"
}
```

**curl**:
```bash
curl -X POST http://localhost:8000/api/challenges/parse \
  -H "Content-Type: application/json" \
  -d '{"challenge_text": "I use a walker and cant handle bad roads."}'
```

---

### `POST /api/routes/plan`

Full route planning pipeline. This is the primary endpoint.

**Request**:
```json
{
  "origin": {"latitude": 13.0827, "longitude": 80.2707},
  "destination": {"latitude": 13.0674, "longitude": 80.2376},
  "challenge_text": "I'm a new driver and highways make me nervous."
}
```

- `challenge_text` is optional. If empty, default balanced routing is used.

**Response** (`200`):
```json
{
  "request_id": "req_abc123",
  "challenge": {
    "raw_text": "...",
    "parsed_constraints": { ... }
  },
  "recommendation": {
    "route_id": "route_002",
    "reason": "Avoids highways and difficult merges while adding only 4 minutes."
  },
  "routes": [
    {
      "route_id": "route_001",
      "label": "Fastest",
      "recommended": false,
      "distance_meters": 8200,
      "duration_seconds": 1380,
      "traffic": {
        "available": true,
        "level": "high",
        "delay_seconds": 360,
        "source": "demo"
      },
      "scores": {
        "overall": 58.2,
        "safety": 52.0,
        "accessibility": 65.0,
        "comfort": 45.0,
        "traffic": 60.0,
        "convenience": 70.0,
        "time": 95.0
      },
      "hazards": [
        {
          "hazard": {
            "id": "HZ-001",
            "type": "pothole",
            "severity": "high",
            "latitude": 13.058,
            "longitude": 80.249,
            "radius_meters": 35,
            "description": "Large pothole on Inner Ring Road",
            "confidence": 0.91,
            "reported_at": "2026-08-18T10:30:00Z",
            "status": "active"
          },
          "distance_from_route_meters": 12.3,
          "penalty": 13.65
        }
      ],
      "pitstops": [],
      "advantages": ["Fastest route"],
      "disadvantages": ["Route includes highway segment(s)", "2 pothole report(s)"],
      "warnings": [],
      "polyline": "m~nAa`x~M..."
    }
  ],
  "metadata": {
    "routing_source": "google",
    "traffic_source": "google",
    "places_source": "google",
    "hazard_source": "demo",
    "parser_source": "fallback"
  }
}
```

**curl**:
```bash
curl -X POST http://localhost:8000/api/routes/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"latitude": 13.0827, "longitude": 80.2707},
    "destination": {"latitude": 13.0674, "longitude": 80.2376},
    "challenge_text": "I am a new driver and highways make me nervous."
  }'
```

---

### `GET /api/hazards`

Get all active hazards.

**Response** (`200`):
```json
[
  {
    "id": "HZ-001",
    "type": "pothole",
    "severity": "high",
    "latitude": 13.058,
    "longitude": 80.249,
    "radius_meters": 35,
    "description": "Large pothole on Inner Ring Road near Kotturpuram",
    "confidence": 0.91,
    "reported_at": "2026-08-18T10:30:00Z",
    "status": "active"
  }
]
```

---

### `GET /api/hazards/demo`

Get all hazards with source metadata.

**Response** (`200`):
```json
{
  "hazard_source": "demo",
  "description": "Seeded demonstration data for Chennai area. NOT live sensor data.",
  "count": 10,
  "hazards": [ ... ]
}
```

---

### `POST /api/pitstops/search`

Search for pitstops near a location.

**Request**:
```json
{
  "latitude": 13.075,
  "longitude": 80.250,
  "categories": ["pharmacy", "cafe"],
  "radius_meters": 1000
}
```

**Categories**: `restroom`, `pharmacy`, `hospital`, `fuel`, `ev_charging`, `cafe`, `rest_area`

**Response** (`200`):
```json
{
  "places_source": "google",
  "pitstops": [
    {
      "place_id": "ChIJ...",
      "name": "Apollo Pharmacy",
      "category": "pharmacy",
      "latitude": 13.074,
      "longitude": 80.252,
      "distance_from_route_meters": 0,
      "rating": 4.0,
      "accessibility_info": null,
      "source": "google"
    }
  ]
}
```

---

### `GET /api/demo`

Returns a complete demo response without requiring any external services. Use this for frontend development.

---

## Error Format

All errors follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Latitude must be between -90 and 90",
    "request_id": "req_123"
  }
}
```

**Error codes**:
| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid request data |
| `ROUTE_NOT_FOUND` | No routes found |
| `GOOGLE_API_ERROR` | Google API failure |
| `PLACES_API_ERROR` | Google Places failure |
| `LLM_ERROR` | LLM provider failure |
| `LLM_INVALID_RESPONSE` | LLM returned invalid data |
| `CONFIGURATION_ERROR` | Missing configuration |
| `INTERNAL_ERROR` | Unexpected server error |

---

## Data Types

### Coordinate
```json
{"latitude": 13.0827, "longitude": 80.2707}
```
Latitude: -90 to 90. Longitude: -180 to 180.

### RouteScores
All scores are 0-100 (higher = better).
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

### TrafficInfo
```json
{
  "available": true,
  "level": "moderate",
  "delay_seconds": 120,
  "source": "google"
}
```
Level values: `low`, `moderate`, `high`, `severe`, `null` (unknown).

### Hazard Types
`pothole`, `roadblock`, `construction`, `unpaved_segment`, `flooded_road`, `dangerous_intersection`

### Hazard Severity
`low`, `medium`, `high`, `critical`

### Constraint Profile Enums

**mobility_level**: `full`, `moderate`, `limited`, `wheelchair`  
**driving_experience**: `learner`, `beginner`, `intermediate`, `experienced`  
**priority**: `safety`, `accessibility`, `comfort`, `speed`, `balanced`

---

## Metadata

Every response includes a `metadata` object indicating data sources:

```json
{
  "routing_source": "google",     // google | demo
  "traffic_source": "google",     // google | demo | unavailable
  "places_source": "google",      // google | demo | unavailable | not_needed
  "hazard_source": "demo",        // demo | community (always demo in MVP)
  "parser_source": "fallback"     // ollama | openai | fallback | demo
}
```

**Never trust data blindly.** Check `metadata` to know what's real vs demo.
