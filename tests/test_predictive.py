"""Unit tests for Predictive Pacing Engine."""

import pytest
from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.dialer.predictive import PredictivePacingEngine


@pytest.fixture
def predictive_db(tmp_path):
    db_file = str(tmp_path / "test_predictive.db")
    init_db(db_file)
    with get_db(db_file) as conn:
        with transaction(conn) as cursor:
            cursor.execute("INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode) VALUES ('CMP_PRED', 'Predictive Camp', 'PREDICTIVE')")
            # 10 available agents
            for i in range(10):
                cursor.execute(f"INSERT INTO agents (agent_id, agent_name, status) VALUES ('AGT_A_{i}', 'Agent {i}', 'AVAILABLE')")
            # 100 queued leads
            for i in range(100):
                cursor.execute(f"INSERT INTO borrowers (borrower_id, name, phone) VALUES ('BRW_P_{i}', 'Borrower {i}', '90000000{i:02d}')")
                cursor.execute(f"INSERT INTO campaign_borrower_queue (campaign_id, borrower_id, status) VALUES ('CMP_PRED', 'BRW_P_{i}', 'QUEUED')")
    yield db_file


def test_predictive_pacing_multiplier_by_answer_rate(predictive_db):
    """
    Test that lower answer rates generate higher call proposals,
    and higher answer rates generate lower, conservative proposals.
    """
    with get_db(predictive_db) as conn:
        # At 20% answer rate: proposed calls should be around 10 / 0.19 ~ 50 calls
        res_20 = PredictivePacingEngine.calculate_calls_to_dial(
            conn, "CMP_PRED", custom_answer_rate=0.20, custom_failure_rate=0.05
        )
        # At 70% answer rate: proposed calls should be around 10 / 0.665 ~ 15 calls
        res_70 = PredictivePacingEngine.calculate_calls_to_dial(
            conn, "CMP_PRED", custom_answer_rate=0.70, custom_failure_rate=0.05
        )

        assert res_20["proposed_calls"] > res_70["proposed_calls"]
        assert res_20["proposed_calls"] >= 40
        assert res_70["proposed_calls"] <= 20


def test_predictive_hazard_rate_connected_agents(predictive_db):
    """Test that connected agents nearing completion increase projected capacity."""
    with get_db(predictive_db) as conn:
        with transaction(conn) as cursor:
            # Move 10 agents to CONNECTED
            for i in range(10):
                cursor.execute(f"INSERT INTO agents (agent_id, agent_name, status) VALUES ('AGT_CONN_{i}', 'Conn {i}', 'CONNECTED')")

        res = PredictivePacingEngine.calculate_calls_to_dial(
            conn, "CMP_PRED", custom_answer_rate=0.50, custom_talk_time=50.0
        )
        # Expected free agents = 10 * (5s setup / 50s talk) = 1.0 agent
        assert res["connected_agents"] == 10
        assert res["expected_free_agents"] > 0.0
        assert res["projected_capacity"] > res["available_agents"]


def test_predictive_in_flight_dampening(predictive_db):
    """Test that active in-flight calls dampen newly proposed calls."""
    with get_db(predictive_db) as conn:
        # Before in-flight calls
        res_before = PredictivePacingEngine.calculate_calls_to_dial(conn, "CMP_PRED", custom_answer_rate=0.50)

        # Inject 10 in-flight RINGING calls
        with transaction(conn) as cursor:
            for i in range(10):
                cursor.execute(
                    f"INSERT INTO calls (call_id, campaign_id, borrower_id, call_status) VALUES ('CALL_INF_{i}', 'CMP_PRED', 'BRW_P_{i}', 'RINGING')"
                )

        res_after = PredictivePacingEngine.calculate_calls_to_dial(conn, "CMP_PRED", custom_answer_rate=0.50)
        assert res_after["in_flight_calls"] == 10
        assert res_after["proposed_calls"] < res_before["proposed_calls"]
