# Project Chimera — Tooling & MCP Strategy

## Developer MCP Servers (System Level)

To assist in the development of Chimera, the following MCP servers are configured:

1. **Filesystem MCP:** Enables the AI to read/write to the `specs/` and `skills/` directories with high precision.
2. **Git MCP:** Ensures every major change is staged and committed with the correct "Orchestrator" nomenclature.
3. **PostgreSQL MCP:** Allows the AI to verify schema migrations and inspect the `campaign_metadata` JSONB audit logs.

## Agent MCP Tools (Runtime Level)

These tools are exposed to the swarm for autonomous execution, with contracts defined in individual skill READMEs:

- **`trend_analyzer`** ([README](./skills/trend_analyzer/)): Fetches and scores trends from MoltBook and social APIs.
- **`video_assembler`** ([README](./skills/video_assembler/)): Assembles video artifacts using MCP video generation tools.
- **`safety_judge`** ([README](./skills/safety_judge/)): Validates content safety and enforces governance thresholds.
- **`agentkit_wallet`** (Financial Skill): Proxied interface for Coinbase AgentKit transactions.

---

## 1. Strategic Objective

This document selects and organizes MCP tools to empower both developers and autonomous agents, aligning tool capabilities with the FastRender Swarm architecture (Planner, Worker, Judge). The goal is to reduce developer friction while enabling auditable, proxied access to external services for safe agent autonomy.

## 2. MCP Tooling Taxonomy

| Category               | Tool Name        | MCP Server / Source                 | Purpose                                                            | User / Accessor                 |
| ---------------------- | ---------------- | ----------------------------------- | ------------------------------------------------------------------ | ------------------------------- |
| Developer Productivity | Filesystem MCP   | `mcp-filesystem`                    | Read/write project files, targeted edits in `specs/` and `skills/` | Developer (via AI Co-pilot)     |
| Developer Productivity | Git MCP          | `mcp-git`                           | Stage/commit/push changes with standardized commit messages        | Developer (via AI Co-pilot)     |
| Developer Productivity | PostgreSQL MCP   | `mcp-postgres`                      | Inspect schemas, run safe read-only queries against dev DB         | Developer (via AI Co-pilot)     |
| Agent Runtime Skill    | fetch_trends     | `mcp-fetch-trends` (moltbook proxy) | Trend sensing and ensemble signals for Planner                     | Planner Agent                   |
| Agent Runtime Skill    | validate_content | `mcp-safety` (judge proxy)          | Content safety evaluation and verdicts for Judge                   | Judge Agent                     |
| Agent Runtime Skill    | agentkit_wallet  | `mcp-agentkit`                      | Agentic payments and wallet operations (AgentKit)                  | Planner / Worker / Judge Agents |

## 3. Developer Tooling Deep Dive

### Filesystem MCP

- Configuration: STDIO transport with root path set to the project workspace. Access controlled by an allowlist limiting paths to `specs/`, `skills/`, and `src/`.
- Use Case Example: The AI co-pilot writes a new Pydantic model into `src/models/` and updates `skills/README.md`, committing the change via the Git MCP.
- Security Consideration: Scope the MCP to read/write only to explicit directories and require explicit approval for destructive operations.

### Git MCP

- Configuration: SSH or token-backed transport configured for a developer sandbox branch. Commit message template enforced (e.g., "Orchestrator: <summary> (#issue)").
- Use Case Example: Auto-generate commit messages referencing changed `specs/` files and include links to PR tickets produced by the co-pilot.
- Security Consideration: Use least-privilege credentials; require signed commits or CI gating for pushes to protected branches.

### PostgreSQL MCP

- Configuration: Two connections — a read-only connection for schema inspection and a read-write connection restricted to migration runners. Default to read-only for AI interactions.
- Use Case Example: The co-pilot inspects `campaign_metadata` JSONB structure to validate a migration before generating SQL DDL changes.
- Security Consideration: Postgres MCP should use role-based access controls; mask or redact PII when returning query results to agents.

## 4. Agent Runtime Skills Overview

- `fetch_trends`: MCP Server — `mcp-fetch-trends` (proxy to MoltBook/Social APIs). Consumed by: `Planner` (trend-informed campaign objectives).
- `validate_content`: MCP Server — `mcp-safety` (Judge safety stack / content moderation adapters). Consumed by: `Judge` (verdicts and signed decisions) and `Worker` (pre-publish checks).
- `agentkit_wallet`: MCP Server — `mcp-agentkit` (Coinbase AgentKit adapter). Consumed by: `Planner` for payouts and `Worker` for expense settlement.

## 5. Implementation Roadmap (Short-term)

- Phase 1: Configure developer tools for local prototyping.
  - Install and configure `mcp-filesystem`, `mcp-git`, `mcp-postgres` with sandbox creds.
  - Validate read-only Postgres inspection flows.
- Phase 2: Implement stubs for runtime skills.
  - Add lightweight HTTP/MCP stubs for `mcp-fetch-trends`, `mcp-safety`, and `mcp-agentkit` that return canned responses for development.
  - Wire Pydantic schemas and sample MCP envelopes for each stub.
- Phase 3: Integrate skills into agents.
  - Hook `fetch_trends` into Planner's sensing loop.
  - Hook `validate_content` into Judge's decision loop with signature and audit persistence.
  - Add end-to-end tests that exercise the Worker -> Judge -> Planner flows using the stubbed MCP servers.

## 6. Conclusion & Goals

This MCP tooling strategy reduces development friction by giving developers precise, auditable interfaces to the codebase and database while simultaneously enabling safe, proxied agent autonomy. By standardizing MCP servers, using sandboxed stubs during development, and enforcing least-privilege access, the Chimera stack can iterate quickly while preserving traceability and governance.
