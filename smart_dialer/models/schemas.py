"""Pydantic schemas for API requests, responses, and validation."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from smart_dialer.models.enums import (
    AgentState,
    CallState,
    DialerMode,
    ProviderEventType,
    ProviderType,
    SafetyDecision,
)


class AgentBase(BaseModel):
    agent_id: str
    employee_code: Optional[str] = None
    agent_name: str
    vendor_id: Optional[str] = None
    team: Optional[str] = "Default"
    status: AgentState = AgentState.AVAILABLE


class AgentUpdateStatusRequest(BaseModel):
    status: AgentState


class BulkAgentStatusUpdateRequest(BaseModel):
    agent_ids: Optional[List[str]] = None
    count: Optional[int] = None
    target_status: AgentState


class BorrowerBase(BaseModel):
    borrower_id: str
    name: str
    phone: str
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class BorrowerImportItem(BaseModel):
    borrower_id: str
    name: str
    phone: str
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class CampaignCreateRequest(BaseModel):
    campaign_id: str
    campaign_name: str
    channel: str = "VOICE"
    strategy_version: str = "v1"
    dialer_mode: DialerMode = DialerMode.PROGRESSIVE
    target_definition: Optional[str] = None


class CampaignUpdateModeRequest(BaseModel):
    dialer_mode: DialerMode


class ProviderConfigRequest(BaseModel):
    provider_type: ProviderType
    failure_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    latency_min_ms: Optional[int] = Field(default=None, ge=0)
    latency_max_ms: Optional[int] = Field(default=None, ge=0)


class ProviderEventWebhookPayload(BaseModel):
    event_id: str
    call_id: str
    event_type: ProviderEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_sec: Optional[int] = 0
    failure_reason: Optional[str] = None
    idempotency_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DialCycleRunRequest(BaseModel):
    campaign_id: str
    force_mode: Optional[DialerMode] = None


class SafetyDecisionLog(BaseModel):
    decision: SafetyDecision
    reason: str
    proposed_calls: int
    approved_calls: int
    overdial_ratio: float
    available_agents: int


class DialerCycleResult(BaseModel):
    campaign_id: str
    mode: DialerMode
    cycle_timestamp: datetime
    available_agents: int
    active_in_flight_calls: int
    proposed_calls: int
    safety_decision: SafetyDecisionLog
    calls_initiated: int
    call_ids: List[str]


class SystemHealthResponse(BaseModel):
    status: str
    database: str
    environment: str
    active_provider: str
    total_agents: int
    available_agents: int
    queued_borrowers: int
    in_flight_calls: int


class MetricSummaryResponse(BaseModel):
    timestamp: datetime
    total_calls_initiated: int
    total_calls_answered: int
    total_calls_connected: int
    total_calls_completed: int
    total_calls_failed: int
    total_calls_abandoned: int
    answer_rate_pct: float
    abandon_rate_pct: float
    agent_utilization_pct: float
    safety_approvals: int
    safety_reductions: int
    safety_rejections: int
    safety_fallbacks: int
