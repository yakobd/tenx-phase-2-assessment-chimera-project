# Skill: safety_judge

- **Owner:** Judge / Safety Team
- **Purpose:** Validate artifacts for toxicity, copyright, factuality, and reputation; issue signed verdicts with calibrated confidence for governance decisions.

## JSON Input (example)

```json
{
  "mcp_request": {
    "request_id": "00000000-0000-0000-0000-000000000100",
    "timestamp": "2026-02-06T12:30:00Z",
    "caller": {"agent_id": "judge-uuid", "role": "Judge"}
  },
  "artifact": {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "campaign_id": "22222222-2222-2222-2222-222222222222",
    "type": "video",
    "text": "transcript or caption text...",
    "media_refs": ["s3://bucket/rendered/video.mp4"],
    "render_meta": {"template":"v1","worker_id":"worker-uuid"}
  },
  "checks": ["toxicity","copyright","factuality","reputation"],
  "policy_version": "v1"
}
```

## JSON Output (example)

```json
{
  "mcp_response": {"request_id":"00000000-0000-0000-0000-000000000100","timestamp":"2026-02-06T12:30:15Z"},
  "verdict": "pass",
  "checks": {
    "toxicity": {"score": 0.12, "pass": true, "explain": "OK"},
    "copyright": {"matches": [], "pass": true}
  },
  "confidence": 0.92,
  "explainability": {"highlights": [{"span": [10, 45], "reason": "context_issue"}]},
  "signed_by": "judge-uuid",
  "signature": {"algorithm":"ed25519","public_key_ref":"did:key:...","signature_blob":"base64"},
  "audit": {"mcp_request_id":"00000000-0000-0000-0000-000000000100","policy_version":"v1"}
}
```

## Pydantic Models (Python)

```python
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

class MCPRequest(BaseModel):
    request_id: str
    timestamp: datetime
    caller: Dict[str, str]

class Artifact(BaseModel):
    id: str
    campaign_id: str
    type: str
    text: Optional[str]
    media_refs: List[str]
    render_meta: Optional[Dict[str, str]]

class CheckResult(BaseModel):
    score: Optional[float]
    pass_: bool
    explain: Optional[str]

class ValidateContentRequest(BaseModel):
    mcp_request: MCPRequest
    artifact: Artifact
    checks: List[str]
    policy_version: str

class ValidateContentResponse(BaseModel):
    mcp_response: Dict[str, str]
    verdict: str
    checks: Dict[str, object]
    confidence: float
    explainability: Optional[Dict[str, object]]
    signed_by: Optional[str]
    signature: Optional[Dict[str, str]]
    audit: Optional[Dict[str, str]]
```

## Notes (MCP & Database)

- The Judge MUST wrap verdicts in an `mcp_response` envelope and persist the signed verdict and supporting `checks` into `campaign_metadata` as an append-only audit entry.
- Implement signature generation (e.g., Ed25519) and store signature metadata in the `signature` field or the `campaign_metadata.envelope` for forensic validation.
- Enforce the governance rule: artifacts may only be auto-published when `confidence >= 0.85` and `verdict == "pass"` (in combination with ensemble scores stored elsewhere). If `confidence < 0.85` or `verdict == "needs_review"`, mark artifact `needs_review` and escalate to Planner/HITL.
