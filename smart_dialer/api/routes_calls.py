"""FastAPI routes for Call Records and Event Inspection."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from smart_dialer.db.connection import get_db

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.get("")
def list_calls(
    status: Optional[str] = None,
    campaign_id: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
):
    """List calls filtered by status or campaign."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM calls WHERE 1=1"
        params = []
        if status:
            query += " AND call_status = ?"
            params.append(status)
        if campaign_id:
            query += " AND campaign_id = ?"
            params.append(campaign_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return cursor.fetchall()


@router.get("/{call_id}")
def get_call_detail(call_id: str):
    """Get full details of a specific call."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calls WHERE call_id = ?", (call_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Call {call_id} not found.")
        return row


@router.get("/{call_id}/events")
def get_call_events(call_id: str):
    """Get chronological provider event logs for a call."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT event_id, call_id, event_type, from_status, to_status,
                   idempotency_key, payload, created_at
            FROM call_events
            WHERE call_id = ?
            ORDER BY event_id ASC
            """,
            (call_id,),
        )
        return cursor.fetchall()
