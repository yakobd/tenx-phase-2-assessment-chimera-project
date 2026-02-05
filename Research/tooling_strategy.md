# Project Chimera — Tooling & MCP Strategy

## Developer MCP Servers (System Level)
To assist in the development of Chimera, the following MCP servers are configured:
1. **Filesystem MCP:** Enables the AI to read/write to the `specs/` and `skills/` directories with high precision.
2. **Git MCP:** Ensures every major change is staged and committed with the correct "Orchestrator" nomenclature.
3. **PostgreSQL MCP:** Allows the AI to verify schema migrations and inspect the `campaign_metadata` JSONB audit logs.

## Agent MCP Tools (Runtime Level)
These tools are exposed to the swarm for autonomous execution:
- **fetch_trends:** Proxied access to MoltBook/Social APIs.
- **validate_content:** The Judge's primary interface for safety checks.
- **agentkit_wallet:** Proxied interface for Coinbase AgentKit transactions.