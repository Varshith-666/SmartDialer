"""FastAPI routes for Health Checks and Real-Time Operational Metrics."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from smart_dialer.config import settings
from smart_dialer.db.connection import get_db
from smart_dialer.api.metrics_dashboard import (
    render_metrics_dashboard,
    render_health_dashboard,
)

router = APIRouter(tags=["Health & Metrics"])


def _should_render_html(request: Request, format_param: Optional[str] = None) -> bool:
    """Determine whether to render the visual interactive HTML dashboard or raw JSON."""
    if format_param == "html":
        return True
    if format_param == "json":
        return False
    accept = request.headers.get("accept", "")
    # Browsers send 'text/html,application/xhtml+xml,...'
    # Automated scripts, cURL, and TestClient send '*/*' or 'application/json'
    return "text/html" in accept


def _compute_health_data() -> dict:
    """Fetch current system health telemetry from DB and runtime settings."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as c FROM agents")
        total_agents = cursor.fetchone()["c"]

        cursor.execute("SELECT COUNT(*) as c FROM agents WHERE status = 'AVAILABLE'")
        avail_agents = cursor.fetchone()["c"]

        cursor.execute("SELECT COUNT(*) as c FROM campaign_borrower_queue WHERE status = 'QUEUED'")
        queued_leads = cursor.fetchone()["c"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM calls WHERE call_status IN ('INITIATED', 'RINGING', 'ANSWERED')"
        )
        in_flight = cursor.fetchone()["c"]

    return {
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "CONNECTED",
        "environment": settings.ENV,
        "active_provider": settings.PROVIDER_TYPE,
        "total_agents": total_agents,
        "available_agents": avail_agents,
        "queued_borrowers": queued_leads,
        "in_flight_calls": in_flight,
    }


def _compute_metrics_data() -> dict:
    """Calculate real-time operational dialer metrics."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Call state counts
        cursor.execute(
            """
            SELECT call_status, COUNT(*) as cnt
            FROM calls
            GROUP BY call_status
            """
        )
        call_counts = {r["call_status"]: r["cnt"] for r in cursor.fetchall()}

        # Agent state counts
        cursor.execute(
            """
            SELECT status, COUNT(*) as cnt
            FROM agents
            GROUP BY status
            """
        )
        agent_counts = {r["status"]: r["cnt"] for r in cursor.fetchall()}

        # Safety Controller Decisions
        cursor.execute(
            """
            SELECT decision, COUNT(*) as cnt
            FROM safety_controller_audit
            GROUP BY decision
            """
        )
        safety_counts = {r["decision"]: r["cnt"] for r in cursor.fetchall()}

    total_initiated = sum(call_counts.values())
    total_answered = (
        call_counts.get("ANSWERED", 0)
        + call_counts.get("CONNECTED", 0)
        + call_counts.get("COMPLETED", 0)
    )
    total_completed = call_counts.get("COMPLETED", 0)
    total_failed = call_counts.get("FAILED", 0)

    # Calculate KPIs
    ans_rate = (total_answered / total_initiated * 100.0) if total_initiated > 0 else 0.0

    total_agents = sum(agent_counts.values())
    active_agents = (
        agent_counts.get("CONNECTED", 0)
        + agent_counts.get("WRAP_UP", 0)
        + agent_counts.get("DIALING", 0)
    )
    agent_util = (active_agents / total_agents * 100.0) if total_agents > 0 else 0.0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "call_metrics": {
            "total_calls": total_initiated,
            "answered_calls": total_answered,
            "completed_calls": total_completed,
            "failed_calls": total_failed,
            "breakdown": call_counts,
            "answer_rate_pct": round(ans_rate, 2),
        },
        "agent_metrics": {
            "total_agents": total_agents,
            "available": agent_counts.get("AVAILABLE", 0),
            "connected": agent_counts.get("CONNECTED", 0),
            "dialing": agent_counts.get("DIALING", 0),
            "reserved": agent_counts.get("RESERVED", 0),
            "wrap_up": agent_counts.get("WRAP_UP", 0),
            "paused": agent_counts.get("PAUSED", 0),
            "offline": agent_counts.get("OFFLINE", 0),
            "utilization_pct": round(agent_util, 2),
        },
        "safety_controller_metrics": {
            "total_evaluations": sum(safety_counts.values()),
            "approvals": safety_counts.get("APPROVE", 0),
            "reductions": safety_counts.get("REDUCE", 0),
            "rejections": safety_counts.get("REJECT", 0),
            "force_progressive_fallbacks": safety_counts.get("FORCE_PROGRESSIVE", 0),
        },
    }


@router.get("/health")
def health_check(
    request: Request,
    format: Optional[str] = Query(None, description="Output format: 'json' or 'html'"),
):
    """System health check and live agent/queue summary. Returns visual dashboard for browsers, JSON for API."""
    data = _compute_health_data()
    if _should_render_html(request, format):
        return HTMLResponse(content=render_health_dashboard(data))
    return data


@router.get("/health/dashboard", response_class=HTMLResponse)
def health_dashboard():
    """Dedicated interactive Health & Diagnostics dashboard view."""
    data = _compute_health_data()
    return HTMLResponse(content=render_health_dashboard(data))


@router.get("/metrics")
def get_metrics(
    request: Request,
    format: Optional[str] = Query(None, description="Output format: 'json' or 'html'"),
):
    """Real-time operational dialer metrics. Returns visual dashboard for browsers, JSON for API."""
    data = _compute_metrics_data()
    if _should_render_html(request, format):
        return HTMLResponse(content=render_metrics_dashboard(data))
    return data


@router.get("/metrics/dashboard", response_class=HTMLResponse)
def metrics_dashboard():
    """Dedicated interactive Telephony Metrics dashboard view."""
    data = _compute_metrics_data()
    return HTMLResponse(content=render_metrics_dashboard(data))

