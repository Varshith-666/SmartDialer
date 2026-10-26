"""Independent Safety Controller: Gatekeeper enforcing hard dialer safety constraints."""

import sqlite3
from typing import Dict, Any, Tuple
from smart_dialer.config import settings
from smart_dialer.models.enums import SafetyDecision, DialerMode


class SafetyController:
    """
    Independent Safety Controller.
    Acts as a non-bypassable firewall between pacing logic and call allocation.
    Evaluates:
      1. Overdial ratio ceiling.
      2. Regulatory abandoned call ceiling (FCC 3% limit).
      3. Minimum agent threshold for predictive statistics.
      4. Telephony provider circuit breaker (error rates/timeouts).
      5. Stale reservations and agent availability drops.
    """

    @classmethod
    def evaluate(
        cls,
        conn: sqlite3.Connection,
        campaign_id: str,
        pacing_result: Dict[str, Any],
        recent_provider_error_rate: float = 0.0,
        historical_abandon_rate: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Evaluate proposed calls against hard safety boundaries.
        Returns safety decision, approved calls, and logs to safety_controller_audit.
        """
        mode = pacing_result.get("mode", "PROGRESSIVE")
        proposed = pacing_result.get("proposed_calls", 0)
        available = pacing_result.get("available_agents", 0)
        in_flight = pacing_result.get("in_flight_calls", 0)
        p_ans = pacing_result.get("answer_rate", settings.DEFAULT_ANSWER_RATE)

        # In Progressive Mode: proposed is already clamped to available agents
        if mode == "PROGRESSIVE":
            approved = max(0, min(proposed, available))
            decision = SafetyDecision.APPROVE if approved == proposed else SafetyDecision.REDUCE
            reason = f"Progressive safety: strictly capped at available capacity ({available})."
            return cls._finalize(conn, campaign_id, mode, available, proposed, approved, decision, reason, p_ans, in_flight)

        # --- PREDICTIVE MODE SAFETY ENFORCEMENT ---

        # 1. Circuit Breaker: Provider Failure Rate / Outage Check
        if recent_provider_error_rate > settings.CIRCUIT_BREAKER_PROVIDER_ERROR_THRESHOLD:
            decision = SafetyDecision.FORCE_PROGRESSIVE
            approved = max(0, min(available, proposed))
            reason = (
                f"SAFETY TRIGGER: Provider error rate ({recent_provider_error_rate:.1%}) exceeded "
                f"circuit threshold ({settings.CIRCUIT_BREAKER_PROVIDER_ERROR_THRESHOLD:.1%}). "
                f"Forcing rollback to Progressive Mode."
            )
            return cls._finalize(conn, campaign_id, mode, available, proposed, approved, decision, reason, p_ans, in_flight)

        # 2. Minimum Agent Quorum Check
        if available < settings.MIN_AVAILABLE_AGENTS_FOR_PREDICTIVE and in_flight > 0:
            decision = SafetyDecision.FORCE_PROGRESSIVE
            approved = max(0, min(available, 1))
            reason = (
                f"SAFETY TRIGGER: Available agents ({available}) below predictive quorum "
                f"({settings.MIN_AVAILABLE_AGENTS_FOR_PREDICTIVE}) with active calls in flight. "
                f"Downgrading to Progressive Mode."
            )
            return cls._finalize(conn, campaign_id, mode, available, proposed, approved, decision, reason, p_ans, in_flight)

        # 3. Abandoned Call Ceiling Check (Regulatory compliance)
        if historical_abandon_rate > settings.MAX_ABANDON_RATE:
            decision = SafetyDecision.FORCE_PROGRESSIVE
            approved = max(0, min(available, proposed))
            reason = (
                f"SAFETY TRIGGER: Abandon rate ({historical_abandon_rate:.1%}) exceeded "
                f"safe ceiling ({settings.MAX_ABANDON_RATE:.1%}). Downgrading to Progressive Mode."
            )
            return cls._finalize(conn, campaign_id, mode, available, proposed, approved, decision, reason, p_ans, in_flight)

        # 4. Zero Available Agents & Low Departure Check
        expected_free = pacing_result.get("expected_free_agents", 0.0)
        if available == 0 and expected_free < 0.5:
            decision = SafetyDecision.REJECT
            approved = 0
            reason = "SAFETY TRIGGER: Zero available agents and negligible expected call completions. Dialing halted."
            return cls._finalize(conn, campaign_id, mode, available, proposed, approved, decision, reason, p_ans, in_flight)

        # 5. Overdial Ratio Ceiling
        # Maximum allowed active + proposed calls relative to agent pool
        effective_agent_base = max(1.0, float(available + expected_free))
        max_allowed_calls = int(effective_agent_base * settings.MAX_OVERDIAL_RATIO)

        # Total outstanding calls if proposed were accepted
        total_projected_inflight = in_flight + proposed

        if total_projected_inflight > max_allowed_calls:
            headroom = max(0, max_allowed_calls - in_flight)
            approved = min(proposed, headroom)
            decision = SafetyDecision.REDUCE
            reason = (
                f"SAFETY TRIGGER: Overdial ratio ceiling hit. Max allowed in-flight = {max_allowed_calls} "
                f"(Ratio {settings.MAX_OVERDIAL_RATIO:.1f}x on base {effective_agent_base:.1f}). "
                f"Reduced proposed from {proposed} to {approved}."
            )
            return cls._finalize(conn, campaign_id, mode, available, proposed, approved, decision, reason, p_ans, in_flight)

        # All safety checks passed
        decision = SafetyDecision.APPROVE
        approved = proposed
        reason = f"Safety checks passed. Approved all {approved} proposed calls."
        return cls._finalize(conn, campaign_id, mode, available, proposed, approved, decision, reason, p_ans, in_flight)

    @classmethod
    def _finalize(
        cls,
        conn: sqlite3.Connection,
        campaign_id: str,
        mode: str,
        available: int,
        proposed: int,
        approved: int,
        decision: SafetyDecision,
        reason: str,
        p_ans: float,
        in_flight: int,
    ) -> Dict[str, Any]:
        """Record audit log and package result."""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO safety_controller_audit (
                campaign_id, dialer_mode, available_agents, calls_proposed,
                calls_approved, decision, reason, current_answer_rate, active_in_flight_calls
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                campaign_id,
                mode,
                available,
                proposed,
                approved,
                decision.value,
                reason,
                p_ans,
                in_flight,
            ),
        )

        return {
            "decision": decision,
            "reason": reason,
            "proposed_calls": proposed,
            "approved_calls": approved,
            "available_agents": available,
            "in_flight_calls": in_flight,
        }
