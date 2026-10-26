"""Simulation Suite: Evaluates Scenarios A, B, C, and D with real engine executions."""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.engine.dialer_worker import DialerWorker
from smart_dialer.models.enums import DialerMode
from smart_dialer.providers.reliable_provider import ReliableTelecomProvider
from smart_dialer.providers.chaotic_provider import ChaoticTelecomProvider


def setup_simulation_environment(
    db_path: str,
    campaign_id: str,
    num_agents: int = 50,
    num_borrowers: int = 300,
) -> None:
    """Prepare clean database environment with seeded agents and leads."""
    if os.path.exists(db_path):
        os.remove(db_path)

    init_db(db_path)

    with get_db(db_path) as conn:
        with transaction(conn) as cursor:
            # Create Campaign in PREDICTIVE mode
            cursor.execute(
                """
                INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode)
                VALUES (?, ?, 'PREDICTIVE')
                """,
                (campaign_id, f"Sim Campaign {campaign_id}"),
            )

            # Insert Agents
            for i in range(num_agents):
                cursor.execute(
                    """
                    INSERT INTO agents (agent_id, agent_name, status)
                    VALUES (?, ?, 'AVAILABLE')
                    """,
                    (f"AGT_SIM_{i:04d}", f"Agent {i}"),
                )

            # Insert Borrowers into queue
            for i in range(num_borrowers):
                b_id = f"BRW_SIM_{i:04d}"
                cursor.execute(
                    """
                    INSERT INTO borrowers (borrower_id, name, phone)
                    VALUES (?, ?, ?)
                    """,
                    (b_id, f"Lead {i}", f"987654{i:04d}"),
                )
                cursor.execute(
                    """
                    INSERT INTO campaign_borrower_queue (campaign_id, borrower_id, status)
                    VALUES (?, ?, 'QUEUED')
                    """,
                    (campaign_id, b_id),
                )


