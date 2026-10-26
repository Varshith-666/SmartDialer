"""Interactive Live Web Dashboard for SmartDialer."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDialer — Live Telephony Operations Console</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #080b11;
            --bg-card: rgba(15, 21, 34, 0.82);
            --bg-card-hover: rgba(22, 31, 50, 0.9);
            --bg-input: #0b101c;
            --border-card: rgba(255, 255, 255, 0.08);
            --border-card-hover: rgba(255, 255, 255, 0.16);
            --border-active: rgba(99, 102, 241, 0.5);
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.4);
            --accent-green: #10b981;
            --accent-green-glow: rgba(16, 185, 129, 0.35);
            --accent-amber: #f59e0b;
            --accent-cyan: #06b6d4;
            --accent-purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(ellipse at 50% 0%, #151e33 0%, var(--bg-base) 75%);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.5;
            padding-bottom: 60px;
        }

        .container {
            max-width: 1360px;
            margin: 0 auto;
            padding: 0 24px;
        }

        /* Top Navigation */
        header {
            border-bottom: 1px solid var(--border-card);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 50;
            background: rgba(8, 11, 17, 0.88);
        }

        .nav-inner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 72px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none;
            color: var(--text-main);
        }

        .brand-icon {
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 18px var(--primary-glow);
        }

        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .brand-badge {
            font-size: 0.6875rem;
            padding: 2px 7px;
            border-radius: 9999px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            font-weight: 600;
        }

        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--text-muted);
            letter-spacing: 0.02em;
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 9999px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.28);
            color: #34d399;
            font-size: 0.8125rem;
            font-weight: 600;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10b981;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 9px;
            font-size: 0.875rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid transparent;
        }

        .btn-outline {
            background: rgba(255, 255, 255, 0.03);
            border-color: var(--border-card);
            color: var(--text-main);
        }

        .btn-outline:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--border-card-hover);
            transform: translateY(-1px);
        }

        /* Prominent White Primary Button */
        .btn-hero {
            background: #ffffff;
            color: #0b0f19;
            font-weight: 700;
            font-size: 0.9375rem;
            padding: 12px 22px;
            border-radius: 10px;
            box-shadow: 0 4px 18px rgba(255, 255, 255, 0.18);
            width: 100%;
        }

        .btn-hero:hover {
            background: #f1f5f9;
            transform: translateY(-1px);
            box-shadow: 0 6px 24px rgba(255, 255, 255, 0.28);
        }

        .btn-hero:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .btn-sm {
            padding: 5px 12px;
            font-size: 0.78125rem;
            border-radius: 7px;
        }

        .hero-banner {
            padding: 30px 0 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .hero-title {
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-desc {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 4px;
        }

        /* KPI Stat Cards Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: 1.15fr 1fr 1fr 1fr 1fr;
            gap: 14px;
            margin-bottom: 24px;
        }

        @media (max-width: 1100px) {
            .kpi-grid {
                grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            }
        }

        .kpi-card {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-card);
            border-radius: 14px;
            padding: 18px 20px;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .kpi-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--border-card-hover);
            transform: translateY(-2px);
        }

        /* Distinctive Light Hero Card for Available Agents */
        .kpi-card-hero {
            background: #ffffff;
            color: #0b0f19;
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25), 0 0 20px rgba(255, 255, 255, 0.08);
        }

        .kpi-card-hero:hover {
            background: #f8fafc;
            border-color: #ffffff;
        }

        .kpi-card-hero .kpi-label {
            color: #475569;
        }

        .kpi-card-hero .kpi-value {
            color: #090d16;
        }

        .kpi-card-hero .kpi-sub {
            color: #64748b;
        }

        .kpi-label {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.15rem;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.03em;
            line-height: 1.1;
        }

        .kpi-sub {
            margin-top: 6px;
            font-size: 0.78125rem;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .kpi-pill {
            display: inline-block;
            font-size: 0.6875rem;
            font-weight: 700;
            padding: 1px 7px;
            border-radius: 9999px;
        }

        .pill-green { background: rgba(16, 185, 129, 0.15); color: #10b981; }
        .pill-blue { background: rgba(6, 182, 212, 0.15); color: #06b6d4; }
        .pill-purple { background: rgba(168, 85, 247, 0.15); color: #a855f7; }

        /* Main Workspace Split Grid */
        .workspace-grid {
            display: grid;
            grid-template-columns: 460px 1fr;
            gap: 20px;
        }

        @media (max-width: 1024px) {
            .workspace-grid {
                grid-template-columns: 1fr;
            }
        }

        .panel-card {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 22px;
        }

        .panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-card);
        }

        .panel-title {
            font-size: 1.0625rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Form Inputs */
        .form-group {
            margin-bottom: 16px;
        }

        .form-label {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8125rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 7px;
        }

        .form-hint {
            font-size: 0.71875rem;
            color: var(--text-dim);
            font-weight: 400;
        }

        .form-select {
            width: 100%;
            padding: 11px 14px;
            background: var(--bg-input);
            border: 1px solid var(--border-card);
            border-radius: 9px;
            color: var(--text-main);
            font-size: 0.875rem;
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
        }

        .form-select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-glow);
        }

        .button-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 10px;
        }

        /* Terminal Console Output */
        .console-wrap {
            margin-top: 18px;
        }

        .console-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }

        .console-title {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .console-output {
            background: #04070e;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 11px;
            padding: 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8125rem;
            color: #38bdf8;
            height: 235px;
            overflow-y: auto;
            white-space: pre-wrap;
            line-height: 1.55;
        }

        .console-output::-webkit-scrollbar {
            width: 6px;
        }
        .console-output::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
        }

        /* Right Panel: Segmented Tabs & Activity Deck */
        .tabs-header {
            display: flex;
            align-items: center;
            gap: 4px;
            background: #0b101c;
            padding: 4px;
            border-radius: 9px;
            border: 1px solid var(--border-card);
        }

        .tab-btn {
            padding: 6px 14px;
            font-size: 0.8125rem;
            font-weight: 600;
            color: var(--text-muted);
            background: transparent;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .tab-btn.active {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-weight: 700;
        }

        .filter-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            gap: 10px;
        }

        .filter-pills {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .filter-pill {
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-card);
            color: var(--text-muted);
            cursor: pointer;
        }

        .filter-pill.active {
            background: rgba(99, 102, 241, 0.2);
            border-color: rgba(99, 102, 241, 0.4);
            color: #a5b4fc;
        }

        .search-box {
            background: var(--bg-input);
            border: 1px solid var(--border-card);
            border-radius: 7px;
            padding: 5px 10px;
            font-size: 0.78125rem;
            color: var(--text-main);
            outline: none;
            width: 170px;
        }

        /* Data Tables */
        .table-wrap {
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid var(--border-card);
            max-height: 480px;
            overflow-y: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.84375rem;
        }

        th {
            background: #090e19;
            padding: 10px 14px;
            font-weight: 600;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-card);
            position: sticky;
            top: 0;
            z-index: 5;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        td {
            padding: 10px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        tr:hover td {
            background: rgba(255, 255, 255, 0.02);
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 0.71875rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        .badge-green { background: rgba(16, 185, 129, 0.14); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.25); }
        .badge-cyan { background: rgba(6, 182, 212, 0.14); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.25); }
        .badge-amber { background: rgba(245, 158, 11, 0.14); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.25); }
        .badge-gray { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.2); }
        .badge-purple { background: rgba(168, 85, 247, 0.14); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.25); }

        .footer-note {
            margin-top: 14px;
            font-size: 0.78125rem;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .footer-note a {
            color: #818cf8;
            text-decoration: none;
            font-weight: 600;
        }
        .footer-note a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <!-- Top Sticky Header -->
    <header>
        <div class="container nav-inner">
            <a href="/" class="brand">
                <div class="brand-icon">📞</div>
                <div>
                    <div class="brand-title">
                        SmartDialer Engine
                        <span class="brand-badge">WAL ACID</span>
                    </div>
                    <div class="brand-subtitle">Progressive & Predictive Dialer • Non-Bypassable Safety Controller</div>
                </div>
            </a>
            <div class="nav-links">
                <div class="status-badge">
                    <span class="pulse-dot"></span>
                    <span id="sys-status">SERVER ONLINE</span>
                </div>
                <a href="/metrics" target="_blank" class="btn btn-outline btn-sm">📊 Telephony Metrics</a>
                <a href="/health" target="_blank" class="btn btn-outline btn-sm">💓 Health Diagnostics</a>
                <a href="/docs" target="_blank" class="btn btn-outline btn-sm">📖 Swagger UI</a>
                <button class="btn btn-outline btn-sm" onclick="refreshDashboard(true)" title="Force Sync">↻</button>
            </div>
        </div>
    </header>

    <main class="container">
        <!-- Hero Header -->
        <section class="hero-banner">
            <div>
                <h1 class="hero-title">Live Telephony Operations Console</h1>
                <p class="hero-desc">
                    Real-time progressive and predictive pacing, Erlang-C risk boundaries, FCC 3% abandon rate safety enforcement, and carrier dispatch.
                </p>
            </div>
        </section>

        <!-- KPI Metrics Grid (Hero Card on Available Agents) -->
        <div class="kpi-grid">
            <!-- Hero Card: Available Agents -->
            <div class="kpi-card kpi-card-hero">
                <div class="kpi-label">
                    <span>Available Agents</span>
                    <span class="kpi-pill pill-green">● READY</span>
                </div>
                <div class="kpi-value" id="kpi-available">...</div>
                <div class="kpi-sub">Wrap-up: <strong id="kpi-wrapup">0</strong> • Total: <strong id="kpi-total">855</strong></div>
            </div>

            <!-- Card 2: Queued Leads -->
            <div class="kpi-card">
                <div class="kpi-label">
                    <span>Queued Leads</span>
                    <span class="kpi-pill pill-blue">FIFO PRIORITY</span>
                </div>
                <div class="kpi-value" id="kpi-queue">...</div>
                <div class="kpi-sub">Pending campaign allocation</div>
            </div>

            <!-- Card 3: Calls & Answer Rate -->
            <div class="kpi-card">
                <div class="kpi-label">
                    <span>Total Calls</span>
                    <span style="color: #38bdf8;">Carrier Mock</span>
                </div>
                <div class="kpi-value" id="kpi-calls">...</div>
                <div class="kpi-sub">Answered: <span id="kpi-answered">0</span> (<span id="kpi-answer-rate" style="color: #34d399; font-weight: 600;">0.0%</span>)</div>
            </div>

            <!-- Card 4: Safety Controller -->
            <div class="kpi-card">
                <div class="kpi-label">
                    <span>Safety Controller</span>
                    <span class="kpi-pill pill-purple">GATEKEEPER</span>
                </div>
                <div class="kpi-value" id="kpi-safety" style="font-size: 1.65rem; color: #c084fc;">APPROVED</div>
                <div class="kpi-sub">FCC 3% Ceiling • Overdial &lt; 2.5x</div>
            </div>

            <!-- Card 5: Carrier Mode -->
            <div class="kpi-card">
                <div class="kpi-label">
                    <span>Carrier Mode</span>
                    <span id="carrier-pill" class="kpi-pill pill-blue">5% FAIL</span>
                </div>
                <div class="kpi-value" id="kpi-provider" style="font-size: 1.65rem; color: #22d3ee;">RELIABLE</div>
                <div class="kpi-sub">Lat: 50-200ms • Dynamic Mock</div>
            </div>
        </div>

        <!-- Main Workspace Deck Grid -->
        <div class="workspace-grid">
            <!-- Left Column: Dialer Controls -->
            <div class="panel-card">
                <div class="panel-header">
                    <div class="panel-title">⚡ Dialer Execution Deck</div>
                    <span class="badge badge-purple">Real-Time Core</span>
                </div>

                <div class="form-group">
                    <div class="form-label">
                        <span>Active Campaign</span>
                        <span class="form-hint" id="campaign-info">Strategy: VOICE</span>
                    </div>
                    <select id="campaign-select" class="form-select" onchange="onCampaignChange()">
                        <option value="CMP0000108">CMP0000108 - NPA_RECOVERY (VOICE)</option>
                        <option value="CMP0000101">CMP0000101 - 30DPD_W1 (FIELD)</option>
                        <option value="CMP0000110">CMP0000110 - DIGITAL_FOLLOWUP (VOICE)</option>
                        <option value="CMP0000117">CMP0000117 - BOUNCE (VOICE)</option>
                    </select>
                </div>

                <div class="form-group">
                    <div class="form-label">
                        <span>Pacing Strategy</span>
                        <span class="form-hint">Determinism vs Throughput</span>
                    </div>
                    <select id="mode-select" class="form-select">
                        <option value="PROGRESSIVE">PROGRESSIVE (1:1 Strict Capacity Allocation)</option>
                        <option value="PREDICTIVE">PREDICTIVE (Statistical Overdial Multiplier)</option>
                    </select>
                </div>

                <!-- Prominent Primary Action Button (Matches Screenshot Thumbnail) -->
                <div style="margin-top: 14px;">
                    <button id="btn-run-cycle" class="btn btn-hero" onclick="triggerDialCycle()">
                        🚀 Trigger Dial Cycle
                    </button>
                </div>

                <!-- Secondary Control Actions -->
                <div class="button-grid">
                    <button class="btn btn-outline btn-sm" onclick="enqueueFreshLeads()" title="Replenish Queue">
                        📥 Enqueue +100 Leads
                    </button>
                    <button class="btn btn-outline btn-sm" onclick="resetWrapUpAgents()" title="Free Wrap-up Agents">
                        🔄 Free Wrap-up
                    </button>
                    <button class="btn btn-outline btn-sm" onclick="toggleProvider()" title="Switch Mock Carrier">
                        📶 Toggle Carrier
                    </button>
                    <button class="btn btn-outline btn-sm" onclick="testQuorumDrop()" title="Simulate Agent Drop for Scenario 3">
                        🛡️ Test Drop (100→60)
                    </button>
                </div>

                <!-- Live Dispatch Log Terminal -->
                <div class="console-wrap">
                    <div class="console-header">
                        <span class="console-title">Live Dispatch Stream</span>
                        <button class="btn btn-outline" style="padding: 2px 8px; font-size: 0.6875rem;" onclick="clearLog()">Clear</button>
                    </div>
                    <div class="console-output" id="cycle-log">Operations console ready. Click "Trigger Dial Cycle" to dispatch live calls...</div>
                </div>
            </div>

            <!-- Right Column: Agent Pool Roster & Live Call Stream -->
            <div class="panel-card">
                <div class="panel-header">
                    <div class="panel-title">👥 Operations Activity</div>
                    <!-- Segmented Tab Switcher (Matches Screenshot Thumbnail Toggle) -->
                    <div class="tabs-header">
                        <button id="tab-agents" class="tab-btn active" onclick="switchTab('agents')">Agent Pool (855)</button>
                        <button id="tab-calls" class="tab-btn" onclick="switchTab('calls')">Live Calls</button>
                    </div>
                </div>

                <!-- Agents Tab View -->
                <div id="view-agents">
                    <div class="filter-bar">
                        <div class="filter-pills">
                            <span class="filter-pill active" onclick="filterAgents('ALL', this)">All</span>
                            <span class="filter-pill" onclick="filterAgents('AVAILABLE', this)">Available</span>
                            <span class="filter-pill" onclick="filterAgents('CONNECTED', this)">Connected</span>
                            <span class="filter-pill" onclick="filterAgents('WRAP_UP', this)">Wrap-Up</span>
                            <span class="filter-pill" onclick="filterAgents('OFFLINE', this)">Offline</span>
                        </div>
                        <input type="text" id="agent-search" class="search-box" placeholder="Search agent name/ID..." oninput="onSearchAgents()">
                    </div>

                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Agent ID</th>
                                    <th>Agent Name</th>
                                    <th>Team</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="agent-table-body">
                                <tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 30px;">Loading agents...</td></tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="footer-note">
                        <span>Showing filtered active agents</span>
                        <a href="/agents?limit=100" target="_blank">Full Agent Roster API →</a>
                    </div>
                </div>

                <!-- Calls Tab View -->
                <div id="view-calls" style="display: none;">
                    <div class="filter-bar">
                        <div class="filter-pills">
                            <span class="filter-pill active" onclick="filterCalls('ALL', this)">All Calls</span>
                            <span class="filter-pill" onclick="filterCalls('ANSWERED', this)">Answered</span>
                            <span class="filter-pill" onclick="filterCalls('COMPLETED', this)">Completed</span>
                            <span class="filter-pill" onclick="filterCalls('FAILED', this)">Failed</span>
                        </div>
                        <button class="btn btn-outline btn-sm" onclick="fetchCalls()">↻ Refresh Calls</button>
                    </div>

                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Call ID</th>
                                    <th>Campaign</th>
                                    <th>Status</th>
                                    <th>Duration</th>
                                    <th>Created At</th>
                                </tr>
                            </thead>
                            <tbody id="call-table-body">
                                <tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 30px;">Loading calls...</td></tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="footer-note">
                        <span>Real-time calls recorded with idempotency keys</span>
                        <a href="/calls?limit=50" target="_blank">Calls Telemetry API →</a>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        let cachedAgents = [];
        let currentStatusFilter = 'ALL';
        let currentActiveTab = 'agents';

        function logMessage(msg) {
            const logBox = document.getElementById('cycle-log');
            const time = new Date().toLocaleTimeString();
            logBox.innerText = `[${time}] ${msg}\\n` + logBox.innerText;
        }

        function clearLog() {
            document.getElementById('cycle-log').innerText = '';
        }

        function switchTab(tab) {
            currentActiveTab = tab;
            document.getElementById('tab-agents').classList.toggle('active', tab === 'agents');
            document.getElementById('tab-calls').classList.toggle('active', tab === 'calls');
            document.getElementById('view-agents').style.display = tab === 'agents' ? 'block' : 'none';
            document.getElementById('view-calls').style.display = tab === 'calls' ? 'block' : 'none';
            if (tab === 'calls') {
                fetchCalls();
            }
        }

        async function fetchMetrics() {
            try {
                const resHealth = await fetch('/health?format=json');
                if (resHealth.ok) {
                    const health = await resHealth.json();
                    document.getElementById('sys-status').innerText = 'SERVER ONLINE (' + health.database + ')';
                    document.getElementById('kpi-available').innerText = health.available_agents;
                    document.getElementById('kpi-total').innerText = health.total_agents;
                    document.getElementById('kpi-queue').innerText = health.queued_borrowers.toLocaleString();
                    const provider = (health.active_provider || 'reliable').toUpperCase();
                    document.getElementById('kpi-provider').innerText = provider;
                    document.getElementById('carrier-pill').innerText = provider === 'RELIABLE' ? '5% FAIL' : 'CHAOS / 20% FAIL';
                }

                const resMetrics = await fetch('/metrics?format=json');
                if (resMetrics.ok) {
                    const metrics = await resMetrics.json();
                    document.getElementById('kpi-calls').innerText = metrics.call_metrics.total_calls.toLocaleString();
                    document.getElementById('kpi-answered').innerText = metrics.call_metrics.answered_calls.toLocaleString();
                    document.getElementById('kpi-answer-rate').innerText = metrics.call_metrics.answer_rate_pct.toFixed(1) + '%';
                    document.getElementById('kpi-wrapup').innerText = metrics.agent_metrics.wrap_up || 0;
                }
            } catch (err) {
                document.getElementById('sys-status').innerText = 'OFFLINE / RECONNECTING';
                console.error("Metrics poll error:", err);
            }
        }

        async function fetchAgents() {
            try {
                const res = await fetch('/agents?limit=120');
                if (!res.ok) return;
                cachedAgents = await res.json();
                renderAgents();
            } catch (err) {
                console.error("Agents fetch error:", err);
            }
        }

        function renderAgents() {
            const tbody = document.getElementById('agent-table-body');
            const search = (document.getElementById('agent-search').value || '').toLowerCase();
            
            let filtered = cachedAgents;
            if (currentStatusFilter !== 'ALL') {
                filtered = filtered.filter(a => a.status === currentStatusFilter);
            }
            if (search) {
                filtered = filtered.filter(a => 
                    a.agent_id.toLowerCase().includes(search) || 
                    a.agent_name.toLowerCase().includes(search) ||
                    (a.team && a.team.toLowerCase().includes(search))
                );
            }

            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 24px;">No agents match this filter.</td></tr>';
                return;
            }

            tbody.innerHTML = '';
            filtered.slice(0, 15).forEach(a => {
                let badgeClass = 'badge-gray';
                let dot = '●';
                if (a.status === 'AVAILABLE') { badgeClass = 'badge-green'; }
                else if (a.status === 'CONNECTED' || a.status === 'DIALING') { badgeClass = 'badge-cyan'; }
                else if (a.status === 'WRAP_UP') { badgeClass = 'badge-amber'; }
                else if (a.status === 'PAUSED') { badgeClass = 'badge-purple'; }

                let actionBtn = '';
                if (a.status === 'AVAILABLE') {
                    actionBtn = `<button class="btn btn-outline" style="padding: 2px 8px; font-size: 0.71875rem;" onclick="setAgentStatus('${a.agent_id}', 'PAUSED')">Pause</button>`;
                } else if (a.status === 'PAUSED' || a.status === 'WRAP_UP' || a.status === 'OFFLINE') {
                    actionBtn = `<button class="btn btn-outline" style="padding: 2px 8px; font-size: 0.71875rem;" onclick="setAgentStatus('${a.agent_id}', 'AVAILABLE')">Make Ready</button>`;
                } else {
                    actionBtn = `<span style="font-size: 0.75rem; color: var(--text-dim);">In Call</span>`;
                }

                const row = `<tr>
                    <td style="font-family: 'JetBrains Mono'; font-weight: 600;">${a.agent_id}</td>
                    <td>${a.agent_name}</td>
                    <td><span class="badge badge-purple">${a.team || 'Collections'}</span></td>
                    <td><span class="badge ${badgeClass}">${dot} ${a.status}</span></td>
                    <td>${actionBtn}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        }

        async function fetchCalls() {
            try {
                const res = await fetch('/calls?limit=15');
                if (!res.ok) return;
                const calls = await res.json();
                const tbody = document.getElementById('call-table-body');
                if (!calls || calls.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 24px;">No calls recorded yet. Trigger a dial cycle!</td></tr>';
                    return;
                }
                tbody.innerHTML = '';
                calls.forEach(c => {
                    let badgeClass = 'badge-gray';
                    if (c.call_status === 'ANSWERED' || c.call_status === 'CONNECTED') badgeClass = 'badge-green';
                    else if (c.call_status === 'COMPLETED') badgeClass = 'badge-cyan';
                    else if (c.call_status === 'FAILED') badgeClass = 'badge-amber';
                    else if (c.call_status === 'RINGING' || c.call_status === 'INITIATED') badgeClass = 'badge-purple';

                    const duration = c.duration_sec ? `${c.duration_sec}s` : '--';
                    const time = c.created_at ? new Date(c.created_at).toLocaleTimeString() : '--';

                    const row = `<tr>
                        <td style="font-family: 'JetBrains Mono'; font-weight: 600;">${c.call_id}</td>
                        <td>${c.campaign_id}</td>
                        <td><span class="badge ${badgeClass}">${c.call_status}</span></td>
                        <td>${duration}</td>
                        <td style="color: var(--text-muted);">${time}</td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            } catch (err) {
                console.error("Fetch calls error:", err);
            }
        }

        function filterAgents(status, elem) {
            currentStatusFilter = status;
            document.querySelectorAll('#view-agents .filter-pill').forEach(el => el.classList.remove('active'));
            elem.classList.add('active');
            renderAgents();
        }

        function onSearchAgents() {
            renderAgents();
        }

        async function setAgentStatus(agentId, newStatus) {
            try {
                const res = await fetch(`/agents/${agentId}/status`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ status: newStatus })
                });
                if (res.ok) {
                    logMessage(`Agent ${agentId} transitioned to ${newStatus}`);
                    await refreshDashboard();
                } else {
                    const err = await res.json();
                    logMessage(`❌ Cannot change ${agentId}: ${err.detail || 'Illegal transition'}`);
                }
            } catch (err) {
                logMessage(`Error updating agent: ${err.message}`);
            }
        }

        async function triggerDialCycle() {
            const btn = document.getElementById('btn-run-cycle');
            const campaignId = document.getElementById('campaign-select').value;
            const mode = document.getElementById('mode-select').value;

            btn.disabled = true;
            btn.innerText = '⏳ Dispatching Telephony Cycle...';
            logMessage(`Executing atomic cycle: ${campaignId} [Mode: ${mode}]...`);

            try {
                const res = await fetch('/dialer/run-cycle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ campaign_id: campaignId, force_mode: mode })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || 'Dialer cycle failed');
                }

                const data = await res.json();
                const allocated = data.calls_allocated || (data.dispatched_call_ids ? data.dispatched_call_ids.length : 0);
                const decision = data.safety_decision ? data.safety_decision.decision : 'APPROVED';
                
                logMessage(`✅ Cycle Complete! Mode: ${data.mode} | Safety: ${decision} | Calls Dispatched: ${allocated} | Carrier Events: ${data.events_processed || 0}`);
                if (data.dispatched_call_ids && data.dispatched_call_ids.length > 0) {
                    logMessage(`  ↳ Call IDs: ${data.dispatched_call_ids.slice(0, 4).join(', ')}${allocated > 4 ? ' ...' : ''}`);
                }

                await refreshDashboard();
                if (currentActiveTab === 'calls') {
                    await fetchCalls();
                }
            } catch (err) {
                logMessage(`❌ Cycle Error: ${err.message}`);
            } finally {
                btn.disabled = false;
                btn.innerText = '🚀 Trigger Dial Cycle';
            }
        }

        async function enqueueFreshLeads() {
            const campaignId = document.getElementById('campaign-select').value;
            logMessage(`Replenishing +100 leads into queue for ${campaignId}...`);
            try {
                const res = await fetch(`/borrowers/replenish/${campaignId}?count=100`, {
                    method: 'POST'
                });
                if (res.ok) {
                    const data = await res.json();
                    logMessage(`📥 Enqueued ${data.leads_enqueued} leads for ${campaignId}! Queue replenished.`);
                    await refreshDashboard();
                } else {
                    logMessage(`❌ Failed to replenish leads.`);
                }
            } catch (err) {
                logMessage(`❌ Error enqueuing leads: ${err.message}`);
            }
        }

        async function resetWrapUpAgents() {
            logMessage(`Freeing wrap-up agents back into AVAILABLE pool...`);
            try {
                const res = await fetch('/agents/bulk-status', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ target_status: 'AVAILABLE', count: 100 })
                });
                const data = await res.json();
                logMessage(`🔄 Returned ${data.agents_updated} agents to AVAILABLE status.`);
                await refreshDashboard();
            } catch (err) {
                logMessage(`Error resetting agents: ${err.message}`);
            }
        }

        async function testQuorumDrop() {
            logMessage(`⚡ Simulating Failure Scenario 3: Agent availability drop (transitioning 40 agents to OFFLINE)...`);
            try {
                const res = await fetch('/agents/bulk-status', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ target_status: 'OFFLINE', count: 40 })
                });
                const data = await res.json();
                logMessage(`🛡️ Dropped ${data.agents_updated} agents to OFFLINE. Trigger dial cycle to observe Safety Controller dynamic clamp.`);
                await refreshDashboard();
            } catch (err) {
                logMessage(`Error: ${err.message}`);
            }
        }

        async function toggleProvider() {
            const current = document.getElementById('kpi-provider').innerText.toLowerCase();
            const nextType = current === 'reliable' ? 'chaotic' : 'reliable';

            try {
                const res = await fetch('/provider/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ provider_type: nextType })
                });
                if (res.ok) {
                    logMessage(`📶 Carrier Provider switched to: ${nextType.toUpperCase()}`);
                    await refreshDashboard();
                }
            } catch (err) {
                logMessage(`Failed to toggle carrier: ${err.message}`);
            }
        }

        function onCampaignChange() {
            const sel = document.getElementById('campaign-select');
            const info = document.getElementById('campaign-info');
            info.innerText = sel.value.includes('101') ? 'Strategy: FIELD' : 'Strategy: VOICE';
        }

        async function refreshDashboard(manual = false) {
            await fetchMetrics();
            await fetchAgents();
            if (manual) {
                logMessage('Dashboard synchronized with SQLite WAL.');
            }
        }

        // Initialize dashboard and start smooth 2.5s poll
        refreshDashboard();
        setInterval(fetchMetrics, 2500);
    </script>
</body>
</html>
"""
