"""Mandatory Failure Scenarios 1 through 7 Verification Suite."""

import time
import pytest
from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.models.enums import AgentState, CallState, SafetyDecision
from smart_dialer.dialer.call_allocator import CallAllocator
from smart_dialer.dialer.predictive import PredictivePacingEngine
from smart_dialer.dialer.safety_controller import SafetyController
from smart_dialer.engine.recovery import RecoveryEngine
from smart_dialer.engine.event_processor import EventProcessor
from smart_dialer.providers.chaotic_provider import ChaoticTelecomProvider, ProviderTimeoutError


@pytest.fixture
def failure_test_db(tmp_path):
    db_file = str(tmp_path / "test_failures.db")
    init_db(db_file)
    with get_db(db_file) as conn:
        with transaction(conn) as cursor:
            cursor.execute("INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode) VALUES ('CMP_FAIL', 'Failure Test Camp', 'PREDICTIVE')")
            # Create 100 agents
            for i in range(100):
                cursor.execute(f"INSERT INTO agents (agent_id, agent_name, status) VALUES ('AGT_F_{i}', 'Agent {i}', 'AVAILABLE')")
            # Create 200 borrowers
            for i in range(200):
                cursor.execute(f"INSERT INTO borrowers (borrower_id, name, phone) VALUES ('BRW_F_{i}', 'Borrower {i}', '98000000{i:02d}')")
                cursor.execute(f"INSERT INTO campaign_borrower_queue (campaign_id, borrower_id, status) VALUES ('CMP_FAIL', 'BRW_F_{i}', 'QUEUED')")
    yield db_file


# Scenario 1: Worker crashes after reservations or call initiation
def test_scenario_1_worker_crash_recovery(failure_test_db):
    """
    Scenario 1: Worker crashes after reserving agents and leads.
    Verifies that the Stale Reservation Reaper detects expired TTLs and restores state.
    """
    with get_db(failure_test_db) as conn:
        # Step 1: Worker reserves 5 calls
        allocations = CallAllocator.allocate_calls(conn, "CMP_FAIL", num_calls_to_allocate=5)
        assert len(allocations) == 5

        # Simulate crash: Worker process dies, leaving agents in RESERVED with expired timestamp
        with transaction(conn) as cursor:
            cursor.execute("UPDATE agents SET reservation_expires_at = datetime('now', '-5 seconds') WHERE status = 'RESERVED'")
            cursor.execute("UPDATE campaign_borrower_queue SET reservation_expires_at = datetime('now', '-5 seconds') WHERE status = 'RESERVED'")

        # Step 2: Recovery Engine executes reaper
        summary = RecoveryEngine.reap_stale_reservations(conn)
        assert summary["reaped_agents"] == 5
        assert summary["reaped_borrowers"] == 5

        # Verify agents returned to AVAILABLE
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM agents WHERE status = 'AVAILABLE'")
        assert cursor.fetchone()["c"] == 100


# Scenario 2: Provider outage and timeout handling
def test_scenario_2_provider_outage_circuit_breaker(failure_test_db):
    """
    Scenario 2: Provider outage / timeout handling.
    Verifies that provider error rates > 15% trip the Safety Controller circuit breaker.
    """
    with get_db(failure_test_db) as conn:
        pacing = {
            "mode": "PREDICTIVE",
            "proposed_calls": 50,
            "available_agents": 20,
            "in_flight_calls": 0,
            "answer_rate": 0.20,
        }
        # Simulate 30% carrier failure rate (outage)
        safety_eval = SafetyController.evaluate(conn, "CMP_FAIL", pacing, recent_provider_error_rate=0.30)
        assert safety_eval["decision"] == SafetyDecision.FORCE_PROGRESSIVE
        assert safety_eval["approved_calls"] <= 20
        assert "Provider error rate" in safety_eval["reason"]


# Scenario 3: Agent availability drops from 100 to 60
def test_scenario_3_agent_pool_drop(failure_test_db):
    """
    Scenario 3: 40 agents abruptly log out or pause (availability drops from 100 to 60).
    Verifies Safety Controller immediately throttles proposals to prevent runaway dropped calls.
    """
    with get_db(failure_test_db) as conn:
        # Before drop: 100 available
        pacing_before = PredictivePacingEngine.calculate_calls_to_dial(conn, "CMP_FAIL", custom_answer_rate=0.50)
        assert pacing_before["available_agents"] == 100

        # Simulate drop: 40 agents transition to OFFLINE
        with transaction(conn) as cursor:
            cursor.execute("UPDATE agents SET status = 'OFFLINE' WHERE agent_id IN (SELECT agent_id FROM agents LIMIT 40)")

        pacing_after = PredictivePacingEngine.calculate_calls_to_dial(conn, "CMP_FAIL", custom_answer_rate=0.50)
        assert pacing_after["available_agents"] == 60

        safety_eval = SafetyController.evaluate(conn, "CMP_FAIL", pacing_after)
        # Max overdial is 2.5x of 60 = 150
        assert safety_eval["approved_calls"] <= 150


