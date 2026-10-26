"""Core Dialer Worker: Orchestrates the complete end-to-end dialing cycle."""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from smart_dialer.config import settings
from smart_dialer.models.enums import DialerMode, ProviderEventType
from smart_dialer.dialer.progressive import ProgressiveDialer
from smart_dialer.dialer.predictive import PredictivePacingEngine
from smart_dialer.dialer.safety_controller import SafetyController
from smart_dialer.dialer.call_allocator import CallAllocator
from smart_dialer.engine.recovery import RecoveryEngine
from smart_dialer.engine.event_processor import EventProcessor
from smart_dialer.providers.base import BaseTelecomProvider
from smart_dialer.providers.reliable_provider import ReliableTelecomProvider
from smart_dialer.providers.chaotic_provider import ChaoticTelecomProvider


class DialerWorker:
    """
    Core orchestrator that runs dialing cycles adhering strictly to the architecture:
    Campaign Manager -> Borrower Queue -> Pacing Engine -> Safety Controller -> Call Allocator -> Provider
    """

    def __init__(
        self,
        provider: Optional[BaseTelecomProvider] = None,
        custom_answer_rate: Optional[float] = None,
        custom_talk_time: Optional[float] = None,
    ):
        if provider:
            self.provider = provider
        elif settings.PROVIDER_TYPE == "chaotic":
            self.provider = ChaoticTelecomProvider()
        else:
            self.provider = ReliableTelecomProvider()

        self.custom_answer_rate = custom_answer_rate
        self.custom_talk_time = custom_talk_time

    def run_cycle(
        self,
        conn: sqlite3.Connection,
        campaign_id: str,
        force_mode: Optional[DialerMode] = None,
        simulate_telephony_events: bool = True,
        target_outcome: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute one complete atomic dialer iteration.
        """
        cycle_start = datetime.now(timezone.utc)

        # Step 1: Stale Reservation Recovery (Reap expired worker locks)
        reaped = RecoveryEngine.reap_stale_reservations(conn)

        # Step 2: Read Campaign Configuration
        cursor = conn.cursor()
        cursor.execute(
            "SELECT campaign_id, dialer_mode, status FROM campaigns WHERE campaign_id = ?",
            (campaign_id,),
        )
        campaign_row = cursor.fetchone()
        if not campaign_row:
            raise ValueError(f"Campaign {campaign_id} not found.")

        active_mode = force_mode.value if force_mode else campaign_row["dialer_mode"]

        # Step 3: Pacing Engine Evaluation
        if active_mode == DialerMode.PREDICTIVE.value:
            pacing_result = PredictivePacingEngine.calculate_calls_to_dial(
                conn,
                campaign_id,
                custom_answer_rate=self.custom_answer_rate,
                custom_talk_time=self.custom_talk_time,
            )
        else:
            pacing_result = ProgressiveDialer.calculate_calls_to_dial(conn, campaign_id)

        # Step 4: Independent Safety Controller Gatekeeper
        safety_eval = SafetyController.evaluate(conn, campaign_id, pacing_result)
        approved_calls = safety_eval["approved_calls"]

        # Step 5: Atomic Call Allocation (Reserve borrowers and agents)
        allocated_calls = CallAllocator.allocate_calls(
            conn,
            campaign_id,
            num_calls_to_allocate=approved_calls,
            vendor_id="VND_DEFAULT",
        )

        # Step 6: Telecom Provider Dispatch & Event Ingestion
        dispatched_call_ids: List[str] = []
        event_summaries: List[Dict[str, Any]] = []

        for call in allocated_calls:
            c_id = call["call_id"]
            dispatched_call_ids.append(c_id)

            # Fetch borrower phone
            cursor.execute(
                "SELECT phone FROM borrowers WHERE borrower_id = ?",
                (call["borrower_id"],),
            )
            phone_row = cursor.fetchone()
            phone = phone_row["phone"] if phone_row else "0000000000"

            # Dispatch outbound initiation with error/timeout protection
            try:
                dispatch_res = self.provider.initiate_call(c_id, phone)
                if isinstance(dispatch_res, dict) and dispatch_res.get("status") == "REJECTED":
                    EventProcessor.process_event(
                        conn,
                        {
                            "call_id": c_id,
                            "event_type": ProviderEventType.FAILED.value,
                            "failure_reason": dispatch_res.get("error", "CARRIER_REJECTED"),
                        },
                    )
                    continue
            except Exception as carrier_err:
                # Catch ProviderTimeoutError or network outage safely
                EventProcessor.process_event(
                    conn,
                    {
                        "call_id": c_id,
                        "event_type": ProviderEventType.FAILED.value,
                        "failure_reason": f"CARRIER_ERROR: {str(carrier_err)}",
                    },
                )
                continue

            # If simulation enabled, run through provider event flow
            if simulate_telephony_events:
                events = self.provider.simulate_event_flow(
                    c_id,
                    target_outcome=target_outcome,
                    duration_sec=int(self.custom_talk_time or settings.DEFAULT_TALK_TIME_SECONDS),
                )
                for evt in events:
                    res = EventProcessor.process_event(conn, evt)
                    event_summaries.append(res)

        return {
            "campaign_id": campaign_id,
            "mode": active_mode,
            "cycle_start": cycle_start.isoformat(),
            "reaped_stale_locks": reaped,
            "pacing_result": pacing_result,
            "safety_decision": safety_eval,
            "calls_allocated": len(allocated_calls),
            "dispatched_call_ids": dispatched_call_ids,
            "events_processed": len(event_summaries),
        }
