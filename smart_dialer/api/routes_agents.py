"""FastAPI routes for Agent Management."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from smart_dialer.db.connection import get_db, transaction
from smart_dialer.models.enums import AgentState
from smart_dialer.models.schemas import AgentBase, AgentUpdateStatusRequest, BulkAgentStatusUpdateRequest
from smart_dialer.state_machines.agent_state import AgentStateMachine, InvalidAgentStateTransitionError

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=List[AgentBase])
def list_agents(
    status: Optional[AgentState] = None,
    limit: int = Query(default=100, le=1000),
):
    """List agents filtered by status."""
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute(
                "SELECT agent_id, employee_code, agent_name, vendor_id, team, status FROM agents WHERE status = ? LIMIT ?",
                (status.value, limit),
            )
        else:
            cursor.execute(
                "SELECT agent_id, employee_code, agent_name, vendor_id, team, status FROM agents LIMIT ?",
                (limit,),
            )
        rows = cursor.fetchall()
        return [AgentBase(**r) for r in rows]


@router.patch("/{agent_id}/status")
def update_agent_status(agent_id: str, payload: AgentUpdateStatusRequest):
    """Transition agent status through state machine."""
    with get_db() as conn:
        with transaction(conn):
            try:
                new_state = AgentStateMachine.transition(
                    conn, agent_id, payload.status, reason="Manual status update via API"
                )
            except InvalidAgentStateTransitionError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        return {"agent_id": agent_id, "status": new_state.value}


@router.post("/bulk-status")
def bulk_update_agent_status(payload: BulkAgentStatusUpdateRequest):
    """
    Update status for multiple agents.
    Useful for Failure Scenario 3: Agent availability drops from 100 to 60.
    """
    target = payload.target_status.value
    count = payload.count or (len(payload.agent_ids) if payload.agent_ids else 0)

    with get_db() as conn:
        with transaction(conn) as cursor:
            if payload.agent_ids:
                placeholders = ",".join(["?"] * len(payload.agent_ids))
                cursor.execute(
                    f"UPDATE agents SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE agent_id IN ({placeholders})",
                    [target] + payload.agent_ids,
                )
                affected = cursor.rowcount
            elif count > 0:
                # Update first N available agents
                cursor.execute(
                    """
                    SELECT agent_id FROM agents
                    WHERE status = 'AVAILABLE'
                    LIMIT ?
                    """,
                    (count,),
                )
                agents = [r["agent_id"] for r in cursor.fetchall()]
                if agents:
                    placeholders = ",".join(["?"] * len(agents))
                    cursor.execute(
                        f"UPDATE agents SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE agent_id IN ({placeholders})",
                        [target] + agents,
                    )
                    affected = len(agents)
                else:
                    affected = 0
            else:
                affected = 0

        return {
            "target_status": target,
            "agents_updated": affected,
            "message": f"Successfully transitioned {affected} agents to {target}.",
        }
