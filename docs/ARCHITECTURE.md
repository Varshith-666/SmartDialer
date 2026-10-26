# SmartDialer Architecture & System Design Document

## 1. System Overview

SmartDialer is an enterprise-grade outbound dialing engine engineered in Python, FastAPI, and SQLite. It provides two operational dialing modes:
1. **Progressive Mode**: Deterministic 1:1 agent-bound dialing with strict zero-overdial guarantee.
2. **Predictive Mode**: Erlang/Hazard-rate statistical dialing that maximizes agent occupancy while protected by a non-bypassable Independent Safety Controller.

### End-to-End Pipeline
```
Campaign Manager
      │
      ▼
Borrower Queue
      │
      ▼
Progressive / Predictive Pacing Engine
      │
      ▼
Independent Safety Controller  <--- [Non-Bypassable Firewall]
      │
      ▼
Call Allocator (Atomic Reservation Lock)
      │
      ▼
Telecom Carrier Gateway (Reliable / Chaotic Provider)
      │
      ▼
Event Processor (Idempotent Webhook Consumer & State Coordinator)
```

---

## 2. Core Subsystems

### 2.1 Campaign Manager & Borrower Queue
- **Campaign Manager**: Manages outbound campaigns, targeting criteria, channel selection (`VOICE`, `SMS`, `WHATSAPP`), and strategy toggling between `PROGRESSIVE` and `PREDICTIVE`.
- **Borrower Queue**: Prioritized FIFO queue partitioned by campaign and priority tiers. Maintains lead reservation tokens, retry counts, and last attempt timestamps.

### 2.2 Pacing Engines

#### Progressive Dialer Engine
- **Invariant**: `proposed_calls <= available_agents`.
- **Formula**:
  $$\text{Proposed Calls} = \min(N_{\text{available}}, N_{\text{queued\_borrowers}})$$
- **Guarantees**: Deterministic 0% probability of agent starvation or abandoned calls caused by dialer overdialing.

#### Predictive Pacing Engine
- **Objective**: Overcome dead telephony setup and ringing latency ($t_{\text{setup}}$) and low connection rates ($p_{\text{ans}}$) by launching speculative calls ahead of agent availability.
- **Mathematical Model**:
  - $N_{\text{available}}$: Agents ready for assignment (`AVAILABLE`).
  - $N_{\text{connected}}$: Agents currently on active calls (`CONNECTED`).
  - $T_{\text{talk}}$: Mean talk time (empirically 452.9s in real dataset, 120s baseline).
  - $t_{\text{setup}}$: Call setup, carrier signaling, and ring duration (default 5.0s).
  - $E_{\text{free}}$: Expected agents completing their calls during the ring window:
    $$E_{\text{free}} = N_{\text{connected}} \times \left(\frac{t_{\text{setup}}}{T_{\text{talk}}}\right)$$
  - $N_{\text{capacity}} = N_{\text{available}} + E_{\text{free}}$: Total projected agent capacity when new calls answer.
  - $N_{\text{in\_flight}}$: Calls currently ringing or initiated across carriers.
  - $p_{\text{eff}} = p_{\text{ans}} \times (1 - p_{\text{fail}})$: Effective answer probability adjusted for network drops.
  - $E_{\text{answers\_pending}} = N_{\text{in\_flight}} \times p_{\text{eff}}$: Answers expected from already launched calls.
  - $\text{Net Needed} = \max(0, N_{\text{capacity}} - E_{\text{answers\_pending}})$.
  - **Proposed Calls**:
    $$\text{Proposed Calls} = \min\left(\left\lfloor \frac{\text{Net Needed}}{p_{\text{eff}}} \right\rfloor, N_{\text{queued}}\right)$$

---

### 2.3 Independent Safety Controller (Firewall)

The Safety Controller acts as an unbypassable gatekeeper between the statistical pacing engine and telephony hardware. It evaluates 5 deterministic rules:

1. **Circuit Breaker (Carrier Outage)**:
   - If carrier timeout/failure rate exceeds 15%, the controller trips the circuit breaker and forces an immediate fallback to `PROGRESSIVE` mode.
2. **Overdial Ratio Ceiling**:
   - Caps total active and proposed calls to a maximum multiplier of available agent capacity:
     $$\text{Max Allowed Calls} = \lfloor (N_{\text{available}} + E_{\text{free}}) \times \text{MAX\_OVERDIAL\_RATIO} \rfloor$$
   - If pacing exceeds this ratio, the controller issues a `REDUCE` decision.
