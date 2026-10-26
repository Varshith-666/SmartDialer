"""Campaign Manager: Handles campaign lifecycle and lead queue orchestration."""

import sqlite3
from typing import List, Dict, Any, Optional
from smart_dialer.db.connection import transaction
from smart_dialer.models.enums import DialerMode


class CampaignManager:
    """Manages outbound campaigns and campaign borrower queueing."""

    @classmethod
    def create_campaign(
        cls,
        conn: sqlite3.Connection,
        campaign_id: str,
        campaign_name: str,
        channel: str = "VOICE",
        strategy_version: str = "v1",
        dialer_mode: DialerMode = DialerMode.PROGRESSIVE,
        target_definition: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign record."""
        with transaction(conn) as cursor:
            cursor.execute(
                """
                INSERT INTO campaigns (
                    campaign_id, campaign_name, channel, strategy_version,
                    dialer_mode, target_definition
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id,
                    campaign_name,
                    channel,
                    strategy_version,
                    dialer_mode.value,
                    target_definition,
                ),
            )
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "channel": channel,
            "dialer_mode": dialer_mode.value,
            "status": "ACTIVE",
        }

    @classmethod
    def set_dialer_mode(
        cls,
        conn: sqlite3.Connection,
        campaign_id: str,
        new_mode: DialerMode,
    ) -> Dict[str, Any]:
        """Update dialer mode between PROGRESSIVE and PREDICTIVE."""
        with transaction(conn) as cursor:
            cursor.execute(
                "UPDATE campaigns SET dialer_mode = ? WHERE campaign_id = ?",
                (new_mode.value, campaign_id),
            )
        return {"campaign_id": campaign_id, "dialer_mode": new_mode.value}

    @classmethod
    def enqueue_borrowers(
        cls,
        conn: sqlite3.Connection,
        campaign_id: str,
        borrower_ids: List[str],
        priority: int = 1,
    ) -> int:
        """Enqueue a list of borrowers into the campaign dialing queue."""
        inserted = 0
        with transaction(conn) as cursor:
            for b_id in borrower_ids:
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO campaign_borrower_queue (campaign_id, borrower_id, priority, status)
                        VALUES (?, ?, ?, 'QUEUED')
                        """,
                        (campaign_id, b_id, priority),
                    )
                    inserted += cursor.rowcount
                except sqlite3.IntegrityError:
                    pass
        return inserted
