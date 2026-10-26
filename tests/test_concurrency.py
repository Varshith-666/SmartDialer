"""Concurrency and Race Condition Tests."""

import threading
import pytest
from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.dialer.call_allocator import CallAllocator


@pytest.fixture
def concurrency_db(tmp_path):
    db_file = str(tmp_path / "test_concurrency.db")
    init_db(db_file)
    with get_db(db_file) as conn:
        with transaction(conn) as cursor:
            cursor.execute("INSERT INTO campaigns (campaign_id, campaign_name) VALUES ('CMP_CONC', 'Concurrency Camp')")
            # 5 agents
            for i in range(5):
                cursor.execute(f"INSERT INTO agents (agent_id, agent_name, status) VALUES ('AGT_CONC_{i}', 'Agent {i}', 'AVAILABLE')")
            # 5 borrowers
            for i in range(5):
                cursor.execute(f"INSERT INTO borrowers (borrower_id, name, phone) VALUES ('BRW_CONC_{i}', 'Borrower {i}', '91111111{i:02d}')")
                cursor.execute(f"INSERT INTO campaign_borrower_queue (campaign_id, borrower_id, status) VALUES ('CMP_CONC', 'BRW_CONC_{i}', 'QUEUED')")
    yield db_file


def test_concurrent_reservation_isolation(concurrency_db):
    """
    Mandatory Scenario 6: Concurrent workers attempt to reserve the same agents or borrowers.
    Spawns 10 threads racing to allocate calls simultaneously.
    Verifies that SQLite transactions prevent double-allocation:
      1. Total assigned calls <= 5 (no phantom double bookings).
      2. Every call has a unique borrower_id and agent_id.
    """
    results = []
    errors = []

    def worker_task():
        try:
            with get_db(concurrency_db) as conn:
                allocations = CallAllocator.allocate_calls(
                    conn, campaign_id="CMP_CONC", num_calls_to_allocate=3
                )
                if allocations:
                    results.extend(allocations)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker_task) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify no duplicate borrower reservations
    borrower_ids = [c["borrower_id"] for c in results]
    assert len(borrower_ids) == len(set(borrower_ids)), "Duplicate borrower allocations detected!"
    assert len(borrower_ids) <= 5, "Exceeded available lead pool!"

    # Verify no duplicate agent reservations
    agent_ids = [c["agent_id"] for c in results if c["agent_id"] is not None]
    assert len(agent_ids) == len(set(agent_ids)), "Duplicate agent allocations detected!"
    assert len(agent_ids) <= 5, "Exceeded available agent capacity!"
