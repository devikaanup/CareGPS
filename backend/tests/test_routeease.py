"""
Comprehensive tests for RouteEase backend.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.schemas.challenges import ChallengeRequest, RoutePlanRequest
from app.schemas.constraints import (
    ConstraintProfile,
    DrivingExperience,
    MobilityLevel,
    Priority,
)

# ── Schema tests ──
from app.schemas.coordinates import Coordinate
from app.schemas.hazards import (
    Hazard,
    HazardOnRoute,
    HazardSeverity,
    HazardStatus,
    HazardType,
)
from app.schemas.routes import (
    RouteScores,
    TrafficInfo,
)
from app.services.hazards.service import (
    HazardAnalysisService,
    _haversine_meters,
)

# ── Service tests ──
from app.services.llm.service import fallback_parse
from app.services.routing.demo import generate_demo_response
from app.services.scoring.service import (
    RouteScoringService,
    ScoringWeights,
    adjust_weights_for_profile,
)

# ====================================================================
# COORDINATE VALIDATION
# ====================================================================

class TestCoordinateValidation:
    def test_valid_coordinate(self):
        c = Coordinate(latitude=13.0827, longitude=80.2707)
        assert c.latitude == 13.0827
        assert c.longitude == 80.2707

    def test_boundary_coordinates(self):
        c = Coordinate(latitude=90.0, longitude=180.0)
        assert c.latitude == 90.0
        c = Coordinate(latitude=-90.0, longitude=-180.0)
        assert c.latitude == -90.0

    def test_invalid_latitude_too_high(self):
        with pytest.raises(PydanticValidationError):
            Coordinate(latitude=91.0, longitude=80.0)

    def test_invalid_latitude_too_low(self):
        with pytest.raises(PydanticValidationError):
            Coordinate(latitude=-91.0, longitude=80.0)

    def test_invalid_longitude_too_high(self):
        with pytest.raises(PydanticValidationError):
            Coordinate(latitude=13.0, longitude=181.0)

    def test_invalid_longitude_too_low(self):
        with pytest.raises(PydanticValidationError):
            Coordinate(latitude=13.0, longitude=-181.0)


# ====================================================================
# CHALLENGE VALIDATION
# ====================================================================

class TestChallengeValidation:
    def test_valid_challenge(self):
        c = ChallengeRequest(challenge_text="I'm a new driver")
        assert c.challenge_text == "I'm a new driver"

    def test_empty_challenge_rejected(self):
        with pytest.raises(PydanticValidationError):
            ChallengeRequest(challenge_text="")

    def test_whitespace_challenge_rejected(self):
        with pytest.raises(PydanticValidationError):
            ChallengeRequest(challenge_text="   ")

    def test_long_challenge_rejected(self):
        with pytest.raises(PydanticValidationError):
            ChallengeRequest(challenge_text="x" * 2001)


# ====================================================================
# CONSTRAINT VALIDATION
# ====================================================================

class TestConstraintProfile:
    def test_defaults(self):
        c = ConstraintProfile()
        assert c.avoid_highways is False
        assert c.mobility_level == MobilityLevel.FULL
        assert c.driving_experience == DrivingExperience.EXPERIENCED
        assert c.priority == Priority.BALANCED

    def test_no_extra_fields(self):
        with pytest.raises(PydanticValidationError):
            ConstraintProfile(made_up_field=True)  # type: ignore

    def test_confidence_range(self):
        c = ConstraintProfile(confidence=0.0)
        assert c.confidence == 0.0
        c = ConstraintProfile(confidence=1.0)
        assert c.confidence == 1.0
        with pytest.raises(PydanticValidationError):
            ConstraintProfile(confidence=1.5)
        with pytest.raises(PydanticValidationError):
            ConstraintProfile(confidence=-0.1)


# ====================================================================
# FALLBACK PARSER TESTS
# ====================================================================

class TestFallbackParser:
    def test_walker_bad_roads(self):
        """Test 1: 'I use a walker and can't handle bad roads.'"""
        result = fallback_parse("I use a walker and can't handle bad roads.")
        assert result.mobility_level == MobilityLevel.LIMITED
        assert result.avoid_unpaved is True
        assert result.avoid_potholes is True
        assert result.priority == Priority.ACCESSIBILITY

    def test_new_driver_highways(self):
        """Test 2: 'I'm a new driver and highways make me nervous.'"""
        result = fallback_parse("I'm a new driver and highways make me nervous.")
        assert result.driving_experience == DrivingExperience.LEARNER
        assert result.avoid_highways is True
        assert result.avoid_heavy_merges is True

    def test_elderly_calm_rest(self):
        """Test 3: 'I'm elderly and want calmer roads with somewhere to rest.'"""
        result = fallback_parse("I'm elderly and want calmer roads with somewhere to rest.")
        assert result.avoid_high_traffic is True
        assert result.needs_rest_stops is True

    def test_pharmacy_needed(self):
        """Test 4: 'I need a pharmacy on the way.'"""
        result = fallback_parse("I need a pharmacy on the way.")
        assert result.needs_pharmacy is True

    def test_speed_priority(self):
        """Test 5: 'I want to get there as quickly as possible.'"""
        result = fallback_parse("I want to get there as quickly as possible.")
        assert result.priority == Priority.SPEED

    def test_roundabouts(self):
        """Test 6: 'I don't like complicated roundabouts.'"""
        result = fallback_parse("I don't like complicated roundabouts.")
        assert result.avoid_roundabouts is True

    def test_wheelchair(self):
        result = fallback_parse("I use a wheelchair and need accessible routes.")
        assert result.mobility_level == MobilityLevel.WHEELCHAIR
        assert result.avoid_unpaved is True
        assert result.needs_accessible_restrooms is True

    def test_night_vision(self):
        result = fallback_parse("I can't see well at night and avoid dark roads.")
        assert result.vision_sensitivity is True
        assert result.avoid_unlit_roads is True

    def test_empty_text(self):
        """Empty text should produce default constraints."""
        result = fallback_parse("")
        assert result.priority == Priority.BALANCED
        assert result.confidence == 0.3

    def test_no_overinterpretation(self):
        """'I'm elderly' should NOT automatically mean wheelchair/blind/medical."""
        result = fallback_parse("I'm elderly.")
        assert result.mobility_level == MobilityLevel.FULL  # Not automatically limited
        assert result.needs_pharmacy is False
        assert result.needs_hospital is False
        assert result.vision_sensitivity is False


