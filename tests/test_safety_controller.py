"""Unit tests for Independent Safety Controller."""

import pytest
from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.models.enums import SafetyDecision
from smart_dialer.dialer.safety_controller import SafetyController


@pytest.fixture
def safety_db(tmp_path):
    db_file = str(tmp_path / "test_safety.db")
    init_db(db_file)
    with get_db(db_file) as conn:
        with transaction(conn) as cursor:
            cursor.execute("INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode) VALUES ('CMP_SAFE', 'Safety Camp', 'PREDICTIVE')")
    yield db_file


def test_safety_overdial_reduction(safety_db):
    """Test that Safety Controller clamps excessive proposals down to max overdial ceiling."""
    with get_db(safety_db) as conn:
        # 10 agents available, pacing engine proposes 50 calls (5.0x ratio, ceiling is 2.5x = 25 calls)
        pacing_result = {
            "mode": "PREDICTIVE",
            "proposed_calls": 50,
            "available_agents": 10,
            "expected_free_agents": 0.0,
            "in_flight_calls": 0,
            "answer_rate": 0.20,
        }
        eval_result = SafetyController.evaluate(conn, "CMP_SAFE", pacing_result)
        assert eval_result["decision"] == SafetyDecision.REDUCE
        assert eval_result["approved_calls"] == 25  # 10 * 2.5 = 25


def test_safety_provider_circuit_breaker(safety_db):
    """Test that provider error rate exceeding 15% trips circuit breaker and forces progressive fallback."""
    with get_db(safety_db) as conn:
        pacing_result = {
            "mode": "PREDICTIVE",
            "proposed_calls": 20,
            "available_agents": 10,
            "in_flight_calls": 0,
            "answer_rate": 0.20,
        }
        eval_result = SafetyController.evaluate(
            conn, "CMP_SAFE", pacing_result, recent_provider_error_rate=0.25
        )
        assert eval_result["decision"] == SafetyDecision.FORCE_PROGRESSIVE
        assert eval_result["approved_calls"] <= 10


def test_safety_quorum_enforcement(safety_db):
    """Test that available agents dropping below 2 forces progressive mode."""
    with get_db(safety_db) as conn:
        pacing_result = {
            "mode": "PREDICTIVE",
            "proposed_calls": 10,
            "available_agents": 1,
            "in_flight_calls": 2,
            "answer_rate": 0.20,
        }
        eval_result = SafetyController.evaluate(conn, "CMP_SAFE", pacing_result)
        assert eval_result["decision"] == SafetyDecision.FORCE_PROGRESSIVE
        assert eval_result["approved_calls"] <= 1


def test_safety_abandon_rate_enforcement(safety_db):
    """Test that abandon rate > 3% forces progressive mode to maintain regulatory compliance."""
    with get_db(safety_db) as conn:
        pacing_result = {
            "mode": "PREDICTIVE",
            "proposed_calls": 20,
            "available_agents": 10,
            "in_flight_calls": 0,
            "answer_rate": 0.50,
        }
        eval_result = SafetyController.evaluate(
            conn, "CMP_SAFE", pacing_result, historical_abandon_rate=0.045
        )
        assert eval_result["decision"] == SafetyDecision.FORCE_PROGRESSIVE
