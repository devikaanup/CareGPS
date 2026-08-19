# CareGPT

> **"Routes built around you, not just the fastest route."**

Navigation for people with disabilities, elderly users, new drivers, and women. Instead of optimizing only for speed, CareGPT considers user-specific challenges to recommend the most suitable route.

---

## How It Works

1. **User describes their challenge** in natural language (e.g., "I'm a new driver and highways make me nervous")
2. **AI extracts structured constraints** (avoid highways, avoid merges, learner profile)
3. **Route candidates** are fetched from Google Routes API
4. **Hazard analysis** checks for potholes, roadblocks, unpaved roads near each route
5. **Traffic analysis** from Google's traffic-aware routing
6. **Pitstop search** finds relevant stops (pharmacies, rest areas, fuel)
7. **Deterministic scoring** evaluates safety, accessibility, comfort, traffic, convenience, time
8. **Explainable recommendation** — the best route with clear reasons WHY

---

## Project Structure

```
hackathon/
├── backend/
│   ├── app/
│   │   ├── api/routes/         # FastAPI endpoints
│   │   ├── core/               # Config, errors, logging
│   │   ├── schemas/            # Pydantic models (API contract)
│   │   ├── services/
│   │   │   ├── routing/        # Google Routes + pipeline + demo
│   │   │   ├── scoring/        # Deterministic scoring engine
│   │   │   ├── hazards/        # Hazard repository + analysis
│   │   │   ├── places/         # Google Places integration
│   │   │   ├── llm/            # LLM providers + fallback parser
│   │   │   └── traffic/        # Traffic integration
│   │   └── main.py             # FastAPI app
│   ├── data/
│   │   ├── hazards.json        # Demo hazard data (Chennai area)
│   │   └── mock_route_response.json  # Full mock response for frontend
│   ├── tests/                  # Automated tests (64 tests)
│   ├── requirements.txt
│   └── venv/
├── docs/
│   ├── API.md                  # Complete API documentation
│   ├── architecture.md         # System architecture
│   └── frontend-integration.md # Frontend developer guide
├── frontend/                   # (Built by frontend teammate)
├── .env.example
├── .gitignore
└── README.md
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+ (tested with 3.13)
- Google Maps API key (optional — demo mode works without it)
- Ollama (optional — fallback parser works without it)

### 2. Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your API keys (optional for demo mode)
```

### 3. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Verify

```bash
# Health check
curl http://localhost:8000/health

# Demo (no external services needed)
curl http://localhost:8000/api/demo

# Interactive API docs
open http://localhost:8000/docs
```

### 5. Run Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_MAPS_API_KEY` | No* | `""` | Google Maps Platform key |
| `LLM_PROVIDER` | No | `ollama` | LLM provider: ollama, openai, anthropic, gemini |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3.2` | Ollama model name |
| `OPENAI_API_KEY` | No | `""` | OpenAI key (future) |
| `ANTHROPIC_API_KEY` | No | `""` | Anthropic key (future) |
| `GEMINI_API_KEY` | No | `""` | Gemini key (future) |
| `CORS_ORIGINS` | No | `localhost:3000,5173` | Allowed CORS origins |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `DEBUG` | No | `true` | Debug mode |

*Without `GOOGLE_MAPS_API_KEY`, the backend uses demo fallback data.

---

## Google Maps Platform Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable these APIs:
   - **Routes API** (for route computation)
   - **Places API (New)** (for pitstop search)
   - **Maps JavaScript API** (for frontend map display)
4. Create an API key under **Credentials**
5. Set `GOOGLE_MAPS_API_KEY` in your `.env`

---

## Ollama Setup (Optional)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Ollama runs on http://localhost:11434 by default
```

Without Ollama, the system uses a **deterministic fallback parser** that recognizes common concepts (walker, wheelchair, new driver, highway, roundabout, pharmacy, etc.).

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/challenges/parse` | Parse challenge → constraints |
| `POST` | `/api/routes/plan` | Full route planning pipeline |
| `GET` | `/api/hazards` | Get all active hazards |
| `GET` | `/api/hazards/demo` | Get hazards with metadata |
| `POST` | `/api/pitstops/search` | Search pitstops near location |
| `GET` | `/api/demo` | Full demo response (no deps) |
| `GET` | `/docs` | Interactive OpenAPI docs |

See [docs/API.md](docs/API.md) for complete documentation.

---

## Demo Mode

The system works fully in demo mode without any external services:

- **Challenge parsing**: Uses deterministic fallback parser
- **Routes**: Returns realistic demo route data
- **Hazards**: Uses seeded Chennai-area hazard data
- **Scoring**: Full deterministic scoring engine
- **Pitstops**: Demo pitstop data

All demo data is **clearly labelled** via `metadata` fields. The system never pretends demo data is live data.

---

## Testing

64 automated tests covering:

- ✅ Coordinate validation (boundary values, invalid ranges)
- ✅ Challenge text validation (empty, blank, length limits)
- ✅ Constraint profile validation (no extra fields, enum values, confidence range)
- ✅ Fallback parser (6 required challenge texts + edge cases)
- ✅ Hazard proximity (haversine distance, detection, penalties)
- ✅ Hard constraint violations (roadblock, unpaved, pothole filtering)
- ✅ Scoring engine (weights, learner ranking, hazard impact, speed priority)
- ✅ Route ranking (learner: non-highway beats highway)
- ✅ Explainability (advantages/disadvantages from data)
- ✅ Demo response (structure, labels, metadata honesty)
- ✅ API schemas (valid/invalid requests, error handling)
- ✅ End-to-end integration (challenge → constraints → scoring → recommendation)
- ✅ HTTP API tests (all endpoints, error codes, OpenAPI docs)

---

## Limitations

- **Hazard data is seeded demo data**, not live sensor data
- **Google live routing** requires a valid API key with billing enabled
- **LLM challenge parsing** requires Ollama or equivalent provider running
- **Accessibility information** from Google Places is limited — the system never fabricates it
- **No database** — uses JSON files (architecture supports DB migration later)
- **No authentication** — MVP scope
- **No real-time tracking** — MVP scope

---

## For Frontend Developers

See [docs/frontend-integration.md](docs/frontend-integration.md) for:

- Complete TypeScript types
- Code examples for map display
- Hazard/pitstop marker setup
- Score visualization suggestions
- Error handling patterns
- CORS configuration

The mock response at `backend/data/mock_route_response.json` lets you build the UI independently.

---

## Tech Stack

- **Python 3.13** + **FastAPI** + **Pydantic v2**
- **Google Routes API** (v2) — current API
- **Google Places API (New)**
- **Ollama** + Llama models (local LLM)
- **httpx** — async HTTP client
- **pytest** — testing
- **polyline** — route polyline encoding/decoding
