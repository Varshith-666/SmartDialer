"""Agent State Machine with strict validation and audit logging."""

import sqlite3
from typing import Optional, Set
from smart_dialer.models.enums import AgentState


class InvalidAgentStateTransitionError(ValueError):
    """Raised when an illegal agent state transition is requested."""
    pass


class AgentStateMachine:
    """Manages legal agent state transitions and audit trails."""

    VALID_TRANSITIONS: dict[AgentState, Set[AgentState]] = {
        AgentState.OFFLINE: {
            AgentState.AVAILABLE,
            AgentState.PAUSED,
        },
        AgentState.AVAILABLE: {
            AgentState.RESERVED,
            AgentState.DIALING,
            AgentState.PAUSED,
            AgentState.OFFLINE,
        },
        AgentState.RESERVED: {
            AgentState.DIALING,
            AgentState.CONNECTED,
            AgentState.WRAP_UP,
            AgentState.AVAILABLE,  # Rollback on aborted call or timeout
            AgentState.OFFLINE,    # Emergency logout
        },
        AgentState.DIALING: {
            AgentState.CONNECTED,
            AgentState.WRAP_UP,
            AgentState.AVAILABLE,  # Call failed/busy before connect
            AgentState.OFFLINE,
        },
        AgentState.CONNECTED: {
            AgentState.WRAP_UP,
            AgentState.AVAILABLE,
            AgentState.OFFLINE,
        },
        AgentState.WRAP_UP: {
            AgentState.AVAILABLE,
            AgentState.PAUSED,
            AgentState.OFFLINE,
        },
        AgentState.PAUSED: {
            AgentState.AVAILABLE,
            AgentState.OFFLINE,
        },
    }

    @classmethod
    def can_transition(cls, from_state: AgentState, to_state: AgentState) -> bool:
        """Check if transitioning from `from_state` to `to_state` is legal."""
        if from_state == to_state:
            return True  # Idempotent no-op
        return to_state in cls.VALID_TRANSITIONS.get(from_state, set())

    @classmethod
    def transition(
        cls,
        conn: sqlite3.Connection,
        agent_id: str,
        to_state: AgentState,
        call_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> AgentState:
        """Perform atomic transition in the database with audit history."""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status, current_call_id FROM agents WHERE agent_id = ?",
            (agent_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Agent {agent_id} does not exist.")

        current_state = AgentState(row["status"])
        if current_state == to_state:
            return current_state

        if not cls.can_transition(current_state, to_state):
            raise InvalidAgentStateTransitionError(
                f"Illegal agent transition for {agent_id}: {current_state} -> {to_state}."
            )

        # Update agent record
        active_call = call_id if to_state in (
            AgentState.RESERVED,
            AgentState.DIALING,
            AgentState.CONNECTED,
            AgentState.WRAP_UP,
        ) else None

        cursor.execute(
            """
            UPDATE agents
            SET status = ?,
                current_call_id = ?,
                last_status_change = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE agent_id = ?
            """,
            (to_state.value, active_call, agent_id),
        )

        # Log audit entry
        cursor.execute(
            """
            INSERT INTO agent_state_history (agent_id, from_state, to_state, call_id, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (agent_id, current_state.value, to_state.value, call_id, reason),
        )

        return to_state
