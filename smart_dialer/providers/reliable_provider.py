"""Reliable Telecom Provider: Fast, deterministic mock provider."""

import random
import time
import uuid
from typing import Dict, Any, List, Optional
from smart_dialer.providers.base import BaseTelecomProvider
from smart_dialer.models.enums import ProviderEventType


class ReliableTelecomProvider(BaseTelecomProvider):
    """
    Standard reliable carrier mock.
    Respects strict event ordering: INITIATED -> RINGING -> ANSWERED -> CONNECTED -> COMPLETED.
    Low latency, deterministic error handling.
    """

    def __init__(
        self,
        failure_rate: float = 0.05,
        answer_rate: float = 0.20,
        latency_ms: int = 50,
    ):
        self.failure_rate = failure_rate
        self.answer_rate = answer_rate
        self.latency_ms = latency_ms

    def initiate_call(
        self,
        call_id: str,
        phone_number: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Acknowledge outbound call request instantly."""
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)

        carrier_ref = f"TEL_{uuid.uuid4().hex[:10]}"
        return {
            "status": "ACCEPTED",
            "provider": "ReliableTelecom",
            "carrier_ref": carrier_ref,
            "call_id": call_id,
        }

    def simulate_event_flow(
        self,
        call_id: str,
        target_outcome: Optional[str] = None,
        duration_sec: int = 120,
    ) -> List[Dict[str, Any]]:
        """Generate ordered list of carrier webhook events for this call."""
        events: List[Dict[str, Any]] = []

        # Event 1: INITIATED
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.INITIATED.value,
                "idempotency_key": f"IDEM_{call_id}_INITIATED",
                "duration_sec": 0,
            }
        )

        # Check for carrier immediate failure
        is_failure = random.random() < self.failure_rate if target_outcome is None else (target_outcome == "FAILED")
        if is_failure:
            events.append(
                {
                    "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                    "call_id": call_id,
                    "event_type": ProviderEventType.FAILED.value,
                    "idempotency_key": f"IDEM_{call_id}_FAILED",
                    "failure_reason": "CARRIER_CONGESTION",
                    "duration_sec": 0,
                }
            )
            return events

        # Event 2: RINGING
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.RINGING.value,
                "idempotency_key": f"IDEM_{call_id}_RINGING",
                "duration_sec": 0,
            }
        )

        # Determine if borrower answers
        is_answered = random.random() < self.answer_rate if target_outcome is None else (target_outcome == "ANSWERED")

        if not is_answered:
            # Result: BUSY or NO_ANSWER (mapped to FAILED in telephony state)
            outcome = random.choice([ProviderEventType.BUSY.value, ProviderEventType.NO_ANSWER.value])
            events.append(
                {
                    "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                    "call_id": call_id,
                    "event_type": outcome,
                    "idempotency_key": f"IDEM_{call_id}_{outcome}",
                    "failure_reason": outcome,
                    "duration_sec": 0,
                }
            )
            return events

        # Event 3: ANSWERED
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.ANSWERED.value,
                "idempotency_key": f"IDEM_{call_id}_ANSWERED",
                "duration_sec": 0,
            }
        )

        # Event 4: CONNECTED (Agent bridged)
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.CONNECTED.value,
                "idempotency_key": f"IDEM_{call_id}_CONNECTED",
                "duration_sec": 0,
            }
        )

        # Event 5: COMPLETED
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.COMPLETED.value,
                "idempotency_key": f"IDEM_{call_id}_COMPLETED",
                "duration_sec": duration_sec,
            }
        )

        return events
