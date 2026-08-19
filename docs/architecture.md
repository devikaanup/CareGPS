# RouteEase Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend (React)                      │
│              (Built by frontend teammate)                 │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP REST API
                     ▼
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend                         │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                 API Layer (Routes)                    │ │
│  │  /health  /challenges  /routes  /hazards  /pitstops │ │
│  └──────────────────┬──────────────────────────────────┘ │
│                     │                                     │
│  ┌──────────────────▼──────────────────────────────────┐ │
│  │              Route Planning Pipeline                 │ │
│  │                                                      │ │
│  │  1. Request Validation                               │ │
│  │  2. Challenge Parsing (LLM / Fallback)              │ │
│  │  3. Constraint Validation                            │ │
│  │  4. Route Generation (Google Routes API)             │ │
│  │  5. Traffic Analysis                                 │ │
│  │  6. Hazard Analysis (Proximity Engine)              │ │
│  │  7. Pitstop Search (Google Places API)              │ │
│  │  8. Hard Constraint Filter                           │ │
│  │  9. Route Scoring (Deterministic)                   │ │
│  │  10. Route Ranking & Recommendation                 │ │
│  │  11. Explainable Response                           │ │
│  └──────────────────┬──────────────────────────────────┘ │
│                     │                                     │
│  ┌────────┐  ┌─────┴─────┐  ┌──────────┐  ┌──────────┐ │
│  │ LLM    │  │ Routing   │  │ Hazard   │  │ Scoring  │ │
│  │Service │  │ Service   │  │ Service  │  │ Service  │ │
│  └───┬────┘  └─────┬─────┘  └────┬─────┘  └──────────┘ │
│      │             │              │                       │
│  ┌───▼────┐  ┌─────▼─────┐  ┌────▼─────┐  ┌──────────┐ │
│  │Ollama  │  │ Google    │  │hazards   │  │ Google   │ │
│  │Provider│  │ Routes API│  │.json     │  │ Places   │ │
│  └────────┘  └───────────┘  └──────────┘  └──────────┘ │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Service Interfaces

### LLMProvider (Abstract)
```python
class LLMProvider(ABC):
    async def generate(system_prompt, user_prompt) -> str
    def provider_name() -> str
```
Implementations: `OllamaProvider` (current), future: `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`

### HazardRepository
```python
class HazardRepository:
    def get_all(active_only=True) -> list[Hazard]
    def get_by_type(hazard_type) -> list[Hazard]
```

### HazardAnalysisService
```python
class HazardAnalysisService:
    def analyze_route(route_points, proximity_threshold) -> list[HazardOnRoute]
    def has_hard_constraint_violation(hazards, constraints) -> (bool, list[str])
```

### RouteScoringService
```python
class RouteScoringService:
    def score_route(...) -> RouteScores
    def generate_advantages_disadvantages(...) -> (list, list, list)
```

### ChallengeParserService
```python
class ChallengeParserService:
    async def parse(challenge_text) -> (ConstraintProfile, str)
```

## Data Flow

```
User Challenge Text
       │
       ▼
ChallengeParserService ──→ LLM (if available)
       │                    │
       │              ┌─────▼──────┐
       │              │ Validate   │
       │              │ JSON       │
       │              │ against    │
       │              │ Pydantic   │
       │              └─────┬──────┘
       │                    │ (fail? retry once, then fallback)
       ▼                    ▼
ConstraintProfile (strict schema)
       │
       ├── Hard constraints: avoid_highways, avoid_roadblocks, etc.
       └── Soft constraints: priority, driving_experience, mobility, etc.
       │
       ▼
Google Routes API ──→ Route Candidates
       │
       ▼
Decode Polyline ──→ Route Points
       │
       ▼
HazardAnalysisService ──→ Haversine proximity check ──→ HazardOnRoute[]
       │
       ▼
Hard Constraint Filter ──→ Remove/warn violated routes
       │
       ▼
RouteScoringService ──→ Weighted scores with profile adjustments
       │
       ▼
Rank by overall score ──→ Recommendation
       │
       ▼
Generate advantages/disadvantages (DETERMINISTIC, not LLM)
       │
       ▼
RoutePlanResponse
```

## Key Design Decisions

1. **LLM only extracts constraints** — never decides routes, traffic, or hazards
2. **Scoring is deterministic** — same inputs always produce same outputs
3. **Hard constraints are separate from soft constraints** — hard = reject/filter, soft = score penalty
4. **Explainability from data** — advantages/disadvantages generated from actual scoring signals
5. **Provider-agnostic LLM** — swap providers without changing routing logic
6. **No database** — JSON files for MVP, clean interfaces allow DB later
7. **Demo mode** — complete concept demonstration without any external dependencies
8. **Data honesty** — metadata always identifies data sources (google vs demo)
