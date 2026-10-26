"""SmartDialer High-Scale Load Testing Script (100, 1,000, and 10,000 Agents)."""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from smart_dialer.db.connection import init_db, get_db, transaction
from smart_dialer.dialer.predictive import PredictivePacingEngine
from smart_dialer.dialer.safety_controller import SafetyController
from smart_dialer.dialer.call_allocator import CallAllocator
from smart_dialer.engine.dialer_worker import DialerWorker
from smart_dialer.models.enums import DialerMode


def run_benchmark_tier(agent_count: int, db_path: str) -> Dict[str, Any]:
    """Run dialer cycle benchmark against specific agent capacity tier."""
    if os.path.exists(db_path):
        os.remove(db_path)

    init_db(db_path)

    campaign_id = f"CMP_LOAD_{agent_count}"
    lead_count = agent_count * 5  # 5x lead inventory

    # 1. Measure Seed Ingestion Time
    t_seed_start = time.perf_counter()
    with get_db(db_path) as conn:
        with transaction(conn) as cursor:
            cursor.execute(
                "INSERT INTO campaigns (campaign_id, campaign_name, dialer_mode) VALUES (?, ?, 'PREDICTIVE')",
                (campaign_id, f"Load Test {agent_count}"),
            )

            # Bulk insert agents
            agent_records = [
                (f"AGT_{agent_count}_{i:05d}", f"Agent {i}", "AVAILABLE")
                for i in range(agent_count)
            ]
            cursor.executemany(
                "INSERT INTO agents (agent_id, agent_name, status) VALUES (?, ?, ?)",
                agent_records,
            )

            # Bulk insert borrowers & queue
            borrower_records = [
                (f"BRW_{agent_count}_{i:06d}", f"Lead {i}", f"987{i:07d}")
                for i in range(lead_count)
            ]
            cursor.executemany(
                "INSERT INTO borrowers (borrower_id, name, phone) VALUES (?, ?, ?)",
                borrower_records,
            )

            queue_records = [
                (campaign_id, f"BRW_{agent_count}_{i:06d}", 1, "QUEUED")
                for i in range(lead_count)
            ]
            cursor.executemany(
                "INSERT INTO campaign_borrower_queue (campaign_id, borrower_id, priority, status) VALUES (?, ?, ?, ?)",
                queue_records,
            )

    t_seed = (time.perf_counter() - t_seed_start) * 1000.0

    # 2. Benchmark Dialer Pipeline Execution
    with get_db(db_path) as conn:
        # Measure Pacing Engine
        t_pace_start = time.perf_counter()
        pacing_result = PredictivePacingEngine.calculate_calls_to_dial(
            conn, campaign_id, custom_answer_rate=0.25, custom_talk_time=120.0
        )
        t_pace_ms = (time.perf_counter() - t_pace_start) * 1000.0

        # Measure Safety Controller
        t_safe_start = time.perf_counter()
        safety_eval = SafetyController.evaluate(conn, campaign_id, pacing_result)
        t_safe_ms = (time.perf_counter() - t_safe_start) * 1000.0

        approved_calls = safety_eval["approved_calls"]

        # Measure Atomic Allocation (Locking & Reservation)
        t_alloc_start = time.perf_counter()
        allocated = CallAllocator.allocate_calls(conn, campaign_id, approved_calls)
        t_alloc_ms = (time.perf_counter() - t_alloc_start) * 1000.0

    total_pipeline_ms = t_pace_ms + t_safe_ms + t_alloc_ms
    allocated_count = len(allocated)
    throughput_cps = (allocated_count / (total_pipeline_ms / 1000.0)) if total_pipeline_ms > 0 else 0.0

    # Cleanup temp db
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    return {
        "agents": agent_count,
        "leads_queued": lead_count,
        "seed_time_ms": round(t_seed, 2),
        "pacing_time_ms": round(t_pace_ms, 3),
        "safety_time_ms": round(t_safe_ms, 3),
        "allocation_time_ms": round(t_alloc_ms, 3),
        "total_cycle_time_ms": round(total_pipeline_ms, 2),
        "calls_proposed": pacing_result["proposed_calls"],
        "calls_approved": approved_calls,
        "calls_allocated": allocated_count,
        "throughput_calls_per_sec": round(throughput_cps, 1),
    }


def run_all_benchmarks():
    print("=" * 85)
    print("SMARTDIALER HIGH-SCALE BENCHMARK (100, 1,000, and 10,000 AGENTS)")
    print("=" * 85)

    tiers = [100, 1000, 10000]
    results = []

    for t in tiers:
        print(f"\nBenchmarking tier: {t:,} agents ...")
        db_file = f"load_test_{t}.db"
        res = run_benchmark_tier(t, db_file)
        results.append(res)
        print(f"  Cycle Latency: {res['total_cycle_time_ms']} ms | Allocated: {res['calls_allocated']:,} calls | Throughput: {res['throughput_calls_per_sec']:,} calls/sec")

    print("\n" + "=" * 95)
    print(f"{'Agents':<8} | {'Queued':<8} | {'Pacing (ms)':<12} | {'Safety (ms)':<12} | {'Alloc (ms)':<12} | {'Total (ms)':<11} | {'Throughput (cps)':<16}")
    print("-" * 95)
    for r in results:
        print(
            f"{r['agents']:<8,d} | {r['leads_queued']:<8,d} | {r['pacing_time_ms']:<12.3f} | {r['safety_time_ms']:<12.3f} | "
            f"{r['allocation_time_ms']:<12.2f} | {r['total_cycle_time_ms']:<11.2f} | {r['throughput_calls_per_sec']:>16,.1f}"
        )
    print("=" * 95)


if __name__ == "__main__":
    run_all_benchmarks()
