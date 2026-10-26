"""ETL Module: Validates, cleans, and imports the real collections dataset."""

import os
import sqlite3
import pandas as pd
from typing import Dict, Any, Optional
from smart_dialer.config import settings
from smart_dialer.db.connection import get_db, init_db, transaction


def clean_and_import_dataset(
    dataset_dir: Optional[str] = None,
    db_path: Optional[str] = None,
    sample_borrower_limit: Optional[int] = None,
    sample_agent_limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Import and normalize real dataset from collections_30k_dataset into SQLite.
    Performs data cleaning:
      - Deduplicates borrowers and filters out null phone records.
      - Maps agent statuses (ACTIVE -> AVAILABLE, others -> OFFLINE).
      - Computes empirical baseline stats from calls.csv (answer rate, duration).
    """
    src_dir = dataset_dir or settings.DATASET_DIR
    target_db = db_path or settings.DB_PATH

    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Dataset directory not found at: {src_dir}")

    # Ensure schema initialized
    init_db(target_db)

    stats_summary: Dict[str, Any] = {}

    with get_db(target_db) as conn:
        with transaction(conn) as cursor:
            # 1. Telephony Vendors
            vendors_csv = os.path.join(src_dir, "vendor_telephony.csv")
            if os.path.exists(vendors_csv):
                vendors_df = pd.read_csv(vendors_csv)
                for _, row in vendors_df.iterrows():
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO vendors (vendor_id, vendor_name, vendor_account_id, status)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            row["vendor_id"],
                            row["vendor_name"],
                            str(row.get("vendor_account_id", "")),
                            row["status"],
                        ),
                    )
                stats_summary["imported_vendors"] = len(vendors_df)

            # Insert default vendor fallback
            cursor.execute(
                """
                INSERT OR IGNORE INTO vendors (vendor_id, vendor_name, status)
                VALUES ('VND_DEFAULT', 'Default Carrier Gateway', 'ACTIVE')
                """
            )

            # 2. Campaigns
            campaigns_csv = os.path.join(src_dir, "campaigns.csv")
            imported_camps = 0
            if os.path.exists(campaigns_csv):
                camp_df = pd.read_csv(campaigns_csv)
                for _, row in camp_df.iterrows():
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO campaigns (
                            campaign_id, campaign_name, channel, strategy_version,
                            target_definition, dialer_mode
                        )
                        VALUES (?, ?, ?, ?, ?, 'PROGRESSIVE')
                        """,
                        (
                            row["campaign_id"],
                            row["campaign_name"],
                            row["channel"],
                            str(row.get("strategy_version", "v1")),
                            str(row.get("target_definition", "")),
                        ),
                    )
                    imported_camps += 1
                stats_summary["imported_campaigns"] = imported_camps

            # 3. Agents
            agents_csv = os.path.join(src_dir, "agents.csv")
            imported_agents = 0
            if os.path.exists(agents_csv):
                agents_df = pd.read_csv(agents_csv)
                if sample_agent_limit:
                    agents_df = agents_df.head(sample_agent_limit)

                for _, row in agents_df.iterrows():
                    # Map raw status: ACTIVE -> AVAILABLE, INACTIVE/SUSPENDED -> OFFLINE
                    raw_status = str(row.get("status", "ACTIVE")).upper()
                    status = "AVAILABLE" if raw_status == "ACTIVE" else "OFFLINE"

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO agents (
                            agent_id, employee_code, agent_name, vendor_id, team, status
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["agent_id"],
                            str(row.get("employee_code", "")),
                            row["agent_name"],
                            str(row.get("vendor_id", "")),
                            str(row.get("team", "Default")),
                            status,
                        ),
                    )
                    imported_agents += 1
                stats_summary["imported_agents"] = imported_agents

            # 4. Borrowers (Data Cleaning: Drop null phones, deduplicate)
            borrowers_csv = os.path.join(src_dir, "borrowers.csv")
            imported_borrowers = 0
            if os.path.exists(borrowers_csv):
                borrowers_df = pd.read_csv(borrowers_csv)
                # Filter null/empty phones
                clean_borrowers = borrowers_df.dropna(subset=["phone"]).drop_duplicates(subset=["borrower_id"])
                if sample_borrower_limit:
                    clean_borrowers = clean_borrowers.head(sample_borrower_limit)

                for _, row in clean_borrowers.iterrows():
                    phone_val = str(int(row["phone"])) if pd.notnull(row["phone"]) else "0000000000"
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO borrowers (
                            borrower_id, name, phone, email, city, state
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["borrower_id"],
                            row["name"],
                            phone_val,
                            str(row.get("email", "")),
                            str(row.get("city", "")),
                            str(row.get("state", "")),
                        ),
                    )
                    imported_borrowers += 1
                stats_summary["imported_borrowers"] = imported_borrowers

            # 5. Compute Empirical Call Stats from calls.csv
            calls_csv = os.path.join(src_dir, "calls.csv")
            if os.path.exists(calls_csv):
                calls_df = pd.read_csv(calls_csv)
                total_calls = len(calls_df)
                ans_count = (calls_df["call_status"] == "ANSWERED").sum()
                ans_rate = ans_count / total_calls if total_calls > 0 else 0.20
                avg_duration = calls_df[calls_df["call_status"] == "ANSWERED"]["duration_sec"].mean()
                if pd.isna(avg_duration):
                    avg_duration = 120.0

                stats_summary["empirical_total_calls"] = int(total_calls)
                stats_summary["empirical_answer_rate"] = round(float(ans_rate), 4)
                stats_summary["empirical_avg_duration_sec"] = round(float(avg_duration), 2)

                cursor.execute(
                    "INSERT OR REPLACE INTO dialer_stats_cache (stat_key, stat_value) VALUES ('HISTORICAL_ANSWER_RATE', ?)",
                    (float(ans_rate),),
                )
                cursor.execute(
                    "INSERT OR REPLACE INTO dialer_stats_cache (stat_key, stat_value) VALUES ('HISTORICAL_AVG_DURATION_SEC', ?)",
                    (float(avg_duration),),
                )

    return stats_summary


if __name__ == "__main__":
    print("Running SmartDialer ETL Import...")
    result = clean_and_import_dataset(sample_borrower_limit=5000, sample_agent_limit=1000)
    print("ETL Import Complete. Summary:")
    for k, v in result.items():
        print(f"  {k}: {v}")
