"""Call State Machine with transition matrix, out-of-order recovery, and idempotency."""

import sqlite3
from datetime import datetime
from typing import Optional, Set
from smart_dialer.models.enums import AgentState, CallState
from smart_dialer.state_machines.agent_state import AgentStateMachine


class InvalidCallStateTransitionError(ValueError):
    """Raised when an illegal call state transition is requested."""
    pass


class CallStateMachine:
    """Enforces the Call State Machine with idempotency and fault tolerance."""

    VALID_TRANSITIONS: dict[CallState, Set[CallState]] = {
        CallState.QUEUED: {
            CallState.RESERVED,
            CallState.CANCELLED,
            CallState.FAILED,
        },
        CallState.RESERVED: {
            CallState.INITIATED,
            CallState.CANCELLED,
            CallState.FAILED,
        },
        CallState.INITIATED: {
            CallState.RINGING,
            CallState.ANSWERED,    # Fast pickup
            CallState.COMPLETED,   # Out-of-order immediate drop
            CallState.FAILED,
            CallState.CANCELLED,
        },
        CallState.RINGING: {
            CallState.ANSWERED,
            CallState.COMPLETED,   # Out-of-order arrival (Scenario 5)
            CallState.FAILED,      # Busy / No Answer
            CallState.CANCELLED,
        },
        CallState.ANSWERED: {
            CallState.CONNECTED,
            CallState.COMPLETED,   # Immediate hangup before audio bridge
            CallState.FAILED,      # Abandoned call (no available agent)
        },
        CallState.CONNECTED: {
            CallState.COMPLETED,
            CallState.FAILED,
        },
        CallState.COMPLETED: set(),  # Terminal state
        CallState.FAILED: set(),     # Terminal state
        CallState.CANCELLED: set(),  # Terminal state
    }

    @classmethod
    def can_transition(cls, from_state: CallState, to_state: CallState) -> bool:
        """Check if transitioning from `from_state` to `to_state` is legal."""
        if from_state == to_state:
            return True  # Idempotent
        return to_state in cls.VALID_TRANSITIONS.get(from_state, set())

    @classmethod
    def transition(
        cls,
        conn: sqlite3.Connection,
        call_id: str,
        to_state: CallState,
        duration_sec: int = 0,
        failure_reason: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> CallState:
        """Atomically transition call state in the database, updating agent status where applicable."""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT call_status, agent_id FROM calls WHERE call_id = ?",
            (call_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Call {call_id} does not exist.")

        current_state = CallState(row["call_status"])
        assigned_agent = agent_id or row["agent_id"]

        # Idempotent no-op check (e.g. Duplicate ANSWERED events)
        if current_state == to_state:
            return current_state

        # Terminal state protection
        if current_state in (CallState.COMPLETED, CallState.FAILED, CallState.CANCELLED):
            # Already finalized; safely ignore duplicate late-arriving non-terminal events
            return current_state

        if not cls.can_transition(current_state, to_state):
            raise InvalidCallStateTransitionError(
                f"Illegal call transition for {call_id}: {current_state} -> {to_state}."
            )

        # Build column update query based on target state
        updates = ["call_status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params: list = [to_state.value]

        if to_state == CallState.INITIATED:
            updates.append("initiated_at = CURRENT_TIMESTAMP")
        elif to_state == CallState.RINGING:
            updates.append("ringing_at = CURRENT_TIMESTAMP")
        elif to_state == CallState.ANSWERED:
            updates.append("answered_at = CURRENT_TIMESTAMP")
        elif to_state == CallState.CONNECTED:
            updates.append("connected_at = CURRENT_TIMESTAMP")
        elif to_state == CallState.COMPLETED:
            updates.append("completed_at = CURRENT_TIMESTAMP")
            if duration_sec > 0:
                updates.append("duration_sec = ?")
                params.append(duration_sec)
        elif to_state == CallState.FAILED:
            updates.append("failure_reason = ?")
            params.append(failure_reason or "CALL_FAILED")

        params.append(call_id)
        cursor.execute(
            f"UPDATE calls SET {', '.join(updates)} WHERE call_id = ?",
            params,
        )

        # Coordinate Agent State Transitions
        if assigned_agent:
            if to_state == CallState.INITIATED:
                AgentStateMachine.transition(
                    conn, assigned_agent, AgentState.DIALING, call_id=call_id, reason="Call initiated"
                )
            elif to_state == CallState.CONNECTED:
                AgentStateMachine.transition(
                    conn, assigned_agent, AgentState.CONNECTED, call_id=call_id, reason="Call connected"
                )
            elif to_state in (CallState.COMPLETED, CallState.FAILED, CallState.CANCELLED):
                # If call was connected, agent moves to WRAP_UP; if failed before connect, return directly to AVAILABLE
                target_agent_state = AgentState.WRAP_UP if current_state == CallState.CONNECTED else AgentState.AVAILABLE
                AgentStateMachine.transition(
                    conn, assigned_agent, target_agent_state, call_id=call_id, reason=f"Call {to_state.value}"
                )

        return to_state
