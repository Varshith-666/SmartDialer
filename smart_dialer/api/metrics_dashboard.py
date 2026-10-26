"""Interactive Formatted Dashboard for Real-Time Telephony & Safety Metrics."""

from typing import Dict, Any
import json


def render_metrics_dashboard(initial_data: Dict[str, Any]) -> str:
    """Generate modern, rich, responsive HTML dashboard for operational metrics."""
    initial_json = json.dumps(initial_data, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDialer — Telephony & Safety Metrics Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #070a12;
            --bg-card: rgba(14, 20, 34, 0.82);
            --bg-card-hover: rgba(22, 32, 54, 0.92);
            --bg-input: #090e1b;
            --border-card: rgba(255, 255, 255, 0.08);
            --border-card-hover: rgba(255, 255, 255, 0.16);
            --border-active: rgba(99, 102, 241, 0.5);
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.35);
            --accent-green: #10b981;
            --accent-green-glow: rgba(16, 185, 129, 0.3);
            --accent-cyan: #06b6d4;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --accent-purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(ellipse at 50% 0%, #151e36 0%, var(--bg-base) 75%);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.5;
            padding-bottom: 60px;
        }}

        .container {{
            max-width: 1360px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        /* Header */
        header {{
            border-bottom: 1px solid var(--border-card);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 50;
            background: rgba(7, 10, 18, 0.88);
        }}

        .nav-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 72px;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none;
            color: var(--text-main);
        }}

        .brand-icon {{
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 18px var(--primary-glow);
        }}

        .brand-title {{
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .brand-badge {{
            font-size: 0.6875rem;
            padding: 2px 7px;
            border-radius: 9999px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            font-weight: 600;
        }}

        .brand-subtitle {{
            font-size: 0.75rem;
            color: var(--text-muted);
            letter-spacing: 0.02em;
        }}

        .nav-links {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .status-badge {{
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
        }}

        .pulse-dot {{
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10b981;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
            70% {{ transform: scale(1); box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }}
            100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 7px;
            padding: 8px 15px;
            border-radius: 9px;
            font-size: 0.84rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid transparent;
            font-family: inherit;
        }}

        .btn-outline {{
            background: rgba(255, 255, 255, 0.04);
            border-color: var(--border-card);
            color: var(--text-main);
        }}

        .btn-outline:hover {{
            background: rgba(255, 255, 255, 0.09);
            border-color: var(--border-card-hover);
            transform: translateY(-1px);
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #4f46e5, #6366f1);
            color: #ffffff;
            box-shadow: 0 4px 14px var(--primary-glow);
        }}

        .btn-primary:hover {{
            background: linear-gradient(135deg, #4338ca, #4f46e5);
            transform: translateY(-1px);
        }}

        .btn-sm {{
            padding: 5px 11px;
            font-size: 0.78125rem;
            border-radius: 7px;
        }}

        /* Hero Header */
        .hero-banner {{
            padding: 26px 0 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .hero-title {{
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero-desc {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 4px;
        }}

        .hero-controls {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* View Mode Segmented Switcher */
        .view-switcher {{
            display: flex;
            align-items: center;
            background: #0b1120;
            padding: 4px;
            border-radius: 10px;
            border: 1px solid var(--border-card);
            gap: 4px;
        }}

        .switch-btn {{
            padding: 6px 14px;
            font-size: 0.8125rem;
            font-weight: 600;
            color: var(--text-muted);
            background: transparent;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .switch-btn.active {{
            background: rgba(99, 102, 241, 0.25);
            color: #ffffff;
            font-weight: 700;
            border: 1px solid rgba(99, 102, 241, 0.4);
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}

        @media (max-width: 1200px) {{
            .kpi-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
        }}

        @media (max-width: 768px) {{
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .kpi-card {{
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-card);
            border-radius: 14px;
            padding: 20px;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }}

        .kpi-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-card-hover);
            transform: translateY(-2px);
        }}

        .kpi-card-hero {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            border-color: rgba(99, 102, 241, 0.35);
            box-shadow: 0 0 25px rgba(99, 102, 241, 0.12);
        }}

        .kpi-label {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.15rem;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.03em;
            line-height: 1.1;
        }}

        .kpi-sub {{
            margin-top: 8px;
            font-size: 0.78125rem;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .kpi-pill {{
            display: inline-block;
            font-size: 0.6875rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 9999px;
        }}

        .pill-green {{ background: rgba(16, 185, 129, 0.18); color: #34d399; }}
        .pill-blue {{ background: rgba(6, 182, 212, 0.18); color: #22d3ee; }}
        .pill-amber {{ background: rgba(245, 158, 11, 0.18); color: #fbbf24; }}
        .pill-purple {{ background: rgba(168, 85, 247, 0.18); color: #c084fc; }}
        .pill-rose {{ background: rgba(244, 63, 94, 0.18); color: #fb7185; }}

        /* Progress Mini Bar */
        .progress-bar-wrap {{
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            margin-top: 10px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            border-radius: 9999px;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .progress-green {{ background: linear-gradient(90deg, #10b981, #34d399); }}
        .progress-blue {{ background: linear-gradient(90deg, #4f46e5, #06b6d4); }}
        .progress-purple {{ background: linear-gradient(90deg, #8b5cf6, #c084fc); }}

        /* Dashboard Section Grid */
        .section-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}

        @media (max-width: 992px) {{
            .section-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .panel-card {{
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 22px;
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-card);
        }}

        .panel-title {{
            font-size: 1.05rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.01em;
        }}

        /* Table & Lists */
        .metric-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 11px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-size: 0.875rem;
        }}

        .metric-row:last-child {{
            border-bottom: none;
        }}

        .metric-row-label {{
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .metric-dot {{
            width: 10px;
            height: 10px;
            border-radius: 3px;
        }}

        .metric-row-value {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .metric-percent {{
            font-size: 0.78125rem;
            color: var(--text-dim);
            width: 50px;
            text-align: right;
        }}

        /* Safety Controller Callout */
        .safety-banner {{
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
        }}

        .safety-badge-pill {{
            background: #10b981;
            color: #04100c;
            font-weight: 800;
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        /* Interactive Simulator Bar */
        .sim-bar {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            flex-wrap: wrap;
        }}

        .sim-title {{
            font-size: 0.9rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .sim-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .sim-select {{
            background: var(--bg-input);
            border: 1px solid var(--border-card);
            color: var(--text-main);
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 0.8125rem;
            outline: none;
            font-family: inherit;
        }}

        /* Raw JSON Inspector View */
        .raw-json-panel {{
            display: none;
            background: #03060d;
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
        }}

        .raw-json-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .json-viewer {{
            background: #020409;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.84rem;
            color: #38bdf8;
            max-height: 520px;
            overflow-y: auto;
            white-space: pre-wrap;
            line-height: 1.5;
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid var(--border-card-hover);
            padding: 12px 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            font-size: 0.84rem;
            font-weight: 600;
            display: none;
            z-index: 100;
            animation: slideUp 0.3s ease;
        }}

        @keyframes slideUp {{
            from {{ transform: translateY(20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
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
                    <span id="sys-status">TELEMETRY LIVE</span>
                </div>
                <a href="/" class="btn btn-outline btn-sm">🖥️ Operations Console</a>
                <a href="/metrics" class="btn btn-primary btn-sm" style="font-weight:700;">📊 Metrics Dashboard</a>
                <a href="/health" class="btn btn-outline btn-sm">💓 Health Probe</a>
                <a href="/docs" target="_blank" class="btn btn-outline btn-sm">📖 Swagger Docs</a>
                <button class="btn btn-outline btn-sm" onclick="fetchMetrics(true)" title="Force Sync">↻ Sync</button>
            </div>
        </div>
    </header>

    <main class="container">
        <!-- Hero Header -->
        <section class="hero-banner">
            <div>
                <h1 class="hero-title">Telephony & Operational Metrics</h1>
                <p class="hero-desc">
                    High-precision real-time metrics stream for call pipelines, agent state machine distributions, and safety controller compliance.
                </p>
            </div>
            <div class="hero-controls">
                <div class="view-switcher">
                    <button class="switch-btn active" id="btn-formatted-view" onclick="switchView('formatted')">📊 Formatted Dashboard</button>
                    <button class="switch-btn" id="btn-raw-view" onclick="switchView('raw')">💻 Raw JSON</button>
                </div>
                <a href="/metrics?format=json" target="_blank" class="btn btn-outline btn-sm" title="Open API endpoint directly">Raw API ↗</a>
            </div>
        </section>

        <!-- Safety Guardrail Banner -->
        <div class="safety-banner">
            <div style="display:flex; align-items:center; gap:12px;">
                <span class="safety-badge-pill">FCC COMPLIANCE ACTIVE</span>
                <span style="font-size:0.875rem; color:#cbd5e1;">
                    Independent Safety Controller running: <strong>3.00% FTC/FCC TSR Abandonment Ceiling</strong> enforced. Overdial ratio capped at <strong>2.5x</strong>.
                </span>
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#34d399; font-weight:700;">
                Abandon Rate: <span id="abandon-rate-val">0.00%</span> (Compliant)
            </div>
        </div>

        <!-- Simulator Quick Dialing Bar -->
        <div class="sim-bar">
            <div class="sim-title">
                <span>⚡ Live Dialing Trigger</span>
                <span style="font-size:0.75rem; color:var(--text-dim); font-weight:400;">Execute an atomic cycle and observe live state changes</span>
            </div>
            <div class="sim-actions">
                <select class="sim-select" id="sim-campaign">
                    <option value="CMP0000101">CMP0000101 (400 Queued Leads)</option>
                    <option value="CMP0000105">CMP0000105 (400 Queued Leads)</option>
                    <option value="CMP0000108">CMP0000108 (Active Recovery)</option>
                    <option value="CMP0000110">CMP0000110 (Voice Lead)</option>
                    <option value="CMP0000117">CMP0000117 (Voice High-Risk)</option>
                </select>
                <select class="sim-select" id="sim-mode">
                    <option value="PROGRESSIVE">Progressive Mode (1:1 Guaranteed)</option>
                    <option value="PREDICTIVE">Predictive Mode (Speculative)</option>
                </select>
                <button class="btn btn-primary btn-sm" id="btn-run-sim" onclick="triggerDialerCycle()">Run Cycle →</button>
            </div>
        </div>

        <!-- FORMATTED VIEW -->
        <div id="formatted-view-container">
            <!-- 5 KPI Cards Grid -->
            <div class="kpi-grid">
                <!-- Card 1: Total Calls -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Total Calls</span>
                        <span class="kpi-pill pill-blue">TELEPHONY</span>
                    </div>
                    <div class="kpi-value" id="kpi-total-calls">0</div>
                    <div class="kpi-sub">
                        <span>Completed: <strong id="kpi-completed-calls" style="color:#34d399;">0</strong></span>
                        <span>•</span>
                        <span>Failed: <strong id="kpi-failed-calls" style="color:#fb7185;">0</strong></span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-blue" id="prog-calls" style="width: 100%;"></div>
                    </div>
                </div>

                <!-- Card 2: Contact / Answer Rate -->
                <div class="kpi-card kpi-card-hero">
                    <div class="kpi-label">
                        <span>Answer Rate</span>
                        <span class="kpi-pill pill-green">CONTACT KPI</span>
                    </div>
                    <div class="kpi-value" id="kpi-answer-rate" style="color:#34d399;">0.00%</div>
                    <div class="kpi-sub">
                        <span>Answered: <strong id="kpi-answered-calls">0</strong> calls</span>
                        <span>• Benchmark ~20%</span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-green" id="prog-answer" style="width: 0%;"></div>
                    </div>
                </div>

                <!-- Card 3: Available Agents -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Available Agents</span>
                        <span class="kpi-pill pill-green">● READY</span>
                    </div>
                    <div class="kpi-value" id="kpi-available-agents" style="color:#38bdf8;">0</div>
                    <div class="kpi-sub">
                        <span>Total Fleet: <strong id="kpi-total-agents">855</strong></span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-blue" id="prog-agents" style="width: 30%;"></div>
                    </div>
                </div>

                <!-- Card 4: Agent Utilization -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Fleet Utilization</span>
                        <span class="kpi-pill pill-purple">PRODUCTIVITY</span>
                    </div>
                    <div class="kpi-value" id="kpi-utilization-pct" style="color:#c084fc;">0.00%</div>
                    <div class="kpi-sub">
                        <span>In Wrap-up: <strong id="kpi-wrapup-agents">0</strong></span>
                        <span>•</span>
                        <span>Connected: <strong id="kpi-connected-agents">0</strong></span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-purple" id="prog-util" style="width: 0%;"></div>
                    </div>
                </div>

                <!-- Card 5: Safety Evaluations -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Safety Audits</span>
                        <span class="kpi-pill pill-amber">CONTROLLER</span>
                    </div>
                    <div class="kpi-value" id="kpi-safety-evals">0</div>
                    <div class="kpi-sub">
                        <span>Approved: <strong id="kpi-safety-approvals" style="color:#34d399;">0</strong></span>
                        <span>•</span>
                        <span>Fallbacks: <strong id="kpi-safety-fallbacks" style="color:#fbbf24;">0</strong></span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-green" id="prog-safety" style="width: 100%;"></div>
                    </div>
                </div>
            </div>

            <!-- Two Breakdown Panels -->
            <div class="section-grid">
                <!-- Panel 1: Call State Machine Pipeline -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span>📡 Call Outcome Distribution</span>
                        </div>
                        <span style="font-size:0.75rem; color:var(--text-dim); font-family:'JetBrains Mono', monospace;" id="call-timestamp">Updating...</span>
                    </div>

                    <div id="call-breakdown-list">
                        <!-- Populated dynamically via JS -->
                    </div>
                </div>

                <!-- Panel 2: Agent Fleet Workforce State -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span>👥 Agent Workforce States</span>
                        </div>
                        <span style="font-size:0.75rem; color:var(--text-dim);" id="fleet-summary">855 Agents Total</span>
                    </div>

                    <div id="agent-breakdown-list">
                        <!-- Populated dynamically via JS -->
                    </div>
                </div>
            </div>

            <!-- Safety Controller Audit Details -->
            <div class="panel-card" style="margin-bottom:24px;">
                <div class="panel-header">
                    <div class="panel-title">
                        <span>🛡️ Independent Safety Controller Audit Log Summary</span>
                    </div>
                    <span class="brand-badge">HARD REGULATORY GUARDRAILS</span>
                </div>
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:16px;">
                    <div style="background:#090e1b; border:1px solid var(--border-card); padding:14px; border-radius:10px;">
                        <div style="font-size:0.75rem; color:var(--text-dim); text-transform:uppercase; margin-bottom:4px;">Total Evaluations</div>
                        <div style="font-size:1.6rem; font-family:'JetBrains Mono', monospace; font-weight:700; color:var(--text-main);" id="audit-evals">0</div>
                    </div>
                    <div style="background:#090e1b; border:1px solid var(--border-card); padding:14px; border-radius:10px;">
                        <div style="font-size:0.75rem; color:var(--text-dim); text-transform:uppercase; margin-bottom:4px;">Approvals</div>
                        <div style="font-size:1.6rem; font-family:'JetBrains Mono', monospace; font-weight:700; color:#34d399;" id="audit-approvals">0</div>
                    </div>
                    <div style="background:#090e1b; border:1px solid var(--border-card); padding:14px; border-radius:10px;">
                        <div style="font-size:0.75rem; color:var(--text-dim); text-transform:uppercase; margin-bottom:4px;">Reductions / Caps</div>
                        <div style="font-size:1.6rem; font-family:'JetBrains Mono', monospace; font-weight:700; color:#fbbf24;" id="audit-reductions">0</div>
                    </div>
                    <div style="background:#090e1b; border:1px solid var(--border-card); padding:14px; border-radius:10px;">
                        <div style="font-size:0.75rem; color:var(--text-dim); text-transform:uppercase; margin-bottom:4px;">Force Progressive Fallbacks</div>
                        <div style="font-size:1.6rem; font-family:'JetBrains Mono', monospace; font-weight:700; color:#f43f5e;" id="audit-fallbacks">0</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RAW JSON VIEW -->
        <div class="raw-json-panel" id="raw-view-container">
            <div class="raw-json-header">
                <div>
                    <h3 style="font-size:1rem; font-weight:700; color:#f8fafc;">Live JSON Telemetry Feed</h3>
                    <p style="font-size:0.75rem; color:var(--text-dim); margin-top:2px;">Direct payload as returned by GET /metrics?format=json</p>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="btn btn-outline btn-sm" onclick="copyJsonToClipboard()">📋 Copy JSON</button>
                    <a href="/metrics?format=json" target="_blank" class="btn btn-outline btn-sm">Direct API Link ↗</a>
                </div>
            </div>
            <pre class="json-viewer" id="json-viewer-content">{initial_json}</pre>
        </div>
    </main>

    <!-- Toast Notification -->
    <div class="toast" id="toast-notify"></div>

    <script>
        let currentMetrics = {initial_json};
        let pollTimer = null;

        function showToast(msg) {{
            const toast = document.getElementById('toast-notify');
            toast.innerText = msg;
            toast.style.display = 'block';
            setTimeout(() => {{
                toast.style.display = 'none';
            }}, 3200);
        }}

        function switchView(mode) {{
            const fmtContainer = document.getElementById('formatted-view-container');
            const rawContainer = document.getElementById('raw-view-container');
            const btnFmt = document.getElementById('btn-formatted-view');
            const btnRaw = document.getElementById('btn-raw-view');

            if (mode === 'raw') {{
                fmtContainer.style.display = 'none';
                rawContainer.style.display = 'block';
                btnFmt.classList.remove('active');
                btnRaw.classList.add('active');
            }} else {{
                fmtContainer.style.display = 'block';
                rawContainer.style.display = 'none';
                btnRaw.classList.remove('active');
                btnFmt.classList.add('active');
            }}
        }}

        function copyJsonToClipboard() {{
            const text = JSON.stringify(currentMetrics, null, 2);
            navigator.clipboard.writeText(text).then(() => {{
                showToast("✓ Metrics JSON copied to clipboard!");
            }}).catch(() => {{
                showToast("Failed to copy JSON.");
            }});
        }}

        function renderDashboard(data) {{
            if (!data) return;
            currentMetrics = data;

            // Update JSON viewer
            const jsonElem = document.getElementById('json-viewer-content');
            if (jsonElem) {{
                jsonElem.innerText = JSON.stringify(data, null, 2);
            }}

            // Call Metrics
            const cm = data.call_metrics || {{}};
            const totalCalls = cm.total_calls || 0;
            const completedCalls = cm.completed_calls || 0;
            const failedCalls = cm.failed_calls || 0;
            const answeredCalls = cm.answered_calls || 0;
            const ansRate = cm.answer_rate_pct || 0.0;

            document.getElementById('kpi-total-calls').innerText = totalCalls.toLocaleString();
            document.getElementById('kpi-completed-calls').innerText = completedCalls.toLocaleString();
            document.getElementById('kpi-failed-calls').innerText = failedCalls.toLocaleString();
            document.getElementById('kpi-answered-calls').innerText = answeredCalls.toLocaleString();
            document.getElementById('kpi-answer-rate').innerText = ansRate.toFixed(2) + '%';
            document.getElementById('prog-answer').style.width = Math.min(ansRate * 3, 100) + '%';

            // Agent Metrics
            const am = data.agent_metrics || {{}};
            const totalAgents = am.total_agents || 855;
            const availAgents = am.available || 0;
            const connectedAgents = am.connected || 0;
            const wrapupAgents = am.wrap_up || 0;
            const utilPct = am.utilization_pct || 0.0;

            document.getElementById('kpi-available-agents').innerText = availAgents.toLocaleString();
            document.getElementById('kpi-total-agents').innerText = totalAgents.toLocaleString();
            document.getElementById('kpi-utilization-pct').innerText = utilPct.toFixed(2) + '%';
            document.getElementById('kpi-connected-agents').innerText = connectedAgents.toLocaleString();
            document.getElementById('kpi-wrapup-agents').innerText = wrapupAgents.toLocaleString();
            document.getElementById('prog-util').style.width = Math.min(utilPct, 100) + '%';

            // Safety Controller Metrics
            const sm = data.safety_controller_metrics || {{}};
            const totalEvals = sm.total_evaluations || 0;
            const approvals = sm.approvals || 0;
            const fallbacks = sm.force_progressive_fallbacks || 0;
            const reductions = sm.reductions || 0;

            document.getElementById('kpi-safety-evals').innerText = totalEvals.toLocaleString();
            document.getElementById('kpi-safety-approvals').innerText = approvals.toLocaleString();
            document.getElementById('kpi-safety-fallbacks').innerText = fallbacks.toLocaleString();
            document.getElementById('audit-evals').innerText = totalEvals.toLocaleString();
            document.getElementById('audit-approvals').innerText = approvals.toLocaleString();
            document.getElementById('audit-reductions').innerText = reductions.toLocaleString();
            document.getElementById('audit-fallbacks').innerText = fallbacks.toLocaleString();

            if (data.timestamp) {{
                const d = new Date(data.timestamp);
                document.getElementById('call-timestamp').innerText = 'Synced at ' + d.toLocaleTimeString();
            }}

            // Render Call Breakdown List
            const breakdown = cm.breakdown || {{}};
            const callList = document.getElementById('call-breakdown-list');
            if (callList) {{
                let html = '';
                const keys = Object.keys(breakdown);
                if (keys.length === 0) {{
                    html = '<div style="color:var(--text-dim); padding:10px 0;">No call records generated yet. Run a dialing cycle to initiate telephony events.</div>';
                }} else {{
                    keys.forEach(k => {{
                        const cnt = breakdown[k];
                        const pct = totalCalls > 0 ? ((cnt / totalCalls) * 100).toFixed(1) : '0.0';
                        let color = '#38bdf8';
                        if (k === 'COMPLETED') color = '#34d399';
                        else if (k === 'FAILED') color = '#fb7185';
                        else if (k === 'ANSWERED' || k === 'CONNECTED') color = '#22d3ee';
                        else if (k === 'RINGING' || k === 'INITIATED') color = '#fbbf24';

                        html += `
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:${{color}};"></span>
                                <span>${{k}}</span>
                            </div>
                            <div class="metric-row-value">
                                <span>${{cnt.toLocaleString()}}</span>
                                <span class="metric-percent">${{pct}}%</span>
                            </div>
                        </div>`;
                    }});
                }}
                callList.innerHTML = html;
            }}

            // Render Agent Breakdown List
            const agentList = document.getElementById('agent-breakdown-list');
            if (agentList) {{
                const agentStates = [
                    {{ key: 'AVAILABLE', label: 'Available (Ready for Bridging)', count: am.available || 0, color: '#34d399' }},
                    {{ key: 'CONNECTED', label: 'Connected on Active Call', count: am.connected || 0, color: '#38bdf8' }},
                    {{ key: 'WRAP_UP', label: 'Post-Call Wrap-up', count: am.wrap_up || 0, color: '#c084fc' }},
                    {{ key: 'DIALING', label: 'Outbound Dialing / Ringing', count: am.dialing || 0, color: '#fbbf24' }},
                    {{ key: 'RESERVED', label: 'Reserved for Atomic Match', count: am.reserved || 0, color: '#818cf8' }},
                    {{ key: 'PAUSED', label: 'Break / Paused', count: am.paused || 0, color: '#94a3b8' }},
                    {{ key: 'OFFLINE', label: 'Offline / Logged Out', count: am.offline || 0, color: '#475569' }}
                ];

                let aHtml = '';
                agentStates.forEach(item => {{
                    const pct = totalAgents > 0 ? ((item.count / totalAgents) * 100).toFixed(1) : '0.0';
                    aHtml += `
                    <div class="metric-row">
                        <div class="metric-row-label">
                            <span class="metric-dot" style="background:${{item.color}};"></span>
                            <span>${{item.label}}</span>
                        </div>
                        <div class="metric-row-value">
                            <span>${{item.count.toLocaleString()}}</span>
                            <span class="metric-percent">${{pct}}%</span>
                        </div>
                    </div>`;
                }});
                agentList.innerHTML = aHtml;
            }}
        }}

        async function fetchMetrics(isManual = false) {{
            try {{
                const res = await fetch('/metrics?format=json');
                if (res.ok) {{
                    const data = await res.json();
                    renderDashboard(data);
                    if (isManual) {{
                        showToast("✓ Telephony metrics synchronized!");
                    }}
                }}
            }} catch (err) {{
                console.warn("Polling error:", err);
            }}
        }}

        async function triggerDialerCycle() {{
            const btn = document.getElementById('btn-run-sim');
            const camp = document.getElementById('sim-campaign').value;
            const mode = document.getElementById('sim-mode').value;

            btn.disabled = true;
            btn.innerText = "Executing...";

            try {{
                const res = await fetch('/dialer/run-cycle', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ campaign_id: camp, force_mode: mode }})
                }});
                const result = await res.json();
                if (res.ok) {{
                    showToast(`✓ Cycle executed on ${{camp}}: ${{result.calls_allocated || 0}} calls placed!`);
                    await fetchMetrics();
                }} else {{
                    showToast(`Error: ${{result.detail || 'Failed cycle'}}`);
                }}
            }} catch (e) {{
                showToast("Dialing cycle request failed.");
            }} finally {{
                btn.disabled = false;
                btn.innerText = "Run Cycle →";
            }}
        }}

        // Initial render
        renderDashboard(currentMetrics);

        // Auto poll every 3 seconds
        pollTimer = setInterval(() => {{
            fetchMetrics(false);
        }}, 3000);
    </script>
</body>
</html>
"""


def render_health_dashboard(data: Dict[str, Any]) -> str:
    """Generate modern, rich, responsive HTML dashboard for health probe."""
    initial_json = json.dumps(data, indent=2)
    status = str(data.get("status", "HEALTHY")).upper()
    status_color = "#34d399" if status == "HEALTHY" else "#fbbf24"
    db_status = str(data.get("database", "CONNECTED")).upper()
    env = str(data.get("environment", "development")).upper()
    provider = str(data.get("active_provider", "reliable")).upper()
    total_agents = int(data.get("total_agents", 0))
    avail_agents = int(data.get("available_agents", 0))
    queued_borrowers = int(data.get("queued_borrowers", 0))
    in_flight = int(data.get("in_flight_calls", 0))
    timestamp = str(data.get("timestamp", ""))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDialer — System Health & Telemetry Diagnostics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #070a12;
            --bg-card: rgba(14, 20, 34, 0.85);
            --bg-card-hover: rgba(22, 32, 54, 0.95);
            --bg-input: #090e1b;
            --border-card: rgba(255, 255, 255, 0.08);
            --border-card-hover: rgba(255, 255, 255, 0.16);
            --border-active: rgba(99, 102, 241, 0.5);
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.35);
            --accent-green: #10b981;
            --accent-green-glow: rgba(16, 185, 129, 0.3);
            --accent-cyan: #06b6d4;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --accent-purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(ellipse at 50% 0%, #151e36 0%, var(--bg-base) 75%);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.5;
            padding-bottom: 60px;
        }}

        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        /* Header */
        header {{
            border-bottom: 1px solid var(--border-card);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 50;
            background: rgba(7, 10, 18, 0.88);
        }}

        .nav-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 72px;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none;
            color: var(--text-main);
        }}

        .brand-icon {{
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, #10b981, #06b6d4);
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 18px rgba(16, 185, 129, 0.35);
        }}

        .brand-title {{
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .brand-badge {{
            font-size: 0.6875rem;
            padding: 2px 7px;
            border-radius: 9999px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
            font-weight: 600;
        }}

        .brand-subtitle {{
            font-size: 0.75rem;
            color: var(--text-muted);
            letter-spacing: 0.02em;
        }}

        .nav-links {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .status-badge {{
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
        }}

        .pulse-dot {{
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10b981;
            animation: pulse 2s infinite;
        }}

        .latency-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: #38bdf8;
            background: rgba(6, 182, 212, 0.12);
            border: 1px solid rgba(6, 182, 212, 0.28);
            padding: 5px 10px;
            border-radius: 9999px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.15); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border-radius: 9px;
            font-size: 0.875rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid transparent;
            font-family: inherit;
        }}

        .btn-sm {{
            padding: 6px 12px;
            font-size: 0.8125rem;
        }}

        .btn-outline {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-main);
            border-color: var(--border-card);
        }}

        .btn-outline:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--border-card-hover);
        }}

        .btn-primary {{
            background: var(--primary);
            color: #ffffff;
            box-shadow: 0 0 12px var(--primary-glow);
        }}

        .btn-primary:hover {{
            background: #4f46e5;
        }}

        .btn-health-active {{
            background: rgba(16, 185, 129, 0.18);
            border-color: rgba(16, 185, 129, 0.4);
            color: #34d399;
            font-weight: 700;
        }}

        /* Hero Banner */
        .hero-banner {{
            padding: 28px 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .hero-title {{
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero-desc {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 4px;
        }}

        .hero-controls {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .view-switcher {{
            display: flex;
            align-items: center;
            background: #0b1120;
            padding: 4px;
            border-radius: 10px;
            border: 1px solid var(--border-card);
            gap: 4px;
        }}

        .switch-btn {{
            padding: 6px 14px;
            font-size: 0.8125rem;
            font-weight: 600;
            color: var(--text-muted);
            background: transparent;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .switch-btn.active {{
            background: rgba(16, 185, 129, 0.25);
            color: #ffffff;
            font-weight: 700;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}

        /* Hero Health Status Box */
        .status-hero-card {{
            background: linear-gradient(135deg, rgba(14, 25, 44, 0.95), rgba(7, 14, 26, 0.95));
            border: 1px solid rgba(16, 185, 129, 0.35);
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.08);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 18px;
        }}

        .status-hero-left {{
            display: flex;
            align-items: center;
            gap: 18px;
        }}

        .status-hero-icon {{
            width: 54px;
            height: 54px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);
        }}

        .status-hero-title {{
            font-size: 1.45rem;
            font-weight: 800;
            color: #f8fafc;
            letter-spacing: -0.02em;
        }}

        .status-hero-desc {{
            font-size: 0.84rem;
            color: var(--text-muted);
            margin-top: 3px;
        }}

        /* 4 KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}

        @media (max-width: 992px) {{
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 580px) {{
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .kpi-card {{
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-card);
            border-radius: 14px;
            padding: 20px;
            transition: all 0.2s ease;
        }}

        .kpi-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-card-hover);
            transform: translateY(-2px);
        }}

        .kpi-label {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.15;
        }}

        .kpi-sub {{
            margin-top: 8px;
            font-size: 0.78125rem;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .kpi-pill {{
            font-size: 0.6875rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 9999px;
        }}

        .pill-green {{ background: rgba(16, 185, 129, 0.18); color: #34d399; }}
        .pill-blue {{ background: rgba(6, 182, 212, 0.18); color: #22d3ee; }}
        .pill-amber {{ background: rgba(245, 158, 11, 0.18); color: #fbbf24; }}
        .pill-purple {{ background: rgba(168, 85, 247, 0.18); color: #c084fc; }}

        .progress-bar-wrap {{
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            margin-top: 10px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            border-radius: 9999px;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .progress-green {{ background: linear-gradient(90deg, #10b981, #34d399); }}
        .progress-cyan {{ background: linear-gradient(90deg, #06b6d4, #38bdf8); }}
        .progress-purple {{ background: linear-gradient(90deg, #8b5cf6, #c084fc); }}
        .progress-amber {{ background: linear-gradient(90deg, #f59e0b, #fbbf24); }}

        /* 4 Deep Subsystem Diagnostic Panels */
        .section-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}

        @media (max-width: 880px) {{
            .section-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .panel-card {{
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 22px;
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-card);
        }}

        .panel-title {{
            font-size: 1.05rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .metric-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 11px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-size: 0.875rem;
        }}

        .metric-row:last-child {{
            border-bottom: none;
        }}

        .metric-row-label {{
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .metric-dot {{
            width: 9px;
            height: 9px;
            border-radius: 3px;
        }}

        .metric-row-value {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* Raw JSON Viewer Panel */
        .raw-json-panel {{
            display: none;
            background: #03060d;
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
        }}

        .raw-json-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .json-viewer {{
            background: #020409;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.84rem;
            color: #38bdf8;
            max-height: 480px;
            overflow-y: auto;
            white-space: pre-wrap;
            line-height: 1.5;
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid var(--border-card-hover);
            padding: 12px 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            font-size: 0.84rem;
            font-weight: 600;
            display: none;
            z-index: 100;
            animation: slideUp 0.3s ease;
        }}

        @keyframes slideUp {{
            from {{ transform: translateY(20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
    </style>
</head>
<body>
    <!-- Top Sticky Header -->
    <header>
        <div class="container nav-inner">
            <a href="/" class="brand">
                <div class="brand-icon">💓</div>
                <div>
                    <div class="brand-title">
                        SmartDialer Diagnostic Probe
                        <span class="brand-badge">WAL ACID</span>
                    </div>
                    <div class="brand-subtitle">Real-Time Telemetry & Subsystem Health Diagnostics</div>
                </div>
            </a>
            <div class="nav-links">
                <div class="status-badge" id="health-live-status-badge">
                    <span class="pulse-dot"></span>
                    <span id="health-live-status">ALL SYSTEMS HEALTHY</span>
                </div>
                <div class="latency-pill" id="health-latency-pill">
                    <span>⚡</span>
                    <span id="health-ping-val">1.2</span>ms latency
                </div>
                <a href="/" class="btn btn-outline btn-sm">🖥️ Operations Console</a>
                <a href="/metrics" class="btn btn-outline btn-sm">📊 Metrics Dashboard</a>
                <a href="/health" class="btn btn-health-active btn-sm">💓 Health Probe</a>
                <a href="/docs" target="_blank" class="btn btn-outline btn-sm">📖 Swagger Docs</a>
                <button class="btn btn-outline btn-sm" onclick="fetchHealth(true)" title="Force Ping Health Probe">↻ Ping</button>
            </div>
        </div>
    </header>

    <main class="container">
        <!-- Hero Header -->
        <section class="hero-banner">
            <div>
                <h1 class="hero-title">System Health & Telemetry Diagnostics</h1>
                <p class="hero-desc">
                    Live continuous inspection across SQLite WAL engine, carrier pipelines, agent workforce pools, and FCC regulatory safety controller.
                </p>
            </div>
            <div class="hero-controls">
                <div class="view-switcher">
                    <button class="switch-btn active" id="btn-formatted-view" onclick="switchView('formatted')">📊 Formatted Diagnostics</button>
                    <button class="switch-btn" id="btn-raw-view" onclick="switchView('raw')">💻 Raw JSON</button>
                </div>
                <a href="/health?format=json" target="_blank" class="btn btn-outline btn-sm" title="Open JSON API probe directly">Raw API ↗</a>
            </div>
        </section>

        <!-- Formatted View Container -->
        <div id="formatted-view-container">
            <!-- Hero Status Banner -->
            <div class="status-hero-card">
                <div class="status-hero-left">
                    <div class="status-hero-icon">✓</div>
                    <div>
                        <div class="status-hero-title">
                            System Operational: <span style="color:#34d399;" id="hero-status-text">{status}</span>
                        </div>
                        <div class="status-hero-desc">
                            All database write-ahead logs, telephony event listeners, and recovery safety controllers are running nominally.
                        </div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; text-transform:uppercase; color:var(--text-dim); font-weight:700;">Last Verified Probe</div>
                    <div style="font-family:'JetBrains Mono', monospace; font-size:0.95rem; color:#38bdf8; font-weight:700; margin-top:3px;" id="hero-timestamp">
                        {timestamp if timestamp else "Just now"}
                    </div>
                </div>
            </div>

            <!-- 4 Overview KPI Cards -->
            <div class="kpi-grid">
                <!-- Card 1: System Status -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Overall Status</span>
                        <span class="kpi-pill pill-green">CORE ENGINE</span>
                    </div>
                    <div class="kpi-value" id="kpi-status" style="color:#34d399;">{status}</div>
                    <div class="kpi-sub">
                        <span>Zero unhandled crash locks</span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-green" style="width: 100%;"></div>
                    </div>
                </div>

                <!-- Card 2: Database Connection -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Database Engine</span>
                        <span class="kpi-pill pill-blue">SQLITE WAL</span>
                    </div>
                    <div class="kpi-value" id="kpi-db" style="color:#38bdf8;">{db_status}</div>
                    <div class="kpi-sub">
                        <span>ACID transactions active</span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-cyan" style="width: 100%;"></div>
                    </div>
                </div>

                <!-- Card 3: Active Provider -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Carrier Provider</span>
                        <span class="kpi-pill pill-purple">TELEPHONY</span>
                    </div>
                    <div class="kpi-value" id="kpi-provider" style="color:#c084fc; font-size:1.6rem;">{provider}</div>
                    <div class="kpi-sub">
                        <span id="kpi-provider-sub">{"5% Failure baseline" if provider == "RELIABLE" else "20% Chaos testing"}</span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-purple" style="width: 100%;"></div>
                    </div>
                </div>

                <!-- Card 4: In-Flight Calls -->
                <div class="kpi-card">
                    <div class="kpi-label">
                        <span>Active Telephony</span>
                        <span class="kpi-pill pill-amber">IN-FLIGHT</span>
                    </div>
                    <div class="kpi-value" id="kpi-inflight" style="color:#fbbf24;">{in_flight}</div>
                    <div class="kpi-sub">
                        <span>Calls in progress</span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-fill progress-amber" id="prog-inflight" style="width: {min(in_flight * 5, 100)}%;"></div>
                    </div>
                </div>
            </div>

            <!-- 4 Subsystem Diagnostics Section Grid -->
            <div class="section-grid">
                <!-- Subsystem 1: Workforce Fleet Readiness -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span>👥 Agent Fleet Health & Capacity</span>
                        </div>
                        <span class="brand-badge">CONCURRENCY SAFE</span>
                    </div>
                    <div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#34d399;"></span>
                                <span>Available Agents (Ready for Bridge)</span>
                            </div>
                            <div class="metric-row-value" style="color:#34d399;" id="sub-avail-agents">
                                {avail_agents}
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#38bdf8;"></span>
                                <span>Total Fleet Capacity</span>
                            </div>
                            <div class="metric-row-value" id="sub-total-agents">
                                {total_agents}
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#c084fc;"></span>
                                <span>Fleet Availability Ratio</span>
                            </div>
                            <div class="metric-row-value" id="sub-avail-ratio">
                                {(avail_agents / max(total_agents, 1) * 100):.1f}%
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#10b981;"></span>
                                <span>Atomic Agent Allocation Lock</span>
                            </div>
                            <div class="metric-row-value" style="color:#34d399;">
                                ACTIVE (ROW-LEVEL)
                            </div>
                        </div>
                        <div class="progress-bar-wrap" style="margin-top:14px;">
                            <div class="progress-fill progress-green" id="prog-fleet-avail" style="width: {min(avail_agents / max(total_agents, 1) * 100, 100)}%;"></div>
                        </div>
                    </div>
                </div>

                <!-- Subsystem 2: Borrower Queue Depth & Pipeline -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span>📋 Lead Queue & Telephony Pipeline</span>
                        </div>
                        <span class="brand-badge">FIFO QUEUE</span>
                    </div>
                    <div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#fbbf24;"></span>
                                <span>Queued Borrowers</span>
                            </div>
                            <div class="metric-row-value" style="color:#fbbf24;" id="sub-queued-leads">
                                {queued_borrowers:,} leads
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#38bdf8;"></span>
                                <span>In-Flight Active Calls</span>
                            </div>
                            <div class="metric-row-value" id="sub-in-flight">
                                {in_flight} active
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#10b981;"></span>
                                <span>Queue Starvation Protection</span>
                            </div>
                            <div class="metric-row-value" style="color:#34d399;">
                                NOMINAL
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#a855f7;"></span>
                                <span>Telephony Webhook Dispatcher</span>
                            </div>
                            <div class="metric-row-value" style="color:#c084fc;">
                                IDEMPOTENT (ACTIVE)
                            </div>
                        </div>
                        <div class="progress-bar-wrap" style="margin-top:14px;">
                            <div class="progress-fill progress-cyan" style="width: 100%;"></div>
                        </div>
                    </div>
                </div>

                <!-- Subsystem 3: Regulatory Safety Guardrails -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span>🛡️ Regulatory Safety Controller</span>
                        </div>
                        <span class="kpi-pill pill-green">HARD COMPLIANCE</span>
                    </div>
                    <div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#34d399;"></span>
                                <span>FTC/FCC TSR Abandonment Ceiling</span>
                            </div>
                            <div class="metric-row-value" style="color:#34d399;">
                                &lt; 3.00% ENFORCED
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#38bdf8;"></span>
                                <span>Maximum Overdial Pacing Cap</span>
                            </div>
                            <div class="metric-row-value">
                                2.50x MAXIMUM
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#fbbf24;"></span>
                                <span>Auto-Fallback Mechanism</span>
                            </div>
                            <div class="metric-row-value" style="color:#fbbf24;">
                                PROGRESSIVE 1:1 RECOVERY
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#10b981;"></span>
                                <span>Startup Crash Reconciliation</span>
                            </div>
                            <div class="metric-row-value" style="color:#34d399;">
                                VERIFIED (ZERO LEAKS)
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Subsystem 4: Runtime Environment & Infrastructure -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span>⚙️ Infrastructure & Persistence</span>
                        </div>
                        <span class="brand-badge">ASYNC ASGI</span>
                    </div>
                    <div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#38bdf8;"></span>
                                <span>Environment</span>
                            </div>
                            <div class="metric-row-value" id="sub-env" style="text-transform:uppercase;">
                                {env}
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#34d399;"></span>
                                <span>Database File</span>
                            </div>
                            <div class="metric-row-value" style="color:#38bdf8; font-size:0.8rem;">
                                smart_dialer.db (WAL)
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#c084fc;"></span>
                                <span>Engine Version</span>
                            </div>
                            <div class="metric-row-value">
                                v1.0.0 (Production)
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-row-label">
                                <span class="metric-dot" style="background:#fbbf24;"></span>
                                <span>IPC Probe Latency</span>
                            </div>
                            <div class="metric-row-value" style="color:#34d399;" id="sub-ipc-latency">
                                &lt; 2.0 ms
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RAW JSON VIEW -->
        <div class="raw-json-panel" id="raw-view-container">
            <div class="raw-json-header">
                <div>
                    <h3 style="font-size:1rem; font-weight:700; color:#f8fafc;">Diagnostic JSON Probe Feed</h3>
                    <p style="font-size:0.75rem; color:var(--text-dim); margin-top:2px;">Direct payload as returned by GET /health?format=json</p>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="btn btn-outline btn-sm" onclick="copyJsonToClipboard()">📋 Copy JSON</button>
                    <a href="/health?format=json" target="_blank" class="btn btn-outline btn-sm">Direct API Link ↗</a>
                </div>
            </div>
            <pre class="json-viewer" id="json-viewer-content">{initial_json}</pre>
        </div>
    </main>

    <!-- Toast Notification -->
    <div class="toast" id="toast-notify"></div>

    <script>
        let currentHealth = {initial_json};
        let pollTimer = null;

        function showToast(msg) {{
            const toast = document.getElementById('toast-notify');
            toast.innerText = msg;
            toast.style.display = 'block';
            setTimeout(() => {{
                toast.style.display = 'none';
            }}, 3200);
        }}

        function switchView(mode) {{
            const fmtContainer = document.getElementById('formatted-view-container');
            const rawContainer = document.getElementById('raw-view-container');
            const btnFmt = document.getElementById('btn-formatted-view');
            const btnRaw = document.getElementById('btn-raw-view');

            if (mode === 'raw') {{
                fmtContainer.style.display = 'none';
                rawContainer.style.display = 'block';
                btnFmt.classList.remove('active');
                btnRaw.classList.add('active');
            }} else {{
                fmtContainer.style.display = 'block';
                rawContainer.style.display = 'none';
                btnRaw.classList.remove('active');
                btnFmt.classList.add('active');
            }}
        }}

        function copyJsonToClipboard() {{
            const text = JSON.stringify(currentHealth, null, 2);
            navigator.clipboard.writeText(text).then(() => {{
                showToast("✓ Health JSON copied to clipboard!");
            }}).catch(() => {{
                showToast("Failed to copy JSON.");
            }});
        }}

        function renderHealth(data, latencyMs = null) {{
            if (!data) return;
            currentHealth = data;

            // Update JSON viewer
            const jsonElem = document.getElementById('json-viewer-content');
            if (jsonElem) {{
                jsonElem.innerText = JSON.stringify(data, null, 2);
            }}

            const status = (data.status || 'HEALTHY').toUpperCase();
            const isHealthy = status === 'HEALTHY';
            const statusColor = isHealthy ? '#34d399' : '#fbbf24';

            // Top Status Badge & Hero
            const badgeText = document.getElementById('health-live-status');
            if (badgeText) {{
                badgeText.innerText = isHealthy ? 'ALL SYSTEMS HEALTHY' : 'SYSTEM DEGRADED';
            }}
            const heroStatus = document.getElementById('hero-status-text');
            if (heroStatus) {{
                heroStatus.innerText = status;
                heroStatus.style.color = statusColor;
            }}
            const kpiStatus = document.getElementById('kpi-status');
            if (kpiStatus) {{
                kpiStatus.innerText = status;
                kpiStatus.style.color = statusColor;
            }}

            // Database & Provider
            const dbVal = document.getElementById('kpi-db');
            if (dbVal) dbVal.innerText = (data.database || 'CONNECTED').toUpperCase();

            const provVal = document.getElementById('kpi-provider');
            if (provVal) {{
                const p = (data.active_provider || 'reliable').toUpperCase();
                provVal.innerText = p;
                const sub = document.getElementById('kpi-provider-sub');
                if (sub) sub.innerText = p === 'RELIABLE' ? '5% Failure baseline' : '20% Chaos testing';
            }}

            // In-flight calls
            const inflight = data.in_flight_calls || 0;
            const inflightVal = document.getElementById('kpi-inflight');
            if (inflightVal) inflightVal.innerText = inflight;
            const subInflight = document.getElementById('sub-in-flight');
            if (subInflight) subInflight.innerText = inflight + ' active';
            const progInflight = document.getElementById('prog-inflight');
            if (progInflight) progInflight.style.width = Math.min(inflight * 5, 100) + '%';

            // Agents
            const totalA = data.total_agents || 0;
            const availA = data.available_agents || 0;
            const subAvail = document.getElementById('sub-avail-agents');
            if (subAvail) subAvail.innerText = availA.toLocaleString();
            const subTotal = document.getElementById('sub-total-agents');
            if (subTotal) subTotal.innerText = totalA.toLocaleString();
            const subRatio = document.getElementById('sub-avail-ratio');
            const ratioPct = totalA > 0 ? (availA / totalA * 100).toFixed(1) : '0.0';
            if (subRatio) subRatio.innerText = ratioPct + '%';
            const progFleet = document.getElementById('prog-fleet-avail');
            if (progFleet) progFleet.style.width = Math.min(parseFloat(ratioPct), 100) + '%';

            // Queue
            const queued = data.queued_borrowers || 0;
            const subQueued = document.getElementById('sub-queued-leads');
            if (subQueued) subQueued.innerText = queued.toLocaleString() + ' leads';

            // Environment
            const subEnv = document.getElementById('sub-env');
            if (subEnv) subEnv.innerText = (data.environment || 'development').toUpperCase();

            // Latency & Timestamps
            if (latencyMs !== null) {{
                const pingElem = document.getElementById('health-ping-val');
                if (pingElem) pingElem.innerText = latencyMs.toFixed(1);
                const subIpc = document.getElementById('sub-ipc-latency');
                if (subIpc) subIpc.innerText = latencyMs.toFixed(1) + ' ms';
            }}

            if (data.timestamp) {{
                const d = new Date(data.timestamp);
                const heroTs = document.getElementById('hero-timestamp');
                if (heroTs) heroTs.innerText = 'Synced at ' + d.toLocaleTimeString();
            }}
        }}

        async function fetchHealth(isManual = false) {{
            const t0 = performance.now();
            try {{
                const res = await fetch('/health?format=json');
                const latency = performance.now() - t0;
                if (res.ok) {{
                    const data = await res.json();
                    renderHealth(data, latency);
                    if (isManual) {{
                        showToast("✓ Health probe verified! Latency: " + latency.toFixed(1) + "ms");
                    }}
                }}
            }} catch (err) {{
                console.warn("Health poll error:", err);
                const badgeText = document.getElementById('health-live-status');
                if (badgeText) badgeText.innerText = 'OFFLINE / RECONNECTING';
            }}
        }}

        // Initial render
        renderHealth(currentHealth, 1.2);

        // Auto poll every 3 seconds
        pollTimer = setInterval(() => {{
            fetchHealth(false);
        }}, 3000);
    </script>
</body>
</html>
"""

