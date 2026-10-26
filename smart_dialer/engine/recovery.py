"""Recovery Engine: Stale reservation reaper and safe startup crash recovery."""

import sqlite3
from typing import Dict, Any
from smart_dialer.db.connection import transaction


class RecoveryEngine:
    """
    Recovers from worker crashes, expired reservations, and dangling locks.
    Essential for guaranteeing agents are never permanently trapped in RESERVED state.
    """

    @classmethod
    def reap_stale_reservations(cls, conn: sqlite3.Connection) -> Dict[str, int]:
        """
        Scan for expired reservations and restore borrowers and agents.
        Mandatory for Scenario 1 (worker crashes after reservation).
        """
        with transaction(conn) as cursor:
            # 1. Stale Agents: Status = RESERVED and reservation_expires_at < CURRENT_TIMESTAMP
            cursor.execute(
                """
                SELECT agent_id, reservation_token
                FROM agents
                WHERE status = 'RESERVED'
                  AND reservation_expires_at IS NOT NULL
                  AND reservation_expires_at < CURRENT_TIMESTAMP
                """
            )
            stale_agents = cursor.fetchall()
            agent_ids = [r["agent_id"] for r in stale_agents]

            if agent_ids:
                cursor.execute(
                    f"""
                    UPDATE agents
                    SET status = 'AVAILABLE',
                        current_call_id = NULL,
                        reservation_token = NULL,
                        reservation_expires_at = NULL,
                        last_status_change = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE agent_id IN ({','.join(['?'] * len(agent_ids))})
                    """,
                    agent_ids,
                )

                for ag_id in agent_ids:
                    cursor.execute(
                        """
                        INSERT INTO agent_state_history (agent_id, from_state, to_state, reason)
                        VALUES (?, 'RESERVED', 'AVAILABLE', 'Stale reservation reaped (worker crash/timeout)')
                        """,
                        (ag_id,),
                    )

            # 2. Stale Borrowers in Queue
            cursor.execute(
                """
                SELECT queue_id
                FROM campaign_borrower_queue
                WHERE status = 'RESERVED'
                  AND reservation_expires_at IS NOT NULL
                  AND reservation_expires_at < CURRENT_TIMESTAMP
                """
            )
            stale_queue_rows = cursor.fetchall()
            queue_ids = [r["queue_id"] for r in stale_queue_rows]

            if queue_ids:
                cursor.execute(
                    f"""
                    UPDATE campaign_borrower_queue
                    SET status = 'QUEUED',
                        reservation_token = NULL,
                        reservation_expires_at = NULL
                    WHERE queue_id IN ({','.join(['?'] * len(queue_ids))})
                    """,
                    queue_ids,
                )

            # 3. Uninitiated Calls left in RESERVED
            cursor.execute(
                """
                SELECT call_id
                FROM calls
                WHERE call_status = 'RESERVED'
                  AND created_at < datetime('now', '-30 seconds')
                """
            )
            stale_calls = cursor.fetchall()
            call_ids = [r["call_id"] for r in stale_calls]

            if call_ids:
                cursor.execute(
                    f"""
                    UPDATE calls
                    SET call_status = 'CANCELLED',
                        failure_reason = 'STALE_RESERVATION_TIMEOUT',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE call_id IN ({','.join(['?'] * len(call_ids))})
                    """,
                    call_ids,
                )

        return {
            "reaped_agents": len(agent_ids),
            "reaped_borrowers": len(queue_ids),
            "cancelled_stale_calls": len(call_ids),
        }

    @classmethod
    def recover_on_startup(cls, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Execute full crash reconciliation on application startup.
        Clean up all dangling reservations left by previously killed workers.
        """
        with transaction(conn) as cursor:
            # Force reap any agent stuck in RESERVED or DIALING without an active call
            cursor.execute(
                """
                UPDATE agents
                SET status = 'AVAILABLE',
                    reservation_token = NULL,
                    reservation_expires_at = NULL,
                    current_call_id = NULL
                WHERE status IN ('RESERVED', 'DIALING')
                """
            )
            recovered_agents = cursor.rowcount

            # Reset any borrowers trapped in RESERVED back to QUEUED
            cursor.execute(
                """
                UPDATE campaign_borrower_queue
                SET status = 'QUEUED',
                    reservation_token = NULL,
                    reservation_expires_at = NULL
                WHERE status = 'RESERVED'
                """
            )
            recovered_leads = cursor.rowcount

        return {
            "recovered_agents": recovered_agents,
            "recovered_leads": recovered_leads,
            "status": "RECONCILIATION_COMPLETE",
        }