3. **Minimum Agent Quorum**:
   - If available agents drop below 2 while calls are in flight, predictive statistics become unstable (the law of large numbers collapses). The controller triggers `FORCE_PROGRESSIVE`.
4. **Regulatory Abandonment Rate Guardrail**:
   - If historical or moving-average abandoned call rate exceeds 3.0% (FCC/FTC compliance ceiling), the dialer is immediately downgraded to `PROGRESSIVE` mode.
5. **Zero Capacity Halting**:
   - If $N_{\text{available}} == 0$ and $E_{\text{free}} < 0.5$, dialing is `REJECTED` (0 calls).

---

### 2.4 Call Allocator & Concurrency Architecture

- **Atomic Reservation Lock**:
  Uses SQLite `BEGIN IMMEDIATE` transactions with a unique UUID `reservation_token` and TTL (`reservation_expires_at = datetime('now', '+30 seconds')`).
- **Race Condition Prevention**:
  When concurrent workers race to allocate leads and agents, the database serializes reservations at transaction boundaries. Only one worker claims a given lead or agent.
- **Dangling Lock Reaper**:
  A background recovery routine reaps expired reservations older than 30s, returning abandoned agents to `AVAILABLE` and leads to `QUEUED`.

---

### 2.5 Telecom Provider Interface & Event Processing

- **`ReliableTelecomProvider`**: Fast, predictable carrier simulation for unit tests and nominal workloads.
- **`ChaoticTelecomProvider`**: Simulates real-world telephony chaos:
  - Jitter and carrier timeouts (`ProviderTimeoutError`).
  - Network 500 drops (`CIRCUIT_RESET_BY_PEER`).
  - Duplicate events (e.g. repeated `ANSWERED` callbacks).
  - Out-of-order events (e.g. `COMPLETED` arriving before `ANSWERED`).
- **`EventProcessor`**:
  - Enforces database idempotency keys on every carrier webhook.
  - Recovers gracefully from out-of-order `COMPLETED` packets without crashing or leaking agent reservations.

---

## 3. High-Scale Bottleneck Analysis & Scaling Strategy

### Measured Benchmarks (Single SQLite Instance)
- **100 Agents**: 22 ms cycle latency (11,315 calls/sec throughput)
- **1,000 Agents**: 167 ms cycle latency (14,970 calls/sec throughput)
- **10,000 Agents**: 2,318 ms cycle latency (10,784 calls/sec throughput)

### Key Bottlenecks Identified

1. **SQLite Database Write Serialization**:
   - *Limitation*: SQLite supports concurrent readers in WAL mode, but only one writer can hold the write lock at any time.
   - *Symptom*: At 10,000 agents, bulk updating 25,000 call and agent records causes transaction execution time to rise to 2.3 seconds.
2. **Row Contention on Hot Queues**:
   - *Limitation*: Standard `LIMIT` queries in concurrent workers create lock contention if workers poll the same table offsets.
3. **In-Memory Event Loops & Thread Sleep**:
   - *Limitation*: Synchronous latency sleeps block Python worker threads under heavy concurrency.

### Targeted Enterprise Scaling Recommendations

1. **Database Migration to PostgreSQL with `SKIP LOCKED`**:
   Replace table-level locking with row-level non-blocking reservation:
   ```sql
   UPDATE campaign_borrower_queue
   SET status = 'RESERVED', reservation_token = $1, reservation_expires_at = NOW() + INTERVAL '30 seconds'
   WHERE queue_id IN (
       SELECT queue_id FROM campaign_borrower_queue
       WHERE campaign_id = $2 AND status = 'QUEUED'
       ORDER BY priority ASC, queue_id ASC
       FOR UPDATE SKIP LOCKED
       LIMIT $3
   );
   ```
   *Benefit*: Allows 50+ concurrent dialing worker processes to pull batches with zero lock contention.

2. **Distributed Queue Architecture with Redis Streams / Celery**:
   - Decouple the Pacing Engine from Call Dispatch using an event-driven message bus (Redis Streams or RabbitMQ).
   - The Pacing Engine publishes dispatch requests; independent pool workers consume tokens and trigger carrier SIP trunks asynchronously.

3. **Campaign-Based Sharding**:
   - Partition borrower queues and agent allocations by `campaign_id` or `tenant_id`. Different campaigns operate completely in parallel on separate partitions.
