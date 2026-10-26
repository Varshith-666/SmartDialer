"""Abstract Base Telecom Provider Interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from smart_dialer.models.enums import ProviderEventType


class BaseTelecomProvider(ABC):
    """Abstract interface defining contract for telecom provider integrations."""

    @abstractmethod
    def initiate_call(
        self,
        call_id: str,
        phone_number: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send outbound call dispatch to carrier.
        Returns initial submission status or queued event sequence.
        """
        pass

    @abstractmethod
    def simulate_event_flow(
        self,
        call_id: str,
        target_outcome: Optional[str] = None,
        duration_sec: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Generate sequence of simulated telephony events for this call.
        """
        pass
