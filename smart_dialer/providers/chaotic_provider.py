"""Chaotic Telecom Provider: Simulates delays, timeouts, duplicates, and out-of-order events."""

import random
import time
import uuid
from typing import Dict, Any, List, Optional
from smart_dialer.providers.base import BaseTelecomProvider
from smart_dialer.models.enums import ProviderEventType


class ProviderTimeoutError(Exception):
    """Raised when telecom carrier times out."""
    pass


class ChaoticTelecomProvider(BaseTelecomProvider):
    """
    Unreliable, chaotic telecom provider used for stress testing resilience.
    Features:
      1. Duplicate events (e.g. 2x ANSWERED).
      2. Out-of-order delivery (e.g. COMPLETED before ANSWERED).
      3. Artificial timeouts and 500 error drops.
      4. Severe network latency jitter.
    """

    def __init__(
        self,
        failure_rate: float = 0.20,
        answer_rate: float = 0.50,
        duplicate_event_rate: float = 0.30,
        out_of_order_rate: float = 0.25,
        timeout_rate: float = 0.10,
        latency_ms_range: tuple[int, int] = (100, 800),
    ):
        self.failure_rate = failure_rate
        self.answer_rate = answer_rate
        self.duplicate_event_rate = duplicate_event_rate
        self.out_of_order_rate = out_of_order_rate
        self.timeout_rate = timeout_rate
        self.latency_ms_range = latency_ms_range

    def initiate_call(
        self,
        call_id: str,
        phone_number: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Simulate carrier initiation with potential timeouts or network drops."""
        # Check timeout injection
        if random.random() < self.timeout_rate:
            raise ProviderTimeoutError(f"Carrier gateway timed out after {self.latency_ms_range[1]}ms for call {call_id}.")

        # Check random failure
        if random.random() < self.failure_rate:
            return {
                "status": "REJECTED",
                "provider": "ChaoticTelecom",
                "error": "CIRCUIT_RESET_BY_PEER",
                "call_id": call_id,
            }

        return {
            "status": "ACCEPTED",
            "provider": "ChaoticTelecom",
            "carrier_ref": f"CHAOS_{uuid.uuid4().hex[:10]}",
            "call_id": call_id,
        }

    def simulate_event_flow(
        self,
        call_id: str,
        target_outcome: Optional[str] = None,
        duration_sec: int = 90,
        force_duplicate_answered: bool = False,
        force_out_of_order_completed: bool = False,
    ) -> List[Dict[str, Any]]:
        """Generate chaotic, potentially corrupted or reordered carrier webhook events."""
        events: List[Dict[str, Any]] = []

        # 1. INITIATED
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.INITIATED.value,
                "idempotency_key": f"IDEM_{call_id}_INITIATED",
                "duration_sec": 0,
            }
        )

        # 2. RINGING
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.RINGING.value,
                "idempotency_key": f"IDEM_{call_id}_RINGING",
                "duration_sec": 0,
            }
        )

        # Scenario 5: COMPLETED arrives before ANSWERED
        should_reverse = force_out_of_order_completed or (random.random() < self.out_of_order_rate)
        if should_reverse:
            # Deliver COMPLETED immediately!
            events.append(
                {
                    "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                    "call_id": call_id,
                    "event_type": ProviderEventType.COMPLETED.value,
                    "idempotency_key": f"IDEM_{call_id}_COMPLETED",
                    "duration_sec": duration_sec,
                }
            )
            # Late-arriving ANSWERED
            events.append(
                {
                    "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                    "call_id": call_id,
                    "event_type": ProviderEventType.ANSWERED.value,
                    "idempotency_key": f"IDEM_{call_id}_ANSWERED",
                    "duration_sec": 0,
                }
            )
            return events

        # Standard Answered flow
        answered_event = {
            "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
            "call_id": call_id,
            "event_type": ProviderEventType.ANSWERED.value,
            "idempotency_key": f"IDEM_{call_id}_ANSWERED",
            "duration_sec": 0,
        }
        events.append(answered_event)

        # Scenario 4: Duplicate ANSWERED events
        if force_duplicate_answered or (random.random() < self.duplicate_event_rate):
            # Duplicate event with same idempotency key or slightly modified carrier payload
            duplicate_event = {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}_DUP",
                "call_id": call_id,
                "event_type": ProviderEventType.ANSWERED.value,
                "idempotency_key": f"IDEM_{call_id}_ANSWERED",  # Same idempotency key!
                "duration_sec": 0,
            }
            events.append(duplicate_event)

        # CONNECTED
        events.append(
            {
                "event_id": f"EVT_{uuid.uuid4().hex[:8]}",
                "call_id": call_id,
                "event_type": ProviderEventType.CONNECTED.value,
                "idempotency_key": f"IDEM_{call_id}_CONNECTED",
                "duration_sec": 0,
            }
        )

        # COMPLETED
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
