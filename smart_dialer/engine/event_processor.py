"""Event Processor: Idempotent event consumer, state coordinator, and anomaly handler."""

import json
import sqlite3
from typing import Dict, Any, Optional
from smart_dialer.db.connection import transaction
from smart_dialer.models.enums import CallState, ProviderEventType, AgentState
from smart_dialer.state_machines.call_state import CallStateMachine, InvalidCallStateTransitionError
from smart_dialer.state_machines.agent_state import AgentStateMachine


class EventProcessor:
    """
    Idempotent, crash-safe telephony event processor.
    Handles duplicate events, out-of-order packets, carrier errors, and agent coordination.
    """

    @classmethod
    def process_event(
        cls,
        conn: sqlite3.Connection,
        event_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process a single carrier event payload with ACID idempotency.
        """
        call_id = event_payload.get("call_id")
        event_type = event_payload.get("event_type")
        idempotency_key = event_payload.get("idempotency_key")
        duration_sec = event_payload.get("duration_sec", 0)
        failure_reason = event_payload.get("failure_reason")

        if not call_id or not event_type:
            raise ValueError("Event must include call_id and event_type.")

        with transaction(conn) as cursor:
            # 1. Idempotency Check via call_events table
            if idempotency_key:
                cursor.execute(
                    "SELECT event_id, created_at FROM call_events WHERE idempotency_key = ?",
                    (idempotency_key,),
                )
                existing = cursor.fetchone()
                if existing:
                    # Duplicate event detected! Return immediately with cached acknowledgment.
                    return {
                        "status": "DUPLICATE_IGNORED",
                        "call_id": call_id,
                        "event_type": event_type,
                        "idempotency_key": idempotency_key,
                        "message": "Duplicate event successfully suppressed by idempotency guard.",
                    }

            # 2. Fetch Call Record
            cursor.execute(
                """
                SELECT call_id, campaign_id, borrower_id, agent_id, call_status
                FROM calls
                WHERE call_id = ?
                """,
                (call_id,),
            )
            call_row = cursor.fetchone()
            if not call_row:
                raise ValueError(f"Call {call_id} not found in database.")

            current_status = CallState(call_row["call_status"])
            agent_id = call_row["agent_id"]
            campaign_id = call_row["campaign_id"]
            borrower_id = call_row["borrower_id"]

            # Map ProviderEventType to Target CallState
            target_status: Optional[CallState] = None
            if event_type == ProviderEventType.INITIATED.value:
                target_status = CallState.INITIATED
            elif event_type == ProviderEventType.RINGING.value:
                target_status = CallState.RINGING
            elif event_type == ProviderEventType.ANSWERED.value:
                target_status = CallState.ANSWERED
            elif event_type == ProviderEventType.CONNECTED.value:
                target_status = CallState.CONNECTED
            elif event_type == ProviderEventType.COMPLETED.value:
                target_status = CallState.COMPLETED
            elif event_type in (
                ProviderEventType.FAILED.value,
                ProviderEventType.BUSY.value,
                ProviderEventType.NO_ANSWER.value,
            ):
                target_status = CallState.FAILED

            if not target_status:
                raise ValueError(f"Unknown or unmapped event_type: {event_type}")

            # 3. Anomaly Handling: Check if call is already in terminal state
            if current_status in (CallState.COMPLETED, CallState.FAILED, CallState.CANCELLED):
                # Out-of-order late arrival: call already completed!
                # Record the event for auditing, but don't regress state.
                cls._record_event_log(
                    cursor, call_id, event_type, current_status.value, current_status.value, idempotency_key, event_payload
                )
                return {
                    "status": "LATE_EVENT_AUDITED",
                    "call_id": call_id,
                    "current_status": current_status.value,
                    "target_status": target_status.value,
                    "message": f"Late event {event_type} audited; call already finalized at {current_status.value}.",
                }

            # 4. Out-of-order handling: COMPLETED arrives before ANSWERED (Scenario 5)
            if target_status == CallState.COMPLETED and current_status in (CallState.INITIATED, CallState.RINGING):
                # Transition directly to COMPLETED
                CallStateMachine.transition(
                    conn, call_id, CallState.COMPLETED, duration_sec=duration_sec, agent_id=agent_id
                )
                cls._mark_queue_completed(cursor, campaign_id, borrower_id)
                cls._record_event_log(
                    cursor, call_id, event_type, current_status.value, CallState.COMPLETED.value, idempotency_key, event_payload
                )
                return {
                    "status": "OUT_OF_ORDER_COMPLETED_RECOVERED",
                    "call_id": call_id,
                    "from_status": current_status.value,
                    "to_status": CallState.COMPLETED.value,
                    "message": "Call completed directly from early ringing phase without crashing.",
                }

            # 5. Normal Valid State Transition
            new_status = CallStateMachine.transition(
                conn,
                call_id,
                target_status,
                duration_sec=duration_sec,
                failure_reason=failure_reason or event_type,
                agent_id=agent_id,
            )

            # Update borrower queue state if terminal
            if new_status == CallState.COMPLETED:
                cls._mark_queue_completed(cursor, campaign_id, borrower_id)
            elif new_status == CallState.FAILED:
                cls._mark_queue_failed(cursor, campaign_id, borrower_id)

            # Record event log
            cls._record_event_log(
                cursor, call_id, event_type, current_status.value, new_status.value, idempotency_key, event_payload
            )

        return {
            "status": "PROCESSED",
            "call_id": call_id,
            "from_status": current_status.value,
            "to_status": new_status.value,
            "agent_id": agent_id,
        }

    @staticmethod
    def _record_event_log(
        cursor: sqlite3.Cursor,
        call_id: str,
        event_type: str,
        from_status: str,
        to_status: str,
        idempotency_key: Optional[str],
        payload: Dict[str, Any],
    ) -> None:
        """Insert event record into call_events table."""
        cursor.execute(
            """
            INSERT INTO call_events (
                call_id, event_type, from_status, to_status,
                idempotency_key, payload
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                call_id,
                event_type,
                from_status,
                to_status,
                idempotency_key,
                json.dumps(payload),
            ),
        )

    @staticmethod
    def _mark_queue_completed(cursor: sqlite3.Cursor, campaign_id: str, borrower_id: str) -> None:
        cursor.execute(
            """
            UPDATE campaign_borrower_queue
            SET status = 'COMPLETED',
                last_attempt_at = CURRENT_TIMESTAMP
            WHERE campaign_id = ? AND borrower_id = ?
            """,
            (campaign_id, borrower_id),
        )

    @staticmethod
    def _mark_queue_failed(cursor: sqlite3.Cursor, campaign_id: str, borrower_id: str) -> None:
        cursor.execute(
            """
            UPDATE campaign_borrower_queue
            SET status = 'FAILED',
                attempts_count = attempts_count + 1,
                last_attempt_at = CURRENT_TIMESTAMP
            WHERE campaign_id = ? AND borrower_id = ?
            """,
            (campaign_id, borrower_id),
        )