# ====================================================================
# HAZARD PROXIMITY TESTS
# ====================================================================

class TestHazardProximity:
    def test_haversine_same_point(self):
        d = _haversine_meters(13.0827, 80.2707, 13.0827, 80.2707)
        assert d == 0.0

    def test_haversine_known_distance(self):
        """Chennai Central to Egmore: roughly 1.5 km"""
        d = _haversine_meters(13.0827, 80.2707, 13.0732, 80.2609)
        assert 1000 < d < 2000

    def test_hazard_near_route(self):
        """Hazard very close to route point should be detected."""
        service = HazardAnalysisService()
        # Route passes right through a known hazard location
        route = [(13.0580, 80.2490)]  # HZ-001 location
        results = service.analyze_route(route, proximity_threshold_meters=50)
        assert len(results) >= 1
        assert any(h.hazard.id == "HZ-001" for h in results)

    def test_hazard_far_from_route(self):
        """Route far from hazards should have no detections."""
        service = HazardAnalysisService()
        # Location far from any hazard
        route = [(12.9000, 80.1000)]
        results = service.analyze_route(route, proximity_threshold_meters=50)
        assert len(results) == 0

    def test_hazard_penalty_applied(self):
        """Detected hazards should have non-zero penalties."""
        service = HazardAnalysisService()
        route = [(13.0580, 80.2490)]
        results = service.analyze_route(route)
        for h in results:
            assert h.penalty > 0


# ====================================================================
# HAZARD HARD CONSTRAINT TESTS
# ====================================================================