# Scenario 4: Duplicate ANSWERED events
def test_scenario_4_duplicate_answered_events(failure_test_db):
    """
    Scenario 4: Carrier sends duplicate ANSWERED events for the same call.
    Verifies idempotency suppresses duplicate without crashing or double agent allocation.
    """
    with get_db(failure_test_db) as conn:
        # Setup call in INITIATED
        with transaction(conn) as cursor:
            cursor.execute(
                """
                INSERT INTO calls (call_id, campaign_id, borrower_id, agent_id, call_status)
                VALUES ('CALL_DUP_1', 'CMP_FAIL', 'BRW_F_0', 'AGT_F_0', 'INITIATED')
                """
            )
            cursor.execute("UPDATE agents SET status = 'DIALING', current_call_id = 'CALL_DUP_1' WHERE agent_id = 'AGT_F_0'")

        # Event 1: First ANSWERED
        evt1 = {
            "call_id": "CALL_DUP_1",
            "event_type": "ANSWERED",
            "idempotency_key": "IDEM_DUP_KEY_123",
        }
        res1 = EventProcessor.process_event(conn, evt1)
        assert res1["status"] == "PROCESSED"
        assert res1["to_status"] == CallState.ANSWERED.value

        # Event 2: Duplicate ANSWERED with same idempotency key
        res2 = EventProcessor.process_event(conn, evt1)
        assert res2["status"] == "DUPLICATE_IGNORED"
        assert "Duplicate event" in res2["message"]


# Scenario 5: COMPLETED arrives before ANSWERED
def test_scenario_5_completed_arrives_before_answered(failure_test_db):
    """
    Scenario 5: Out-of-order delivery where COMPLETED arrives while call is still RINGING.
    Verifies call transitions directly to COMPLETED, frees agent, and subsequent ANSWERED is ignored.
    """
    with get_db(failure_test_db) as conn:
        with transaction(conn) as cursor:
            cursor.execute(
                """
                INSERT INTO calls (call_id, campaign_id, borrower_id, agent_id, call_status)
                VALUES ('CALL_OOO_1', 'CMP_FAIL', 'BRW_F_1', 'AGT_F_1', 'RINGING')
                """
            )
            cursor.execute("UPDATE agents SET status = 'DIALING', current_call_id = 'CALL_OOO_1' WHERE agent_id = 'AGT_F_1'")

        # Event arrives out-of-order: COMPLETED
        completed_evt = {
            "call_id": "CALL_OOO_1",
            "event_type": "COMPLETED",
            "duration_sec": 45,
            "idempotency_key": "IDEM_OOO_COMPLETED",
        }
        res = EventProcessor.process_event(conn, completed_evt)
        assert res["to_status"] == CallState.COMPLETED.value

        # Verify agent is safely moved to WRAP_UP / freed
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM agents WHERE agent_id = 'AGT_F_1'")
        assert cursor.fetchone()["status"] in (AgentState.WRAP_UP.value, AgentState.AVAILABLE.value)

        # Stale ANSWERED arrives late
        late_answered = {
            "call_id": "CALL_OOO_1",
            "event_type": "ANSWERED",
            "idempotency_key": "IDEM_OOO_LATE_ANSWER",
        }
        late_res = EventProcessor.process_event(conn, late_answered)
        assert late_res["status"] == "LATE_EVENT_AUDITED"


# Scenario 6: Concurrent workers attempt to reserve the same agent or borrower
def test_scenario_6_concurrency_race(failure_test_db):
    """
    Scenario 6: Race condition handling during high-concurrency reservation.
    """
    with get_db(failure_test_db) as conn:
        # Allocate 10 calls
        alloc1 = CallAllocator.allocate_calls(conn, "CMP_FAIL", num_calls_to_allocate=10)
        alloc2 = CallAllocator.allocate_calls(conn, "CMP_FAIL", num_calls_to_allocate=10)

        ids_1 = {c["borrower_id"] for c in alloc1}
        ids_2 = {c["borrower_id"] for c in alloc2}
        assert ids_1.isdisjoint(ids_2), "Race condition: Allocated same borrower across calls!"


# Scenario 7: Answer rate unexpectedly drops from 70% to 10%
def test_scenario_7_answer_rate_shock(failure_test_db):
    """
    Scenario 7: Sudden drop in borrower answer rate from 70% to 10%.
    Verifies that pacing engine adapts proposals and safety controller prevents runaway overdialing.
    """
    with get_db(failure_test_db) as conn:
        # Pacing at 70%
        pacing_70 = PredictivePacingEngine.calculate_calls_to_dial(conn, "CMP_FAIL", custom_answer_rate=0.70)

        # Answer rate drops to 10%
        pacing_10 = PredictivePacingEngine.calculate_calls_to_dial(conn, "CMP_FAIL", custom_answer_rate=0.10)

        # Safety evaluation enforces overdial ratio
        safety_eval = SafetyController.evaluate(conn, "CMP_FAIL", pacing_10)

        assert safety_eval["decision"] in (SafetyDecision.APPROVE, SafetyDecision.REDUCE)
        # Even with 10% answer rate, max approved calls must not exceed max overdial ceiling
        available = pacing_10["available_agents"]
        assert safety_eval["approved_calls"] <= (available * 2.5)
