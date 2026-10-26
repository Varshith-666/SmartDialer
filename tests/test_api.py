"""End-to-End API Integration Tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from smart_dialer.api.app import app
from smart_dialer.config import settings
from smart_dialer.db.connection import init_db, get_db, transaction


@pytest.fixture(autouse=True)
def setup_api_test_db(tmp_path):
    test_db = str(tmp_path / "api_test.db")
    settings.DB_PATH = test_db
    init_db(test_db)

    with get_db(test_db) as conn:
        with transaction(conn) as cursor:
            # Seed campaign
            cursor.execute(
                "INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode) VALUES ('CMP_API', 'API Camp', 'PROGRESSIVE')"
            )
            # Seed 5 agents
            for i in range(5):
                cursor.execute(
                    f"INSERT INTO agents (agent_id, agent_name, status) VALUES ('AGT_API_{i}', 'Agent {i}', 'AVAILABLE')"
                )
            # Seed 10 borrowers
            for i in range(10):
                cursor.execute(
                    f"INSERT INTO borrowers (borrower_id, name, phone) VALUES ('BRW_API_{i}', 'Lead {i}', '98765432{i:02d}')"
                )
                cursor.execute(
                    f"INSERT INTO campaign_borrower_queue (campaign_id, borrower_id, status) VALUES ('CMP_API', 'BRW_API_{i}', 'QUEUED')"
                )
    yield test_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_api_health(client):
    """Test /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["database"] == "CONNECTED"
    assert data["total_agents"] == 5
    assert data["available_agents"] == 5


def test_api_agents_list_and_update(client):
    """Test /agents listing and status update."""
    res = client.get("/agents?status=AVAILABLE")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) == 5

    # Update agent status
    patch_res = client.patch(
        f"/agents/{agents[0]['agent_id']}/status",
        json={"status": "PAUSED"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "PAUSED"


def test_api_run_dialer_cycle(client):
    """Test /dialer/run-cycle endpoint."""
    res = client.post(
        "/dialer/run-cycle",
        json={"campaign_id": "CMP_API", "force_mode": "PROGRESSIVE"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["campaign_id"] == "CMP_API"
    assert data["mode"] == "PROGRESSIVE"
    assert data["calls_allocated"] > 0
    assert len(data["dispatched_call_ids"]) > 0


def test_api_provider_event_webhook(client):
    """Test /provider/events webhook with idempotency."""
    # First create a call record
    with get_db() as conn:
        with transaction(conn) as cursor:
            cursor.execute(
                "INSERT INTO calls (call_id, campaign_id, borrower_id, call_status) VALUES ('CALL_WH_1', 'CMP_API', 'BRW_API_0', 'INITIATED')"
            )

    evt = {
        "event_id": "EVT_1",
        "call_id": "CALL_WH_1",
        "event_type": "ANSWERED",
        "idempotency_key": "IDEM_WH_101",
    }
    res1 = client.post("/provider/events", json=evt)
    assert res1.status_code == 200
    assert res1.json()["status"] == "PROCESSED"

    # Send duplicate
    res2 = client.post("/provider/events", json=evt)
    assert res2.status_code == 200
    assert res2.json()["status"] == "DUPLICATE_IGNORED"


def test_api_metrics(client):
    """Test /metrics endpoint."""
    res = client.get("/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "call_metrics" in data
    assert "agent_metrics" in data
    assert "safety_controller_metrics" in data


def test_api_health_and_metrics_dashboards(client):
    """Test visual HTML dashboards and content negotiation for /health and /metrics."""
    # 1. Test /health with Accept: text/html returns HTML dashboard
    res_health_html = client.get("/health", headers={"Accept": "text/html,application/xhtml+xml"})
    assert res_health_html.status_code == 200
    assert "text/html" in res_health_html.headers["content-type"]
    assert "System Health &amp; Telemetry Diagnostics" in res_health_html.text or "System Health & Telemetry Diagnostics" in res_health_html.text
    assert "SmartDialer Diagnostic Probe" in res_health_html.text

    # 2. Test /health with format=json returns JSON
    res_health_json = client.get("/health?format=json")
    assert res_health_json.status_code == 200
    assert res_health_json.json()["status"] == "HEALTHY"

    # 3. Test dedicated /health/dashboard endpoint
    res_health_dash = client.get("/health/dashboard")
    assert res_health_dash.status_code == 200
    assert "text/html" in res_health_dash.headers["content-type"]

    # 4. Test /metrics with Accept: text/html returns HTML dashboard
    res_metrics_html = client.get("/metrics", headers={"Accept": "text/html,application/xhtml+xml"})
    assert res_metrics_html.status_code == 200
    assert "text/html" in res_metrics_html.headers["content-type"]
    assert "Telephony &amp; Operational Metrics" in res_metrics_html.text or "Telephony & Operational Metrics" in res_metrics_html.text
    assert "FCC COMPLIANCE ACTIVE" in res_metrics_html.text

    # 5. Test /metrics with format=json returns JSON
    res_metrics_json = client.get("/metrics?format=json")
    assert res_metrics_json.status_code == 200
    assert "call_metrics" in res_metrics_json.json()

    # 6. Test dedicated /metrics/dashboard endpoint
    res_metrics_dash = client.get("/metrics/dashboard")
    assert res_metrics_dash.status_code == 200
    assert "text/html" in res_metrics_dash.headers["content-type"]