class TestHardConstraints:
    def test_roadblock_violation(self):
        """TEST 2: Active roadblock with avoid_roadblocks=True."""
        service = HazardAnalysisService()
        hazard = HazardOnRoute(
            hazard=Hazard(
                id="HZ-003",
                type=HazardType.ROADBLOCK,
                severity=HazardSeverity.CRITICAL,
                latitude=13.0650,
                longitude=80.2580,
                radius_meters=100,
                description="Road closed",
                confidence=0.98,
                status=HazardStatus.ACTIVE,
            ),
            distance_from_route_meters=25.0,
            penalty=49.0,
        )
        violated, reasons = service.has_hard_constraint_violation(
            [hazard], avoid_roadblocks=True
        )
        assert violated is True
        assert len(reasons) >= 1

    def test_roadblock_no_constraint(self):
        """Roadblock present but not avoided — no violation."""
        service = HazardAnalysisService()
        hazard = HazardOnRoute(
            hazard=Hazard(
                id="HZ-003",
                type=HazardType.ROADBLOCK,
                severity=HazardSeverity.CRITICAL,
                latitude=13.0650,
                longitude=80.2580,
                radius_meters=100,
                description="Road closed",
                confidence=0.98,
                status=HazardStatus.ACTIVE,
            ),
            distance_from_route_meters=25.0,
            penalty=49.0,
        )
        violated, _reasons = service.has_hard_constraint_violation(
            [hazard], avoid_roadblocks=False
        )
        assert violated is False

    def test_unpaved_violation(self):
        service = HazardAnalysisService()
        hazard = HazardOnRoute(
            hazard=Hazard(
                id="HZ-005",
                type=HazardType.UNPAVED_SEGMENT,
                severity=HazardSeverity.MEDIUM,
                latitude=13.0550,
                longitude=80.2300,
                radius_meters=80,
                description="Unpaved road",
                confidence=0.72,
                status=HazardStatus.ACTIVE,
            ),
            distance_from_route_meters=15.0,
            penalty=5.76,
        )
        violated, _ = service.has_hard_constraint_violation(
            [hazard], avoid_unpaved=True
        )
        assert violated is True


# ====================================================================
# SCORING TESTS
# ====================================================================

