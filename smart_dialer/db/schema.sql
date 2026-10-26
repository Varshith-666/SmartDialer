-- SmartDialer SQLite Production Schema

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;

-- 1. Agents Table
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    employee_code TEXT,
    agent_name TEXT NOT NULL,
    vendor_id TEXT,
    team TEXT DEFAULT 'Default',
    status TEXT NOT NULL DEFAULT 'AVAILABLE',
    current_call_id TEXT NULL,
    reserved_at TIMESTAMP NULL,
    reservation_token TEXT NULL,
    reservation_expires_at TIMESTAMP NULL,
    connected_at TIMESTAMP NULL,
    last_status_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_reservation ON agents(reservation_expires_at) WHERE status = 'RESERVED';

-- 2. Borrowers Table
CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    city TEXT,
    state TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_borrowers_phone ON borrowers(phone);

-- 3. Telephony Vendors Table
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id TEXT PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    vendor_account_id TEXT,
    status TEXT DEFAULT 'ACTIVE',
    failure_rate REAL DEFAULT 0.05,
    latency_ms INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Campaigns Table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    channel TEXT DEFAULT 'VOICE',
    strategy_version TEXT DEFAULT 'v1',
    status TEXT DEFAULT 'ACTIVE',
    dialer_mode TEXT NOT NULL DEFAULT 'PROGRESSIVE',
    target_definition TEXT,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Campaign Borrower Queue Table
CREATE TABLE IF NOT EXISTS campaign_borrower_queue (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    borrower_id TEXT NOT NULL REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'QUEUED',
    reserved_at TIMESTAMP NULL,
    reservation_token TEXT NULL,
    reservation_expires_at TIMESTAMP NULL,
    attempts_count INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_campaign_borrower UNIQUE (campaign_id, borrower_id)
);

CREATE INDEX IF NOT EXISTS idx_cbq_fetch ON campaign_borrower_queue(campaign_id, status, priority, queue_id);
CREATE INDEX IF NOT EXISTS idx_cbq_reservation ON campaign_borrower_queue(reservation_expires_at) WHERE status = 'RESERVED';

-- 6. Calls Table
CREATE TABLE IF NOT EXISTS calls (
    call_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),
    borrower_id TEXT NOT NULL REFERENCES borrowers(borrower_id),
    agent_id TEXT NULL REFERENCES agents(agent_id),
    vendor_id TEXT,
    call_status TEXT NOT NULL DEFAULT 'QUEUED',
    initiated_at TIMESTAMP NULL,
    ringing_at TIMESTAMP NULL,
    answered_at TIMESTAMP NULL,
    connected_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    duration_sec INTEGER DEFAULT 0,
    failure_reason TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(call_status);
CREATE INDEX IF NOT EXISTS idx_calls_agent ON calls(agent_id);
CREATE INDEX IF NOT EXISTS idx_calls_campaign ON calls(campaign_id);
CREATE INDEX IF NOT EXISTS idx_calls_created ON calls(created_at);

-- 7. Call Events Table (Idempotent Event Log)
CREATE TABLE IF NOT EXISTS call_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id TEXT NOT NULL REFERENCES calls(call_id),
    event_type TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT,
    provider_event_id TEXT NULL,
    idempotency_key TEXT NULL UNIQUE,
    payload TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_call_events_call ON call_events(call_id);
CREATE INDEX IF NOT EXISTS idx_call_events_key ON call_events(idempotency_key);

-- 8. Agent State History Table (Audit Trail)
CREATE TABLE IF NOT EXISTS agent_state_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL REFERENCES agents(agent_id),
    from_state TEXT,
    to_state TEXT NOT NULL,
    call_id TEXT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_history_agent ON agent_state_history(agent_id, created_at);

-- 9. Safety Controller Audit Table
CREATE TABLE IF NOT EXISTS safety_controller_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT NOT NULL,
    dialer_mode TEXT NOT NULL,
    available_agents INTEGER NOT NULL,
    calls_proposed INTEGER NOT NULL,
    calls_approved INTEGER NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    current_answer_rate REAL,
    active_in_flight_calls INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_safety_audit_campaign ON safety_controller_audit(campaign_id, created_at);

-- 10. Key-Value Stats & Configuration Cache
CREATE TABLE IF NOT EXISTS dialer_stats_cache (
    stat_key TEXT PRIMARY KEY,
    stat_value REAL NOT NULL,
    meta_json TEXT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
