"""FastAPI routes for Borrower Queue and Lead Management."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from smart_dialer.db.connection import get_db, transaction
from smart_dialer.models.schemas import BorrowerImportItem
from smart_dialer.engine.campaign_manager import CampaignManager

router = APIRouter(prefix="/borrowers", tags=["Borrowers"])


class EnqueueBorrowersRequest(BaseModel):
    campaign_id: str
    borrower_ids: List[str]
    priority: int = 1


@router.get("/queue/{campaign_id}")
def get_campaign_queue(
    campaign_id: str,
    status: Optional[str] = "QUEUED",
    limit: int = Query(default=100, le=1000),
):
    """View campaign borrower queue."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT q.queue_id, q.campaign_id, q.borrower_id, q.priority, q.status,
                   b.name, b.phone, q.attempts_count, q.created_at
            FROM campaign_borrower_queue q
            JOIN borrowers b ON q.borrower_id = b.borrower_id
            WHERE q.campaign_id = ? AND (? IS NULL OR q.status = ?)
            ORDER BY q.priority ASC, q.queue_id ASC
            LIMIT ?
            """,
            (campaign_id, status, status, limit),
        )
        return cursor.fetchall()


@router.post("/enqueue")
def enqueue_leads(payload: EnqueueBorrowersRequest):
    """Enqueue borrower leads into a campaign."""
    with get_db() as conn:
        inserted = CampaignManager.enqueue_borrowers(
            conn,
            campaign_id=payload.campaign_id,
            borrower_ids=payload.borrower_ids,
            priority=payload.priority,
        )
        return {
            "campaign_id": payload.campaign_id,
            "leads_enqueued": inserted,
        }


@router.post("/batch-import")
def batch_import_borrowers(borrowers: List[BorrowerImportItem]):
    """Directly insert a batch of borrowers."""
    with get_db() as conn:
        with transaction(conn) as cursor:
            for b in borrowers:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO borrowers (borrower_id, name, phone, email, city, state)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (b.borrower_id, b.name, b.phone, b.email, b.city, b.state),
                )
        return {"status": "SUCCESS", "imported_count": len(borrowers)}


@router.post("/replenish/{campaign_id}")
def replenish_campaign_leads(campaign_id: str, count: int = Query(default=100, le=500)):
    """Replenish campaign queue with unqueued or fresh borrowers."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.borrower_id FROM borrowers b
            WHERE b.borrower_id NOT IN (
                SELECT borrower_id FROM campaign_borrower_queue WHERE campaign_id = ?
            )
            LIMIT ?
            """,
            (campaign_id, count),
        )
        rows = cursor.fetchall()
        borrower_ids = [r["borrower_id"] for r in rows]
        if not borrower_ids:
            cursor.execute("SELECT borrower_id FROM borrowers LIMIT ?", (count,))
            borrower_ids = [r["borrower_id"] for r in cursor.fetchall()]

        inserted = CampaignManager.enqueue_borrowers(
            conn,
            campaign_id=campaign_id,
            borrower_ids=borrower_ids,
            priority=1,
        )
        return {
            "campaign_id": campaign_id,
            "leads_enqueued": inserted,
            "borrowers_selected": len(borrower_ids),
        }

