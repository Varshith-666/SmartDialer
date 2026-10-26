"""Predictive Pacing Engine: Statistical Erlang/Hazard-based pacing model."""

import sqlite3
import math
from typing import Dict, Any, Optional
from smart_dialer.config import settings


class PredictivePacingEngine:
    """
    Statistical Predictive Pacing Engine.
    Estimates outbound calls using Little's Law / Hazard Rate of connected agents,
    telephony latency, provider failure rates, and historical answer rates.
    """

    @staticmethod
    def calculate_calls_to_dial(
        conn: sqlite3.Connection,
        campaign_id: str,
        custom_answer_rate: Optional[float] = None,
        custom_talk_time: Optional[float] = None,
        custom_failure_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate proposed outbound calls for predictive mode.
        """
        cursor = conn.cursor()

        # 1. Available Agents
        cursor.execute("SELECT COUNT(*) as count FROM agents WHERE status = 'AVAILABLE'")
        n_available = cursor.fetchone()["count"]

        # 2. Connected Agents (currently talking)
        cursor.execute("SELECT COUNT(*) as count FROM agents WHERE status = 'CONNECTED'")
        n_connected = cursor.fetchone()["count"]

        # 3. Active in-flight calls (INITIATED or RINGING)
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM calls
            WHERE campaign_id = ?
              AND call_status IN ('INITIATED', 'RINGING')
            """,
            (campaign_id,),
        )
        n_in_flight = cursor.fetchone()["count"]

        # 4. Queued borrowers ready to dial
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM campaign_borrower_queue
            WHERE campaign_id = ? AND status = 'QUEUED'
            """,
            (campaign_id,),
        )
        queued_borrowers = cursor.fetchone()["count"]

        # 5. Parameters & Historical Calibration
        p_ans = custom_answer_rate if custom_answer_rate is not None else settings.DEFAULT_ANSWER_RATE
        t_talk = custom_talk_time if custom_talk_time is not None else settings.DEFAULT_TALK_TIME_SECONDS
        p_fail = custom_failure_rate if custom_failure_rate is not None else settings.PROVIDER_FAILURE_RATE
        t_setup = settings.CALL_SETUP_LATENCY_SECONDS

        # Effective Answer Probability (accounting for carrier failure drops)
        p_eff = max(0.05, min(0.95, p_ans * (1.0 - p_fail)))

        # 6. Expected Agent Departures (Hazard rate during setup window)
        # Expected agents completing calls while new calls ring: E_free = n_connected * (t_setup / t_talk)
        t_talk_clamped = max(10.0, t_talk)
        expected_free_agents = n_connected * (t_setup / t_talk_clamped)

        # 7. Total Projected Agent Capacity when calls pick up
        projected_capacity = n_available + expected_free_agents

        # 8. Expected answers from calls already ringing
        pending_answers = n_in_flight * p_eff

        # 9. Net agent capacity needed
        net_capacity_needed = max(0.0, projected_capacity - pending_answers)

        # 10. Raw Proposed Calls = Net Capacity / Effective Answer Rate
        raw_proposed = net_capacity_needed / p_eff if p_eff > 0 else 0.0
        proposed_calls = int(math.floor(raw_proposed))

        # Clamp by lead inventory
        proposed_calls = max(0, min(proposed_calls, queued_borrowers))

        explanation = (
            f"Predictive Model: Available={n_available}, Connected={n_connected}, In-Flight={n_in_flight}. "
            f"p_ans={p_ans:.2f}, p_fail={p_fail:.2f} -> p_eff={p_eff:.3f}. "
            f"Expected Free Agents (t_setup={t_setup}s, t_talk={t_talk}s) = {expected_free_agents:.2f}. "
            f"Projected Capacity = {projected_capacity:.2f}. Pending Answers = {pending_answers:.2f}. "
            f"Net Needed = {net_capacity_needed:.2f} -> Raw Proposed = {raw_proposed:.2f} -> Final Proposed = {proposed_calls}."
        )

        return {
            "mode": "PREDICTIVE",
            "available_agents": n_available,
            "connected_agents": n_connected,
            "in_flight_calls": n_in_flight,
            "queued_borrowers": queued_borrowers,
            "answer_rate": p_ans,
            "failure_rate": p_fail,
            "effective_answer_rate": p_eff,
            "avg_talk_time_sec": t_talk,
            "setup_time_sec": t_setup,
            "expected_free_agents": round(expected_free_agents, 2),
            "projected_capacity": round(projected_capacity, 2),
            "pending_answers": round(pending_answers, 2),
            "raw_proposed_calls": round(raw_proposed, 2),
            "proposed_calls": proposed_calls,
            "reasoning": explanation,
        }
