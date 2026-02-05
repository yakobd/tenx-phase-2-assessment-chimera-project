# Project Chimera — Source of Truth (Engineering Specification)

Version: 1.0
Last updated: 2026-02-05

Purpose: This document is the canonical engineering specification for Project Chimera. It defines Vision, Core Architecture, Technical Constraints, and Governance controls that all agents, services, and operators must adhere to. Implementations must reference this file as the Source of Truth and surface `mcp_request` envelopes and signed audit metadata for all external interactions.

## Vision

Project Chimera is a High‑Governance Node for autonomous influencers: a policy-first coordination point that issues, verifies, and audits autonomous actions (content posts, promotions, and agentic payments). Chimera balances autonomous execution with enforceable safety controls and tamper‑evident auditability so that strategic intents translate into accountable, traceable outcomes.

## Strategic Objective

Solve the Creative Supply Chain failure by making high-quality, safe, and auditable influencer content programmatically scalable and commercially viable. Chimera enables three complementary business models, each realized and secured by the technical architecture:

1. Digital Talent Agency — operate, manage, and monetize owned AI influencers (content creation, brand deals, creator payouts) under a centralized governance and audit model.
2. Chimera OS (Platform-as-a-Service) — license the governance, FastRender orchestration, and MCP tooling to brands and creative platforms as a secure PaaS for autonomous content workflows.
3. Hybrid Ecosystem — combine owned AI talent and third-party creators into a federated marketplace using Agentic Commerce, enabling shared monetization and on‑platform payments.

The Core Architecture (FastRender Hierarchical Swarm, MCP envelopes, PostgreSQL audit store, and Weaviate semantic memory) is the enabler for these models — providing scalability, low-latency execution, tamper-evident traceability, and auditable financial rails (via AgentKit) required for commercial adoption.

## Core Architecture — FastRender Hierarchical Swarm

Overview:

- Roles: `Planner` (strategic intent), `Worker` (parallel rendering & execution), `Judge` (safety & compliance).
- Pattern: FastRender Hierarchical Swarm — Workers operate in horizontally scaled pools to render candidate artifacts in parallel (FastRender). An ensemble aggregator computes agreement; the Planner coordinates campaign-level scheduling and budgets; the Judge validates and can veto.

Key guarantees:

- Low-latency render-to-publish through parallel candidate generation and fast consensus rounds.
- Hierarchical coordination enabling campaign specialization and prioritized resource allocation.
- Clear separation of concerns: Planner for intent and strategy, Worker for execution, Judge for safety.

## Technical Constraints

- Language/runtime: Python 3.12+ for all services and agents.
- Persistence: PostgreSQL for canonical metadata, campaign state, and audit envelopes; use `UUID` primary keys and `JSONB` for audit/policy payloads.
- Semantic memory: Weaviate for vector embeddings and semantic search; reference Weaviate IDs from PostgreSQL (`embedding_ref`/`semantic_ref`).
- All external tool/service access MUST be proxied through MCP (Model‑Context‑Proxy). Direct external calls from agents or services are prohibited.

## Governance

Confidence Threshold:

- Autonomous publish decision requires `calibrated_confidence >= 0.85`.

Decision Rule (publish precondition):

- Publish only when all of the following are true:
  - `ensemble_agreement >= ensemble_threshold` (configurable per campaign)
  - `calibrated_confidence >= 0.85`
  - `Judge.verdict == "pass"`

If any condition fails, the artifact must be marked `needs_review` and follow the escalation policy (Planner review or human audit) depending on policy severity.

Safety Overrides:

- The `Judge` may block publishing regardless of confidence for policy violations (toxicity, copyright, legal/regulatory). All Judge decisions must be signed and stored in audit envelopes.

Audit & Traceability:

- Every Planner intent, Worker artifact, Judge verdict, publish, rollback, and payment must include an `mcp_request` envelope and a signed audit entry saved in PostgreSQL `JSONB` fields.
- Proof‑of‑Intent (PoI) handshakes and OpenClaw ACK receipts must be persisted and linked to the relevant Campaign records.

## Stakeholders & Roles

- Planner: defines strategy, canonicalized signed intents, and acceptance criteria.
- Worker: renders candidate artifacts, computes local ensemble signals, and submits artifacts for Judge validation.
- Judge: performs automated safety checks, issues signed verdicts, and triggers rollbacks or escalations.

## Source-of-Truth Directives

- This file (`specs/_meta.md`) is the canonical engineering specification. Any divergence in code, agents, or deployment must be reconciled and documented here.
- Changes to governance thresholds, policy versions, or core architectural patterns require a versioned update to this file and a signed change log stored in the audit store.

## Implementation Guidance

- Implement ensemble scoring and confidence calibration pipelines; maintain held-out validation datasets and rolling production drift checks to ensure the 0.85 threshold remains meaningful.
- Use MCP envelopes for all inter-agent messaging and external calls; enforce envelope validation in ingress adapters.
- Store all cryptographic signatures, PoI envelopes, and OpenClaw ACK receipts in PostgreSQL `audit` JSONB for forensic preservation.

## References

- Research/architecture_strategy.md (Persistence Layer, Domain Architecture)
- Research/strategic_analysis.md (Executive Synthesis, Social Protocols)
