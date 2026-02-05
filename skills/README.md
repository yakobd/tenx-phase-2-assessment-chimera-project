# Skills — I/O Contracts and Implementation Guidance

This document defines the input/output contracts and Pydantic-compatible models for three critical skills used by Project Chimera's FastRender Hierarchical Swarm. All messages MUST be wrapped in MCP envelopes (`mcp_request` / `mcp_response`) for traceability and audit logs.

Goals:

- Provide strict, Pydantic-compatible schemas for skill inputs and outputs.
- Ensure outputs map cleanly to the PostgreSQL `campaigns` / `campaign_metadata` and `media_metadata` JSONB shapes and to the Judge `verdict` envelope.
- Enforce the governance rule: calibrated_confidence >= 0.85 for auto-publishes; the `skill_safety_judge` signs verdicts.

1. skill_trend_analyzer

- Purpose: fetch and score trending topics (MoltBook + ensemble signals) and produce trend objects aligning with the Campaign schema for Planner consumption.

Input (MCP envelope):

{
"mcp_request": {"request_id":"uuid","timestamp":"ISO8601","caller":{"agent_id":"uuid","role":"Planner"}},
"query": {"sources": ["moltbook"], "since":"ISO8601", "filters": {...}}
}

Output (MCP envelope):

{
"mcp_response": {"request_id":"uuid","timestamp":"ISO8601"},
"trends": [
{
"topic": "string",
"score": 0.0, -- relevance score (0..1)
"velocity": 0.0, -- change rate
"examples": [{"text":"..","source":"moltbook","ts":"ISO8601","ref_id":"weaviate-id"}],
"campaign_hint": {"recommended_objective":"string","budget_estimate":12345}
}
],
"ensemble_score": 0.0,
"confidence": 0.0
}

Pydantic model (example):

```python
from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import UUID

class TrendExample(BaseModel):
    text: str
    source: str
    ts: str
    ref_id: Optional[str]

class TrendItem(BaseModel):
    topic: str
    score: float
    velocity: float
    examples: List[TrendExample]
    campaign_hint: Optional[Dict[str, object]]

class FetchTrendsResponse(BaseModel):
    trends: List[TrendItem]
    ensemble_score: float
    confidence: float
```

Mapping notes:

- `campaign_hint` is optional metadata mapping directly into `campaigns.objective` and `campaigns.budget_bigint` when the Planner converts a trend into a signed PoI.

2. skill_video_assembler

- Purpose: assemble video artifacts from assets and produce `media_metadata` JSON matching PostgreSQL shape.

Input (MCP envelope):

{
"mcp_request": {"request_id":"uuid","timestamp":"ISO8601","caller":{"agent_id":"uuid","role":"Worker"}},
"assembly": {"campaign_id":"uuid","assets": [...], "spec": {"format":"mp4","resolution":"1080p"}, "metadata": {...}}
}

Output (MCP envelope):

{
"mcp_response": {"request_id":"uuid","timestamp":"ISO8601"},
"media_metadata": {
"id": "uuid",
"campaign_id": "uuid",
"worker_id": "uuid",
"uri": "s3://.../file.mp4",
"media_type": "video",
"size_bytes": 12345678,
"checksums": {"sha256":"..."},
"features": {"duration_s":120, "resolution":"1080p"},
"embedding_ref": "weaviate-id",
"created_at": "ISO8601"
}
}

Pydantic model (example):

```python
from pydantic import BaseModel
from typing import Dict, Optional

class MediaMetadata(BaseModel):
    id: UUID
    campaign_id: UUID
    worker_id: UUID
    uri: str
    media_type: str
    size_bytes: int
    checksums: Dict[str,str]
    features: Dict[str, object]
    embedding_ref: Optional[str]
    created_at: str
```

Mapping notes:

- `MediaMetadata` maps 1:1 to the `media_metadata` Postgres table's JSONB payload. The Worker must insert the returned object into the DB and persist the MCP envelopes into `campaign_metadata` for audit.

3. skill_safety_judge

- Purpose: validate artifacts and enforce governance. Must output a signed verdict and enforce `calibrated_confidence >= 0.85` for auto-publish decisions.

Input (MCP envelope):

{
"mcp_request": {"request_id":"uuid","timestamp":"ISO8601","caller":{"agent_id":"uuid","role":"Worker"}},
"artifact": {"id":"uuid","campaign_id":"uuid","type":"video","text":"...","media_refs": [...]},
"checks": ["toxicity","copyright","factuality","reputation"],
"policy_version": "v1"
}

Output (MCP envelope):

{
"mcp_response": {"request_id":"uuid","timestamp":"ISO8601"},
"verdict": "pass|fail|needs_review",
"checks": {"toxicity": {"score":0.12, "pass":true}, ...},
"confidence": 0.92, -- calibrated confidence used for governance
"signed_by": "judge_agent_id",
"signature": {"algorithm":"ed25519","public_key_ref":"did:key:...","signature_blob":"base64"},
"audit": {"mcp_request_id":"uuid","policy_version":"v1"}
}

Pydantic model (example):

```python
from pydantic import BaseModel
from typing import Dict, Any

class CheckResult(BaseModel):
    score: float
    passed: bool
    explain: Optional[str]

class ValidateContentResponse(BaseModel):
    verdict: str
    checks: Dict[str, Any]
    confidence: float
    signed_by: str
    signature: Dict[str,str]
    audit: Dict[str,Any]

    def is_autopublish_allowed(self) -> bool:
        return self.verdict == 'pass' and self.confidence >= 0.85
```

Signature & enforcement rules:

- `skill_safety_judge` MUST compute and return a calibrated `confidence` score. Implementers must maintain calibration logs and model versions in `campaign_metadata`.
- If `validate_content` returns `verdict == 'pass'` but `confidence < 0.85`, the response MUST set `verdict` to `needs_review` or explicitly flag `autopublish_allowed: false` in `audit`.
- The `signature` object must sign the serialized `verdict`+`checks`+`confidence` payload using Ed25519 and include the public key reference and `key_version`.

Audit & MCP requirements

- All skill inputs and outputs are transported inside `mcp_request`/`mcp_response` envelopes. Implementations MUST persist these envelopes in `campaign_metadata` with appropriate `envelope_type` (e.g., `intent`, `validate_response`, `media_metadata`).
- Maintain versioning: every skill output must include `model_version` and `policy_version` in `diagnostics` or `audit` to facilitate reproducibility.

Testing guidance

- Unit test each skill to validate Pydantic serialization/deserialization, proper MCP envelope wrapping/unwrapping, and DB persistence hooks.
- Integration tests: mock MCP endpoints for Judge and Weaviate to validate end-to-end flows: fetch_trends -> create PoI -> worker produces media -> judge validates -> (autopublish or needs_review).

Appendix: Example MCP wrapper (pseudo)

```python
def wrap_mcp_request(caller_id: str, role: str, payload: dict) -> dict:
    return {
        "mcp_request": {"request_id": str(uuid.uuid4()), "timestamp": now_iso(), "caller": {"agent_id": caller_id, "role": role}},
        **payload
    }
```

---

This file is the authoritative developer-facing contract for skill implementers. For code generation from these models (Pydantic classes + FastAPI endpoints), ask me to scaffold endpoints and tests.
