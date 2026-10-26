"""FastAPI routes for Campaign Management."""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from smart_dialer.db.connection import get_db, transaction
from smart_dialer.models.schemas import CampaignCreateRequest, CampaignUpdateModeRequest
from smart_dialer.engine.campaign_manager import CampaignManager

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("")
def list_campaigns():
    """List all campaigns and active dialer modes."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT campaign_id, campaign_name, channel, strategy_version,
                   status, dialer_mode, target_definition, created_at
            FROM campaigns
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


@router.post("", status_code=201)
def create_campaign(payload: CampaignCreateRequest):
    """Create a new outbound campaign."""
    with get_db() as conn:
        try:
            return CampaignManager.create_campaign(
                conn,
                campaign_id=payload.campaign_id,
                campaign_name=payload.campaign_name,
                channel=payload.channel,
                strategy_version=payload.strategy_version,
                dialer_mode=payload.dialer_mode,
                target_definition=payload.target_definition,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{campaign_id}/mode")
def update_dialer_mode(campaign_id: str, payload: CampaignUpdateModeRequest):
    """Switch campaign dialing strategy between PROGRESSIVE and PREDICTIVE."""
    with get_db() as conn:
        try:
            return CampaignManager.set_dialer_mode(conn, campaign_id, payload.dialer_mode)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