class TestScoring:
    def setup_method(self):
        self.scorer = RouteScoringService()

    def test_scoring_weights_sum_to_one(self):
        w = ScoringWeights()
        w.validate()  # Should not raise

    def test_learner_weights_emphasize_safety(self):
        constraints = ConstraintProfile(
            driving_experience=DrivingExperience.LEARNER,
            priority=Priority.SAFETY,
        )
        w = adjust_weights_for_profile(constraints)
        assert w.safety >= 0.30

    def test_speed_weights_emphasize_time(self):
        constraints = ConstraintProfile(priority=Priority.SPEED)
        w = adjust_weights_for_profile(constraints)
        assert w.time >= 0.30

    def test_route_with_hazards_scores_lower(self):
        """TEST 3: Route with potholes should score lower on safety/accessibility."""
        constraints = ConstraintProfile(
            mobility_level=MobilityLevel.LIMITED,
            avoid_potholes=True,
        )
        hazard = HazardOnRoute(
            hazard=Hazard(
                id="HZ-001",
                type=HazardType.POTHOLE,
                severity=HazardSeverity.HIGH,
                latitude=13.0580,
                longitude=80.2490,
                radius_meters=35,
                description="Large pothole",
                confidence=0.91,
                status=HazardStatus.ACTIVE,
            ),
            distance_from_route_meters=12.3,
            penalty=13.65,
        )

        # Route WITH potholes
        scores_bad = self.scorer.score_route(
            constraints=constraints,
            duration_seconds=1400,
            distance_meters=8000,
            min_duration=1380,
            max_duration=1620,
            hazards=[hazard, hazard],
            traffic_delay_seconds=100,
            traffic_available=True,
            has_highway=False,
            pitstop_count=0,
            pitstop_needed=False,
        )

        # Route WITHOUT potholes
        scores_good = self.scorer.score_route(
            constraints=constraints,
            duration_seconds=1600,
            distance_meters=9000,
            min_duration=1380,
            max_duration=1620,
            hazards=[],
            traffic_delay_seconds=50,
            traffic_available=True,
            has_highway=False,
            pitstop_count=0,
            pitstop_needed=False,
        )

        assert scores_good.safety > scores_bad.safety
        assert scores_good.accessibility > scores_bad.accessibility

    def test_learner_route_ranking(self):
        """TEST 1 — LEARNER: Route B (no highway) should be recommended over A (highway)."""
        constraints = ConstraintProfile(
            driving_experience=DrivingExperience.LEARNER,
            avoid_highways=True,
            avoid_heavy_merges=True,
            priority=Priority.SAFETY,
        )

        # Route A: faster, highway
        score_a = self.scorer.score_route(
            constraints=constraints,
            duration_seconds=1380,
            distance_meters=8200,
            min_duration=1380,
            max_duration=1620,
            hazards=[],
            traffic_delay_seconds=200,
            traffic_available=True,
            has_highway=True,
            pitstop_count=0,
            pitstop_needed=False,
        )

        # Route B: slower, no highway
        score_b = self.scorer.score_route(
            constraints=constraints,
            duration_seconds=1620,
            distance_meters=9100,
            min_duration=1380,
            max_duration=1620,
            hazards=[],
            traffic_delay_seconds=50,
            traffic_available=True,
            has_highway=False,
            pitstop_count=0,
            pitstop_needed=False,
        )

        assert score_b.overall > score_a.overall, (
            f"Route B (no highway, overall={score_b.overall}) should beat "
            f"Route A (highway, overall={score_a.overall}) for learner"
        )

    def test_speed_time_weight(self):
        """TEST 4: Speed priority should increase time weight."""
        constraints = ConstraintProfile(priority=Priority.SPEED)
        w = adjust_weights_for_profile(constraints)
        assert w.time >= 0.30

    def test_rest_stop_detection(self):
        """TEST 5: 'I need somewhere to stop and rest' → needs_rest_stops=True."""
        result = fallback_parse("I need somewhere to stop and rest.")
        assert result.needs_rest_stops is True

    def test_scores_within_range(self):
        """All scores must be 0-100."""
        constraints = ConstraintProfile()
        scores = self.scorer.score_route(
            constraints=constraints,
            duration_seconds=1500,
            distance_meters=8500,
            min_duration=1380,
            max_duration=1620,
            hazards=[],
            traffic_delay_seconds=100,
            traffic_available=True,
            has_highway=False,
            pitstop_count=1,
            pitstop_needed=True,
        )
        for field in ["overall", "safety", "accessibility", "comfort", "traffic", "convenience", "time"]:
            val = getattr(scores, field)
            assert 0 <= val <= 100, f"{field}={val} out of range"

    def test_advantage_disadvantage_generation(self):
        """Explainability: advantages/disadvantages should be generated from data."""
        constraints = ConstraintProfile(avoid_highways=True)
        advantages, disadvantages, _warnings = self.scorer.generate_advantages_disadvantages(
            constraints=constraints,
            hazards=[],
            duration_seconds=1620,
            min_duration=1380,
            traffic_delay=50,
            traffic_available=True,
            has_highway=False,
            pitstop_count=1,
            is_fastest=False,
        )
        assert "Avoids highways" in advantages
        assert any("slower" in d.lower() for d in disadvantages)


# ====================================================================
# DEMO ENDPOINT TEST
# ====================================================================

class TestDemoResponse:
    def test_demo_generates_valid_response(self):
        """Demo response must be valid according to our schema."""
        response = generate_demo_response()
        assert response.request_id == "demo_req_001"
        assert len(response.routes) == 3
        assert response.recommendation is not None
        assert response.recommendation.route_id == "route_002"
        assert response.metadata.hazard_source == "demo"

    def test_demo_recommended_route_has_highest_score(self):
        response = generate_demo_response()
        recommended = next(r for r in response.routes if r.recommended)
        for other in response.routes:
            if not other.recommended:
                assert recommended.scores.overall >= other.scores.overall

    def test_demo_labels(self):
        response = generate_demo_response()
        labels = [r.label for r in response.routes]
        assert "Recommended" in labels
        assert "Fastest" in labels

    def test_demo_metadata_honesty(self):
        """All demo metadata should say 'demo'."""
        response = generate_demo_response()
        assert response.metadata.routing_source == "demo"
        assert response.metadata.traffic_source == "demo"
        assert response.metadata.hazard_source == "demo"
        assert response.metadata.parser_source == "demo"


# ====================================================================
# API SCHEMA TESTS
# ====================================================================

