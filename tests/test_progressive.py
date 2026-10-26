"""Unit tests for Progressive Dialer Engine."""

import pytest
from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.dialer.progressive import ProgressiveDialer


@pytest.fixture
def progressive_db(tmp_path):
    db_file = str(tmp_path / "test_progressive.db")
    init_db(db_file)
    with get_db(db_file) as conn:
        with transaction(conn) as cursor:
            cursor.execute("INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode) VALUES ('CMP_1', 'Camp 1', 'PROGRESSIVE')")
            # 5 agents available
            for i in range(5):
                cursor.execute(f"INSERT INTO agents (agent_id, agent_name, status) VALUES ('AGT_{i}', 'Agent {i}', 'AVAILABLE')")
            # 10 borrowers queued
            for i in range(10):
                cursor.execute(f"INSERT INTO borrowers (borrower_id, name, phone) VALUES ('BRW_{i}', 'Borrower {i}', '987654321{i}')")
                cursor.execute(f"INSERT INTO campaign_borrower_queue (campaign_id, borrower_id, status) VALUES ('CMP_1', 'BRW_{i}', 'QUEUED')")
    yield db_file


def test_progressive_capacity_cap(progressive_db):
    """Test that progressive dialing never proposes more calls than available agents."""
    with get_db(progressive_db) as conn:
        result = ProgressiveDialer.calculate_calls_to_dial(conn, "CMP_1")
        # 5 available agents, 10 queued -> proposed must be exactly 5
        assert result["available_agents"] == 5
        assert result["queued_borrowers"] == 10
        assert result["proposed_calls"] == 5


def test_progressive_zero_agents(progressive_db):
    """Test that zero available agents results in exactly zero proposed calls."""
    with get_db(progressive_db) as conn:
        with transaction(conn) as cursor:
            cursor.execute("UPDATE agents SET status = 'OFFLINE'")
        result = ProgressiveDialer.calculate_calls_to_dial(conn, "CMP_1")
        assert result["available_agents"] == 0
        assert result["proposed_calls"] == 0


def test_progressive_limited_queue(progressive_db):
    """Test that when queue is smaller than agents, proposed calls equals queue size."""
    with get_db(progressive_db) as conn:
        with transaction(conn) as cursor:
            cursor.execute("DELETE FROM campaign_borrower_queue WHERE queue_id > 2")
        result = ProgressiveDialer.calculate_calls_to_dial(conn, "CMP_1")
        assert result["queued_borrowers"] == 2
        assert result["proposed_calls"] == 2
