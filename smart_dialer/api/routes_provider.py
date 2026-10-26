"""FastAPI routes for Telecom Provider Webhook and Configuration."""

from fastapi import APIRouter, HTTPException
from smart_dialer.config import settings
from smart_dialer.db.connection import get_db
from smart_dialer.models.schemas import ProviderEventWebhookPayload, ProviderConfigRequest
from smart_dialer.engine.event_processor import EventProcessor

router = APIRouter(prefix="/provider", tags=["Telecom Provider"])


@router.post("/events")
def receive_provider_event(payload: ProviderEventWebhookPayload):
    """
    Ingest telephony event webhook from carrier.
    Handles duplicate events (idempotency key), out-of-order delivery, and terminal transitions.
    """
    with get_db() as conn:
        try:
            return EventProcessor.process_event(
                conn,
                {
                    "call_id": payload.call_id,
                    "event_type": payload.event_type.value,
                    "idempotency_key": payload.idempotency_key,
                    "duration_sec": payload.duration_sec,
                    "failure_reason": payload.failure_reason,
                    "metadata": payload.metadata,
                },
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Provider event error: {str(e)}")


@router.get("/config")
def get_provider_config():
    """Inspect current mock telecom provider settings."""
    return {
        "active_provider": settings.PROVIDER_TYPE,
        "failure_rate": settings.PROVIDER_FAILURE_RATE,
        "latency_min_ms": settings.PROVIDER_LATENCY_MIN_MS,
        "latency_max_ms": settings.PROVIDER_LATENCY_MAX_MS,
    }


@router.post("/config")
def update_provider_config(config: ProviderConfigRequest):
    """Dynamically switch between reliable and chaotic telecom providers."""
    settings.PROVIDER_TYPE = config.provider_type.value
    if config.failure_rate is not None:
        settings.PROVIDER_FAILURE_RATE = config.failure_rate
    if config.latency_min_ms is not None:
        settings.PROVIDER_LATENCY_MIN_MS = config.latency_min_ms
    if config.latency_max_ms is not None:
        settings.PROVIDER_LATENCY_MAX_MS = config.latency_max_ms

    return {
        "status": "CONFIG_UPDATED",
        "active_provider": settings.PROVIDER_TYPE,
        "failure_rate": settings.PROVIDER_FAILURE_RATE,
    }