class TestAPISchemas:
    def test_route_plan_request_valid(self):
        req = RoutePlanRequest(
            origin=Coordinate(latitude=13.0827, longitude=80.2707),
            destination=Coordinate(latitude=13.0674, longitude=80.2376),
            challenge_text="I'm a new driver.",
        )
        assert req.origin.latitude == 13.0827

    def test_route_plan_request_empty_challenge(self):
        """Empty challenge_text is allowed (defaults to balanced routing)."""
        req = RoutePlanRequest(
            origin=Coordinate(latitude=13.0827, longitude=80.2707),
            destination=Coordinate(latitude=13.0674, longitude=80.2376),
        )
        assert req.challenge_text == ""

    def test_route_plan_request_invalid_origin(self):
        with pytest.raises(PydanticValidationError):
            RoutePlanRequest(
                origin=Coordinate(latitude=999, longitude=80.2707),
                destination=Coordinate(latitude=13.0674, longitude=80.2376),
            )

    def test_traffic_info_defaults(self):
        t = TrafficInfo()
        assert t.available is False
        assert t.level is None
        assert t.source == "unavailable"

    def test_route_scores_validation(self):
        s = RouteScores(overall=85, safety=90, accessibility=80, comfort=85, traffic=75, convenience=70, time=65)
        assert s.overall == 85

        with pytest.raises(PydanticValidationError):
            RouteScores(overall=101, safety=90, accessibility=80, comfort=85, traffic=75, convenience=70, time=65)


# ====================================================================
# INTEGRATION TEST
# ====================================================================

class TestIntegration:
    def test_full_demo_pipeline(self):
        """
        End-to-end: challenge → constraints → routes → hazards → scoring → ranking → recommendation.
        Uses demo data (no external services required).
        """
        # Step 1: Parse challenge
        challenge = "I'm a new driver and highways make me nervous."
        constraints = fallback_parse(challenge)

        assert constraints.driving_experience == DrivingExperience.LEARNER
        assert constraints.avoid_highways is True

        # Step 2: Generate demo response (simulates full pipeline with demo data)
        response = generate_demo_response(challenge, constraints)

        # Step 3: Verify response structure
        assert response.request_id is not None
        assert response.challenge.raw_text == challenge
        assert response.recommendation is not None
        assert len(response.routes) >= 2

        # Step 4: Verify recommended route
        recommended = [r for r in response.routes if r.recommended]
        assert len(recommended) == 1
        rec = recommended[0]

        # Step 5: Verify scoring makes sense
        _fastest = min(response.routes, key=lambda r: r.duration_seconds)
        assert rec.scores.overall >= 80  # Recommended should score well
        assert rec.route_id == response.recommendation.route_id

        # Step 6: Verify metadata honesty
        assert response.metadata.hazard_source == "demo"

        # Step 7: Verify explainability
        assert len(rec.advantages) > 0
        assert response.recommendation.reason != ""

    def test_hazard_to_scoring_integration(self):
        """Verify hazard analysis feeds correctly into scoring."""
        service = HazardAnalysisService()
        scorer = RouteScoringService()

        # Route through known hazard area
        route_bad = [(13.0580, 80.2490), (13.0600, 80.2500)]
        hazards_bad = service.analyze_route(route_bad)

        # Route through clear area
        route_good = [(12.9000, 80.1000), (12.9100, 80.1100)]
        hazards_good = service.analyze_route(route_good)

        constraints = ConstraintProfile(avoid_potholes=True, mobility_level=MobilityLevel.LIMITED)

        score_bad = scorer.score_route(
            constraints=constraints,
            duration_seconds=1500,
            distance_meters=8500,
            min_duration=1380,
            max_duration=1620,
            hazards=hazards_bad,
            traffic_delay_seconds=100,
            traffic_available=True,
            has_highway=False,
        )

        score_good = scorer.score_route(
            constraints=constraints,
            duration_seconds=1600,
            distance_meters=9000,
            min_duration=1380,
            max_duration=1620,
            hazards=hazards_good,
            traffic_delay_seconds=100,
            traffic_available=True,
            has_highway=False,
        )

        assert score_good.safety >= score_bad.safety, "Clear route should have better safety"
