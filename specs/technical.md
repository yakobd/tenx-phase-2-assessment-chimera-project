# Project Chimera — Technical Specifications

## Persistence Layer (PostgreSQL)

This layer stores canonical campaign state, metadata, financial transactions, and tamper-evident audit envelopes. The design follows the Domain Architecture: normalized core entities (Campaigns, Transactions) with append-only `campaign_metadata` for intents, ACKs, and audit traces.

-- Campaigns
CREATE TABLE campaigns (
id UUID PRIMARY KEY,
name TEXT NOT NULL,
planner_id UUID NOT NULL,
objective TEXT,
start_at TIMESTAMPTZ,
end_at TIMESTAMPTZ,
status TEXT CHECK (status IN ('draft','active','paused','archived')),
budget_bigint BIGINT,
created_at TIMESTAMPTZ DEFAULT now(),
updated_at TIMESTAMPTZ DEFAULT now()
);

-- Campaign Metadata (append-only envelopes: PoI, ACKs, audit entries)
CREATE TABLE campaign_metadata (
id UUID PRIMARY KEY,
campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
envelope_type TEXT NOT NULL, -- e.g. intent|ack|audit|model_snapshot
envelope JSONB NOT NULL, -- canonical PoI, ACK, or audit payload
signature JSONB, -- {algorithm, public_key_ref, signature_blob, key_version}
created_at TIMESTAMPTZ DEFAULT now()
);

-- Transactions (AgentKit-backed)
CREATE TABLE transactions (
id UUID PRIMARY KEY,
campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
agent_id UUID, -- initiating agent
wallet_address TEXT,
amount_bigint BIGINT,
currency TEXT,
tx_type TEXT, -- payout, ad_spend, refund, etc.
status TEXT, -- pending, settled, failed
agentkit_payload JSONB, -- raw AgentKit transaction envelope
mcp_request_id UUID, -- link to MCP event/request
audit_json JSONB, -- signed receipts, validation notes
external_tx_ref TEXT, -- external blockchain/rail reference
created_at TIMESTAMPTZ DEFAULT now(),
settled_at TIMESTAMPTZ
);

Notes:

- Use `UUID` for primary keys and references; use `JSONB` for flexible payloads and audit envelopes.
- Treat `campaign_metadata` as append-only: insert new metadata rows for each PoI, ACK, or audit event instead of mutating previous entries.
- Persist cryptographic receipts (ACKs, signed verdicts) in `campaign_metadata.envelope` and store signature details in `signature`.

## Vector Store (Weaviate) — Semantic Memory

Weaviate stores embeddings and enables semantic search for content recall, trend-context retrieval, and similarity lookups. Use a class to capture canonicalized text/snippets, exemplars, and policy rationale with metadata for provenance.

Example Weaviate Class (JSON):
{
"class": "SemanticMemory",
"vectorizer": "text2vec-transformers",
"moduleConfig": {"text2vec-transformers": {"pooling": "mean"}},
"properties": [
{"name": "text", "dataType": ["text"]},
{"name": "campaignRef", "dataType": ["string"]},
{"name": "agentRef", "dataType": ["string"]},
{"name": "tags", "dataType": ["string[]"]},
{"name": "policy_ref", "dataType": ["string"]},
{"name": "timestamp", "dataType": ["date"]}
]
}

Usage notes:

- Store canonical content snippets, trend exemplars, and policy rationales in `SemanticMemory` with vector embeddings.
- Persist Weaviate object IDs back into PostgreSQL rows (e.g., `campaign_metadata.envelope.ref_id`) to maintain referential links between relational records and semantic objects.

## API Contracts (MCP-standard JSON schemas)

All tool APIs MUST use an `mcp_request`/`mcp_response` envelope. Implementations should provide strict Pydantic models matching these schemas.

fetch_trends (MoltBook + ensemble) — Request (Input):
{
"mcp_request": {
"request_id": "uuid",
"timestamp": "ISO8601",
"caller": {"agent_id": "uuid", "role": "Planner"}
},
"query": {
"sources": ["moltbook", "social_api"],
"since": "ISO8601",
"max_items": 200,
"filters": {"region": "global", "language": "en"}
},
"options": {"ensemble": true, "include_examples": true, "use_semantic_memory": true}
}

Response (Output):
{
"mcp_response": {"request_id": "uuid", "timestamp": "ISO8601"},
"trends": [
{
"topic": "string",
"score": 0.0,
"velocity": 0.0,
"examples": [{"text":"...","source":"moltbook","ts":"ISO8601", "ref_id": "weaviate-id"}],
"metadata": {"tags": ["tag1","tag2"]}
}
],
"ensemble_score": 0.0,
"confidence": 0.0,
"diagnostics": {"sources_used": ["moltbook"], "model_versions": {}}
}

validate_content — Request (Input):
{
"mcp_request": {"request_id": "uuid", "timestamp": "ISO8601", "caller": {"agent_id": "uuid", "role": "Worker"}},
"artifact": {
"id": "uuid",
"campaign_id": "uuid",
"type": "video|image|text",
"text": "string",
"media_refs": ["media-id-uuid"],
"render_meta": {"template":"v1","worker_id":"uuid"}
},
"checks": ["toxicity","copyright","factuality","reputation"],
"policy_version": "string"
}

Response (Output):
{
"mcp_response": {"request_id": "uuid", "timestamp": "ISO8601"},
"verdict": "pass|fail|needs_review",
"checks": {
"toxicity": {"score": 0.12, "pass": true, "explain": "OK"},
"copyright": {"matches": [], "pass": true}
},
"confidence": 0.92, -- calibrated confidence used for governance
"explainability": {"highlights": [{"span": [10, 45], "reason": "factuality_issue"}]},
"signed_by": "judge_agent_id",
"audit": {"mcp_request_id": "uuid", "policy_version": "v1"}
}

Schema Notes:

- The `mcp_request` / `mcp_response` envelope is mandatory for all tool interactions to ensure traceability.
- Use Pydantic models for request/response validation and automatic API docs generation in FastAPI.

## Tech Stack

- Python 3.12
- FastAPI (HTTP MCP adapters / service endpoints)
- PostgreSQL (primary relational store)
- Weaviate (vector DB for embeddings and semantic search)
- AsyncPG / SQLAlchemy Core for DB access
- AgentKit for transactional/agentic payment workflows
- MCP (Model-Context-Proxy) for all external tool/service access
- Uvicorn / Gunicorn for ASGI hosting

## Operational Notes

- All external calls (trend sources, payment rails, vector DB writes) must be proxied through MCP with audit envelopes.
- Store audit and governance events in JSONB fields to enable tamper-evident append-only logs (consider signing envelopes and storing receipts).
- Maintain a mapping between PostgreSQL entities and Weaviate object IDs via `embedding_ref` or `semantic_ref` fields to facilitate joins.
