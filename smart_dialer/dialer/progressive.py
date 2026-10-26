"""Progressive Dialer Engine: Deterministic 1:1 agent-bound dialing."""

import sqlite3
from typing import Dict, Any


class ProgressiveDialer:
    """Implements progressive dialing: exactly one call per available agent."""

    @staticmethod
    def calculate_calls_to_dial(
        conn: sqlite3.Connection,
        campaign_id: str,
    ) -> Dict[str, Any]:
        """
        Calculate proposed outbound calls for progressive mode.
        Invariant: proposed_calls <= available_agents.
        """
        cursor = conn.cursor()

        # Count available agents
        cursor.execute("SELECT COUNT(*) as count FROM agents WHERE status = 'AVAILABLE'")
        available_agents = cursor.fetchone()["count"]

        # Count currently in-flight calls (INITIATED, RINGING, ANSWERED)
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM calls
            WHERE campaign_id = ?
              AND call_status IN ('INITIATED', 'RINGING', 'ANSWERED')
            """,
            (campaign_id,),
        )
        in_flight_calls = cursor.fetchone()["count"]

        # Count queued borrowers ready to dial
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM campaign_borrower_queue
            WHERE campaign_id = ? AND status = 'QUEUED'
            """,
            (campaign_id,),
        )
        queued_borrowers = cursor.fetchone()["count"]

        # Progressive rule: never exceed available capacity
        proposed_calls = max(0, min(available_agents, queued_borrowers))

        return {
            "mode": "PROGRESSIVE",
            "available_agents": available_agents,
            "in_flight_calls": in_flight_calls,
            "queued_borrowers": queued_borrowers,
            "proposed_calls": proposed_calls,
            "reasoning": (
                f"Progressive mode: {available_agents} available agents, "
                f"{queued_borrowers} queued leads. Proposed = min({available_agents}, {queued_borrowers}) = {proposed_calls}."
            ),
        }
