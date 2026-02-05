# OpenClaw Integration — Proof-of-Intent & Availability Heartbeats

This document defines how Project Chimera participates in the OpenClaw network using a Proof‑of‑Intent (PoI) handshake to broadcast node status and intent. All network interactions MUST flow through MCP for auditability and governance.

## Proof‑of‑Intent (PoI) Handshake

Purpose: enable a tamper‑evident, verifiable mechanism for Chimera nodes to announce intent (campaign or campaign action) and current availability to the OpenClaw mesh.

High‑level flow:

1. Intent Creation: The Planner composes an `intent` object describing planned campaign action (e.g., scheduled publish, A/B experiment). The intent is assigned a stable `intent_id` (UUID) and canonicalized JSON.
2. Intent Signing: The Planner signs the canonicalized intent using the node's keypair (Ed25519 recommended). The signature is stored as `intent_signature` in the PoI envelope.
3. PoI Broadcast: The node wraps the signed intent in an MCP envelope and broadcasts a `poi/announce` event to OpenClaw via MCP. The envelope includes tamper‑evident metadata (timestamp, seq_no, policy_version).
4. OpenClaw Receipt & ACK: OpenClaw validators verify the signature, the Planner's authority (reputation), and intent schema, returning a signed ACK containing `ack_id`, `received_at`, and optional `validation_notes`.
5. Availability Heartbeat: Independently (and frequently), the node emits `availability/heartbeat` messages to indicate live status, current load, and active intent references (see JSON schema below).

Security & governance rules:

- All PoI and heartbeat messages MUST include an `mcp_request` envelope for traceability.
- Signatures MUST use an approved algorithm (Ed25519) and include the public key reference and key version.
- OpenClaw validators MUST record ACKs and provide a signed receipt; receipts are stored in local audit logs and in the `audit` JSONB fields of relevant DB records.
- Any change to an existing `intent` must be published as a new signed intent with a new `intent_version` and linked to the original `intent_id`.

## Availability Heartbeat JSON Structure

Top-level envelope (MCP):

{
"mcp_request": {"request_id": "uuid", "timestamp": "ISO8601", "caller": {"agent_id": "uuid", "role": "Worker|Planner"}},
"heartbeat": {
"node_id": "uuid",
"role": "Planner|Worker|Judge|CFO",
"status": "online|idle|busy|maintenance|offline",
"seq_no": 12345,
"timestamp": "ISO8601",
"uptime_seconds": 86400,
"load": {"cpu": 0.12, "mem": 0.43, "pending_jobs": 7},
"active_intents": [
{"intent_id": "uuid", "intent_hash": "sha256-hex", "intent_version": 2, "role": "Planner"}
],
"campaign_refs": ["campaign-uuid-1","campaign-uuid-2"],
"policy_version": "string",
"mcp_connection": {"latency_ms": 30, "mcp_endpoint": "https://mcp.example"},
"metadata": {"region": "us-east-1", "zone": "a"}
},
"signature": {
"algorithm": "ed25519",
"public_key_ref": "did:key:...",
"signature_blob": "base64",
"key_version": "v1"
}
}

Field notes:

- `seq_no`: monotonic sequence number per node to detect dropped or out‑of‑order heartbeats.
- `intent_hash`: canonical SHA‑256 hash of the canonicalized intent JSON for fast verification and diffing.
- `signature.signature_blob`: covers the serialized `heartbeat` object (not the `mcp_request`), enabling OpenClaw validators to verify the node's liveness claim.
- `mcp_request`/`mcp_response` envelopes MUST be recorded in audit logs and linked to Campaign/Transaction records as appropriate.

## Heartbeat Frequency & TTL

- Default frequency: 30s for `online` nodes; configurable per deployment.
- TTL: heartbeats older than 3×frequency are considered stale; OpenClaw validators should mark nodes as `unknown` after TTL expiration.

## ACK / Receipt Structure (OpenClaw Validator Response)

{
"mcp_response": {"request_id": "uuid", "timestamp": "ISO8601"},
"ack": {
"ack_id": "uuid",
"intent_id": "uuid|null",
"node_id": "uuid",
"received_at": "ISO8601",
"status": "accepted|rejected|needs_review",
"validation_notes": ["string"]
},
"validator_signature": {"algorithm":"ed25519","signature_blob":"base64","validator_id":"did:oc:..."}
}

## Operational Recommendations

- Use MCP to multiplex PoI and heartbeat traffic; avoid direct sockets to OpenClaw from individual Workers.
- Implement local replay protection by tracking `seq_no` and rejecting older heartbeats.
- Persist signed heartbeats and ACK receipts in the `audit` JSONB fields for future forensic analysis.
- Expose a local health endpoint that returns last heartbeat status and last ACK to simplify debugging.

## Example (Minimal heartbeat)

{
"mcp_request": {"request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "timestamp": "2026-02-05T12:00:00Z", "caller": {"agent_id": "7b9e2b8a-...", "role": "Worker"}},
"heartbeat": {"node_id": "7b9e2b8a-...", "role": "Worker", "status": "online", "seq_no": 1024, "timestamp": "2026-02-05T12:00:00Z", "uptime_seconds": 3600, "load": {"cpu": 0.08, "mem": 0.33, "pending_jobs": 2}, "active_intents": [], "policy_version": "v1"},
"signature": {"algorithm": "ed25519", "public_key_ref": "did:key:z6Mk...", "signature_blob": "MEUCIQD...", "key_version": "v1"}
}

---

Store this spec in `specs/openclaw_integration.md` and ensure implementations conform to the MCP envelope and signature rules. Would you like Pydantic models or example MCP adapters for these messages?