def run_scenario(
    scenario_name: str,
    db_path: str,
    num_cycles: int,
    answer_rate: float,
    talk_time: float,
    provider_type: str = "reliable",
    provider_failure_rate: float = 0.05,
    provider_latency_ms: int = 0,
    dynamic_shift: bool = False,
) -> Dict[str, Any]:
    """Execute multi-cycle dialer simulation and collect real metrics."""
    campaign_id = f"CMP_{scenario_name}"
    setup_simulation_environment(db_path, campaign_id, num_agents=50, num_borrowers=500)

    # Instantiate Provider
    if provider_type == "chaotic":
        provider = ChaoticTelecomProvider(
            failure_rate=provider_failure_rate,
            answer_rate=answer_rate,
        )
    else:
        provider = ReliableTelecomProvider(
            failure_rate=provider_failure_rate,
            answer_rate=answer_rate,
            latency_ms=provider_latency_ms,
        )

    current_ans_rate = answer_rate
    current_talk_time = talk_time

    cycle_logs: List[Dict[str, Any]] = []

    with get_db(db_path) as conn:
        for c in range(1, num_cycles + 1):
            # Dynamic Shift for Scenario D
            if dynamic_shift and c > (num_cycles // 2):
                current_ans_rate = 0.15  # Drops from 70% to 15%
                current_talk_time = 60.0

            worker = DialerWorker(
                provider=provider,
                custom_answer_rate=current_ans_rate,
                custom_talk_time=current_talk_time,
            )

            cycle_out = worker.run_cycle(
                conn,
                campaign_id=campaign_id,
                force_mode=DialerMode.PREDICTIVE,
                simulate_telephony_events=True,
            )
            cycle_logs.append(cycle_out)

            # Release some agents from WRAP_UP back to AVAILABLE for next cycle
            with transaction(conn) as cursor:
                cursor.execute("UPDATE agents SET status = 'AVAILABLE' WHERE status = 'WRAP_UP'")

        # Aggregate Real Metrics from DB
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM calls WHERE campaign_id = ?", (campaign_id,))
        total_calls = cursor.fetchone()["c"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM calls WHERE campaign_id = ? AND call_status IN ('ANSWERED', 'CONNECTED', 'COMPLETED')",
            (campaign_id,),
        )
        total_answered = cursor.fetchone()["c"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM calls WHERE campaign_id = ? AND call_status = 'COMPLETED'",
            (campaign_id,),
        )
        total_completed = cursor.fetchone()["c"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM calls WHERE campaign_id = ? AND call_status = 'FAILED'",
            (campaign_id,),
        )
        total_failed = cursor.fetchone()["c"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM calls WHERE campaign_id = ? AND call_status = 'CONNECTED'",
            (campaign_id,),
        )
        total_connected = cursor.fetchone()["c"]

        # Safety Controller Statistics
        cursor.execute(
            "SELECT decision, COUNT(*) as c FROM safety_controller_audit WHERE campaign_id = ? GROUP BY decision",
            (campaign_id,),
        )
        safety_decisions = {r["decision"]: r["c"] for r in cursor.fetchall()}

        # Proposed vs Approved
        total_proposed = sum(c["pacing_result"].get("proposed_calls", 0) for c in cycle_logs)
        total_approved = sum(c["safety_decision"].get("approved_calls", 0) for c in cycle_logs)

        # Agent Utilization
        cursor.execute("SELECT COUNT(*) as c FROM agents")
        total_agents = cursor.fetchone()["c"]

        measured_ans_rate = (total_answered / total_calls * 100.0) if total_calls > 0 else 0.0

    return {
        "scenario": scenario_name,
        "input_parameters": {
            "configured_answer_rate": answer_rate,
            "configured_talk_time_sec": talk_time,
            "provider_type": provider_type,
            "provider_failure_rate": provider_failure_rate,
            "dynamic_shift": dynamic_shift,
            "total_agents": 50,
            "cycles_run": num_cycles,
        },
        "metrics": {
            "calls_initiated": total_calls,
            "calls_answered": total_answered,
            "calls_connected": total_connected,
            "calls_completed": total_completed,
            "calls_failed": total_failed,
            "realized_answer_rate_pct": round(measured_ans_rate, 2),
            "total_proposed_calls": total_proposed,
            "total_approved_calls": total_approved,
            "safety_decisions": safety_decisions,
            "agent_utilization_estimate_pct": round(min(100.0, (total_completed / max(1, total_calls)) * 100.0 * (talk_time / 120.0)), 2),
        },
    }


def run_all_simulations():
    """Run Scenarios A, B, C, and D."""
    print("=" * 80)
    print("SMARTDIALER PREDICTIVE PACING & SAFETY SIMULATION SUITE")
    print("=" * 80)

    db_base = "sim_test.db"
    results = {}

    # Scenario A: 20% answer rate, 120-second average talk time
    print("\n--- Running Scenario A: 20% Answer Rate, 120s Talk Time (Baseline Dataset) ---")
    res_a = run_scenario("SCENARIO_A", db_base, num_cycles=5, answer_rate=0.20, talk_time=120.0)
    results["A"] = res_a

    # Scenario B: 50% answer rate, 90-second average talk time
    print("--- Running Scenario B: 50% Answer Rate, 90s Talk Time ---")
    res_b = run_scenario("SCENARIO_B", db_base, num_cycles=5, answer_rate=0.50, talk_time=90.0)
    results["B"] = res_b

    # Scenario C: 70% answer rate, 180-second average talk time
    print("--- Running Scenario C: 70% Answer Rate, 180s Talk Time ---")
    res_c = run_scenario("SCENARIO_C", db_base, num_cycles=5, answer_rate=0.70, talk_time=180.0)
    results["C"] = res_c

    # Scenario D: Changing answer rates and durations with chaotic provider
    print("--- Running Scenario D: Dynamic Shift (70% -> 15%) with Chaotic Provider ---")
    res_d = run_scenario(
        "SCENARIO_D",
        db_base,
        num_cycles=8,
        answer_rate=0.70,
        talk_time=180.0,
        provider_type="chaotic",
        provider_failure_rate=0.15,
        dynamic_shift=True,
    )
    results["D"] = res_d

    # Cleanup temp db
    if os.path.exists(db_base):
        try:
            os.remove(db_base)
        except Exception:
            pass

    # Print Summary Table
    print("\n" + "=" * 90)
    print(f"{'Scenario':<12} | {'Proposed':<9} | {'Approved':<9} | {'Initiated':<10} | {'Answered':<9} | {'Completed':<10} | {'Failed':<8} | {'Ans Rate':<8}")
    print("-" * 90)
    for key, data in results.items():
        m = data["metrics"]
        print(
            f"{data['scenario']:<12} | {m['total_proposed_calls']:<9} | {m['total_approved_calls']:<9} | "
            f"{m['calls_initiated']:<10} | {m['calls_answered']:<9} | {m['calls_completed']:<10} | "
            f"{m['calls_failed']:<8} | {m['realized_answer_rate_pct']:>6.1f}%"
        )
    print("=" * 90)

    # Save to JSON
    out_file = "simulation_report.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed simulation report persisted to {out_file}.")
    return results


if __name__ == "__main__":
    run_all_simulations()
