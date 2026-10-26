"""FastAPI routes for running and controlling dialing cycles."""

from fastapi import APIRouter, HTTPException
from smart_dialer.db.connection import get_db
from smart_dialer.models.schemas import DialCycleRunRequest
from smart_dialer.engine.dialer_worker import DialerWorker

router = APIRouter(prefix="/dialer", tags=["Dialer Engine"])


@router.post("/run-cycle")
def run_dialer_cycle(payload: DialCycleRunRequest):
    """
    Execute one atomic dialing cycle:
    Pacing calculation -> Safety Controller evaluation -> Allocation -> Carrier dispatch.
    """
    with get_db() as conn:
        try:
            worker = DialerWorker()
            result = worker.run_cycle(
                conn,
                campaign_id=payload.campaign_id,
                force_mode=payload.force_mode,
                simulate_telephony_events=True,
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Dialing cycle error: {str(e)}")
