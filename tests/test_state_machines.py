"""Unit tests for Agent and Call State Machines."""

import pytest
import sqlite3
from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.models.enums import AgentState, CallState
from smart_dialer.state_machines.agent_state import (
    AgentStateMachine,
    InvalidAgentStateTransitionError,
)
from smart_dialer.state_machines.call_state import (
    CallStateMachine,
    InvalidCallStateTransitionError,
)


@pytest.fixture
def test_db(tmp_path):
    """Create isolated SQLite test database."""
    db_file = str(tmp_path / "test_dialer.db")
    init_db(db_file)
    with get_db(db_file) as conn:
        with transaction(conn) as cursor:
            # Seed test agent
            cursor.execute(
                """
                INSERT INTO agents (agent_id, agent_name, status)
                VALUES ('AGT_TEST_1', 'Alice Agent', 'AVAILABLE')
                """
            )
            # Seed test campaign
            cursor.execute(
                """
                INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode)
                VALUES ('CMP_TEST', 'Test Campaign', 'PROGRESSIVE')
                """
            )
            # Seed test borrower
            cursor.execute(
                """
                INSERT INTO borrowers (borrower_id, name, phone)
                VALUES ('BRW_TEST_1', 'Bob Borrower', '9999999999')
                """
            )
            # Seed test call
            cursor.execute(
                """
                INSERT INTO calls (call_id, campaign_id, borrower_id, agent_id, call_status)
                VALUES ('CALL_TEST_1', 'CMP_TEST', 'BRW_TEST_1', 'AGT_TEST_1', 'QUEUED')
                """
            )
    yield db_file


def test_agent_valid_state_transitions(test_db):
    """Test standard legal lifecycle: AVAILABLE -> RESERVED -> DIALING -> CONNECTED -> WRAP_UP -> AVAILABLE."""
    with get_db(test_db) as conn:
        with transaction(conn):
            st1 = AgentStateMachine.transition(conn, "AGT_TEST_1", AgentState.RESERVED, reason="Reserved")
            assert st1 == AgentState.RESERVED

            st2 = AgentStateMachine.transition(conn, "AGT_TEST_1", AgentState.DIALING, reason="Dialing")
            assert st2 == AgentState.DIALING

            st3 = AgentStateMachine.transition(conn, "AGT_TEST_1", AgentState.CONNECTED, reason="Connected")
            assert st3 == AgentState.CONNECTED

            st4 = AgentStateMachine.transition(conn, "AGT_TEST_1", AgentState.WRAP_UP, reason="Wrap up")
            assert st4 == AgentState.WRAP_UP

            st5 = AgentStateMachine.transition(conn, "AGT_TEST_1", AgentState.AVAILABLE, reason="Ready")
            assert st5 == AgentState.AVAILABLE


def test_agent_illegal_state_transition(test_db):
    """Test that illegal transition raises InvalidAgentStateTransitionError."""
    with get_db(test_db) as conn:
        with transaction(conn):
            # OFFLINE directly to CONNECTED is illegal
            AgentStateMachine.transition(conn, "AGT_TEST_1", AgentState.OFFLINE)
            with pytest.raises(InvalidAgentStateTransitionError):
                AgentStateMachine.transition(conn, "AGT_TEST_1", AgentState.CONNECTED)


def test_call_valid_state_transitions(test_db):
    """Test standard call progression: QUEUED -> RESERVED -> INITIATED -> RINGING -> ANSWERED -> CONNECTED -> COMPLETED."""
    with get_db(test_db) as conn:
        with transaction(conn):
            c1 = CallStateMachine.transition(conn, "CALL_TEST_1", CallState.RESERVED)
            assert c1 == CallState.RESERVED

            c2 = CallStateMachine.transition(conn, "CALL_TEST_1", CallState.INITIATED)
            assert c2 == CallState.INITIATED

            c3 = CallStateMachine.transition(conn, "CALL_TEST_1", CallState.RINGING)
            assert c3 == CallState.RINGING

            c4 = CallStateMachine.transition(conn, "CALL_TEST_1", CallState.ANSWERED)
            assert c4 == CallState.ANSWERED

            c5 = CallStateMachine.transition(conn, "CALL_TEST_1", CallState.CONNECTED)
            assert c5 == CallState.CONNECTED

            c6 = CallStateMachine.transition(conn, "CALL_TEST_1", CallState.COMPLETED, duration_sec=45)
            assert c6 == CallState.COMPLETED


def test_call_illegal_state_transition(test_db):
    """Test that jumping from QUEUED to CONNECTED directly raises InvalidCallStateTransitionError."""
    with get_db(test_db) as conn:
        with transaction(conn):
            with pytest.raises(InvalidCallStateTransitionError):
                CallStateMachine.transition(conn, "CALL_TEST_1", CallState.CONNECTED)
