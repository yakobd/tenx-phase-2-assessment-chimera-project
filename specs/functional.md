# Project Chimera — Functional User Stories

Format: AS AN [Agent Role],

I NEED TO [Action],

SO THAT [Value].

---

## Epic 1: Agent Cognition & Campaign Execution

AS AN Planner,

I NEED TO sense and aggregate trending signals from MoltBook and other social sources via MCP,

SO THAT I CAN produce canonicalized campaign intents (Proof‑of‑Intent) aligned with emergent audience signals.

---

AS AN Planner,

I NEED TO sign and publish a Proof‑of‑Intent (PoI) envelope to the OpenClaw mesh via MCP,

SO THAT the swarm and external validators can ACK, verify provenance, and coordinate campaign scheduling.

---

AS AN Planner,

I NEED TO prioritize campaign objectives and allocate budgets/worker-capacity using ensemble trend summaries,

SO THAT high-impact topics receive appropriate rendering resources within the FastRender Hierarchical Swarm.

---

## Epic 2: Content Creation & Moderation

AS AN Worker,

I NEED TO accept trend-context payloads (MCP) and generate high-quality video content using declared skillsets (scripting, editing, rendering, captioning),

SO THAT I CAN produce candidate artifacts that maximize ensemble agreement and calibrated confidence.

---

AS AN Worker,

I NEED TO attach rendering telemetry, versioned model metadata, and semantic memory references (Weaviate IDs) to each artifact and submit them to Judge via MCP,

SO THAT the Judge and audit pipelines can reproduce, validate, and score each candidate.

---

AS AN Worker,

I NEED TO participate in FastRender consensus rounds (ensemble scoring) and report local agreement metrics,

SO THAT a consolidated ensemble_score can be computed to determine publishability against governance thresholds.

---

AS AN Judge,

I NEED TO validate artifacts against multi-stage safety rules (toxicity, copyright, factuality, reputation) using approved MCP tools,

SO THAT I CAN issue a signed verdict (`pass|fail|needs_review`) and supply a calibrated confidence score and explainability payload.

---

AS AN Judge,

I NEED TO enforce the governance publish rule requiring `calibrated_confidence >= 0.85` (combined with ensemble agreement),

SO THAT autonomous publishes meet the safety and quality bar defined by governance.

---

## Epic 3: Social Interaction & Agentic Commerce

AS AN CFO,

I NEED TO authorize and execute Agentic Commerce wallet transactions via the Coinbase AgentKit through MCP (payouts, promotions, refunds),

SO THAT financial flows are auditable and atomic relative to publish events and campaign settlements.

---

AS AN CFO,

I NEED TO receive tamper-evident audit envelopes (Planner PoI, Worker artifact, Judge verdict) before signing payments,

SO THAT every disbursement is defensible, traceable, and reversible when policy violations are discovered.

---

AS AN System,

I NEED TO emit Proof‑of‑Intent announcements, availability heartbeats, and receive OpenClaw ACKs via MCP,

SO THAT the node's operational state, active intents, and validator receipts are globally discoverable and auditable.

---

## Epic 4: System Orchestration & Governance

AS AN User,

I NEED TO monitor the swarm via the HITL dashboard (campaign health, rolling confidence distributions, safety incidents, and payment ledger),

SO THAT I CAN intervene (pause, throttle, escalate) and audit decisions produced by the Planner/Worker/Judge pipeline.

---

Notes:

- All inter-agent messages, trend fetches, validation calls, and payment actions MUST be proxied through MCP with `mcp_request`/`mcp_response` envelopes.
- Worker skill declarations should be typed (e.g., `video:render:v1`, `audio:mix:v2`) and discoverable via registry to enable specialized assignment.
- Any publish event must satisfy ensemble and Judge checks; otherwise it must be marked `needs_review` and follow escalation workflows surfaced in the HITL dashboard.

- All external data, tool calls, and payments must flow through MCP for visibility and control.
- Trend sensing stories should integrate with the FastRender Swarm: Workers should accept trend-context and return ensemble artifacts for Judge validation.
- Agentic Commerce flows MUST include tamper-evident audit payloads and require Judge sign-off when policy flags are present.
