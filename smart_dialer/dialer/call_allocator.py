"""Call Allocator: Atomic reservation of agents and borrowers with concurrency locks."""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from smart_dialer.config import settings
from smart_dialer.db.connection import transaction
from smart_dialer.models.enums import AgentState, CallState


class CallAllocator:
    """
    Atomically allocates and reserves borrowers and agents for outbound dialing.
    Ensures zero duplicate assignments across concurrent workers using atomic transactions.
    """

    @classmethod
    def allocate_calls(
        cls,
        conn: sqlite3.Connection,
        campaign_id: str,
        num_calls_to_allocate: int,
        vendor_id: Optional[str] = "VND_DEFAULT",
    ) -> List[Dict[str, Any]]:
        """
        Atomically reserve borrowers (and available agents if bound) and create calls in calls table.
        Returns list of allocated call payloads.
        """
        if num_calls_to_allocate <= 0:
            return []

        allocated_calls: List[Dict[str, Any]] = []
        token = str(uuid.uuid4())
        ttl_seconds = settings.RESERVATION_TTL_SECONDS

        # Execute in strict atomic immediate transaction
        with transaction(conn) as cursor:
            # 1. Fetch and atomically reserve queued borrowers
            cursor.execute(
                """
                SELECT queue_id, borrower_id
                FROM campaign_borrower_queue
                WHERE campaign_id = ? AND status = 'QUEUED'
                ORDER BY priority ASC, queue_id ASC
                LIMIT ?
                """,
                (campaign_id, num_calls_to_allocate),
            )
            borrower_rows = cursor.fetchall()

            if not borrower_rows:
                return []

            actual_borrowers = len(borrower_rows)
            queue_ids = [r["queue_id"] for r in borrower_rows]

            # Mark borrowers as RESERVED with token and expiry
            cursor.execute(
                f"""
                UPDATE campaign_borrower_queue
                SET status = 'RESERVED',
                    reservation_token = ?,
                    reserved_at = CURRENT_TIMESTAMP,
                    reservation_expires_at = datetime('now', '+{ttl_seconds} seconds')
                WHERE queue_id IN ({','.join(['?'] * len(queue_ids))})
                """,
                [token] + queue_ids,
            )

            # 2. Fetch and atomically reserve available agents (if any)
            cursor.execute(
                """
                SELECT agent_id
                FROM agents
                WHERE status = 'AVAILABLE'
                ORDER BY last_status_change ASC
                LIMIT ?
                """,
                (actual_borrowers,),
            )
            agent_rows = cursor.fetchall()
            agent_ids = [r["agent_id"] for r in agent_rows]

            if agent_ids:
                cursor.execute(
                    f"""
                    UPDATE agents
                    SET status = 'RESERVED',
                        reservation_token = ?,
                        reserved_at = CURRENT_TIMESTAMP,
                        reservation_expires_at = datetime('now', '+{ttl_seconds} seconds'),
                        last_status_change = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE agent_id IN ({','.join(['?'] * len(agent_ids))})
                    """,
                    [token] + agent_ids,
                )

                # Log to agent state history
                for ag_id in agent_ids:
                    cursor.execute(
                        """
                        INSERT INTO agent_state_history (agent_id, from_state, to_state, reason)
                        VALUES (?, 'AVAILABLE', 'RESERVED', 'Call allocation reservation')
                        """,
                        (ag_id,),
                    )

            # 3. Create Call records in RESERVED status
            for idx, b_row in enumerate(borrower_rows):
                call_id = f"CALL_{uuid.uuid4().hex[:12].upper()}"
                assigned_agent = agent_ids[idx] if idx < len(agent_ids) else None

                cursor.execute(
                    """
                    INSERT INTO calls (
                        call_id, campaign_id, borrower_id, agent_id,
                        vendor_id, call_status
                    )
                    VALUES (?, ?, ?, ?, ?, 'RESERVED')
                    """,
                    (
                        call_id,
                        campaign_id,
                        b_row["borrower_id"],
                        assigned_agent,
                        vendor_id,
                    ),
                )

                # Update agent's current call pointer if bound
                if assigned_agent:
                    cursor.execute(
                        "UPDATE agents SET current_call_id = ? WHERE agent_id = ?",
                        (call_id, assigned_agent),
                    )

                allocated_calls.append(
                    {
                        "call_id": call_id,
                        "campaign_id": campaign_id,
                        "borrower_id": b_row["borrower_id"],
                        "agent_id": assigned_agent,
                        "vendor_id": vendor_id,
                        "reservation_token": token,
                    }
                )

        return allocated_calls
