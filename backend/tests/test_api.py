"""
HTTP API integration tests using FastAPI TestClient.
Tests actual endpoint responses, not just business logic.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestChallengeEndpoint:
    def test_parse_new_driver(self):
        resp = client.post(
            "/api/challenges/parse",
            json={"challenge_text": "I'm a new driver and highways make me nervous."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["parsed_constraints"]["avoid_highways"] is True
        assert data["parsed_constraints"]["driving_experience"] == "learner"
        assert data["parser_source"] in ("fallback", "ollama", "lmstudio")

    def test_parse_empty_rejected(self):
        resp = client.post(
            "/api/challenges/parse",
            json={"challenge_text": ""},
        )
        assert resp.status_code == 422

    def test_parse_missing_field(self):
        resp = client.post("/api/challenges/parse", json={})
        assert resp.status_code == 422


class TestRoutePlanEndpoint:
    def test_plan_route_demo_fallback(self):
        """Without Google creds, should return demo response."""
        resp = client.post(
            "/api/routes/plan",
            json={
                "origin": {"latitude": 13.0827, "longitude": 80.2707},
                "destination": {"latitude": 13.0674, "longitude": 80.2376},
                "challenge_text": "I'm a new driver.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "request_id" in data
        assert "routes" in data
        assert len(data["routes"]) >= 1
        assert "recommendation" in data
        assert data["metadata"]["hazard_source"] == "demo"

    def test_plan_invalid_coords(self):
        resp = client.post(
            "/api/routes/plan",
            json={
                "origin": {"latitude": 999, "longitude": 80.2707},
                "destination": {"latitude": 13.0674, "longitude": 80.2376},
            },
        )
        assert resp.status_code == 422

    def test_plan_empty_challenge_allowed(self):
        resp = client.post(
            "/api/routes/plan",
            json={
                "origin": {"latitude": 13.0827, "longitude": 80.2707},
                "destination": {"latitude": 13.0674, "longitude": 80.2376},
            },
        )
        assert resp.status_code == 200


class TestHazardEndpoints:
    def test_get_hazards(self):
        resp = client.get("/api/hazards")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_hazards_demo(self):
        resp = client.get("/api/hazards/demo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["hazard_source"] == "demo"
        assert data["count"] > 0


class TestPitstopEndpoint:
    def test_search_pitstops_demo(self):
        resp = client.post(
            "/api/pitstops/search",
            json={
                "latitude": 13.0750,
                "longitude": 80.2500,
                "categories": ["pharmacy"],
                "radius_meters": 1000,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "pitstops" in data
        assert data["places_source"] in ("demo", "google")


class TestDemoEndpoint:
    def test_demo_returns_complete_response(self):
        resp = client.get("/api/demo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["request_id"] == "demo_req_001"
        assert len(data["routes"]) == 3
        assert data["recommendation"]["route_id"] == "route_002"
        assert data["metadata"]["hazard_source"] == "demo"

        # Verify route structure
        route = data["routes"][0]
        assert "scores" in route
        assert "traffic" in route
        assert "hazards" in route
        assert "advantages" in route
        assert "polyline" in route


class TestOpenAPIDocs:
    def test_docs_accessible(self):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_json(self):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["info"]["title"] == "RouteEase API"
