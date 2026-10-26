"""FastAPI main application entrypoint with lifespan startup/shutdown hooks."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from smart_dialer.config import settings
from smart_dialer.db.connection import init_db, get_db
from smart_dialer.engine.recovery import RecoveryEngine
from smart_dialer.api.routes_agents import router as agents_router
from smart_dialer.api.routes_campaigns import router as campaigns_router
from smart_dialer.api.routes_borrowers import router as borrowers_router
from smart_dialer.api.routes_calls import router as calls_router
from smart_dialer.api.routes_dialer import router as dialer_router
from smart_dialer.api.routes_provider import router as provider_router
from smart_dialer.api.routes_metrics import router as metrics_router
from smart_dialer.api.dashboard import DASHBOARD_HTML


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler: initializes DB and runs crash recovery on startup."""
    # 1. Initialize schema
    init_db()

    # 2. Run startup crash reconciliation (Mandatory Scenario 1)
    with get_db() as conn:
        recovery_summary = RecoveryEngine.recover_on_startup(conn)
        print(f"[SmartDialer Startup] Database initialized. Crash Recovery: {recovery_summary}")

    yield

    print("[SmartDialer Shutdown] Dialer shutdown complete.")


app = FastAPI(
    title="SmartDialer Production Backend API",
    description="High-concurrency Progressive & Predictive Outbound Dialer Engine with Independent Safety Controller.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(metrics_router)
app.include_router(agents_router)
app.include_router(campaigns_router)
app.include_router(borrowers_router)
app.include_router(calls_router)
app.include_router(dialer_router)
app.include_router(provider_router)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return {
            "service": "SmartDialer API",
            "version": "1.0.0",
            "status": "ONLINE",
            "docs_url": "/docs",
            "dashboard_url": "/dashboard",
        }
    return HTMLResponse(content=DASHBOARD_HTML)



@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)

