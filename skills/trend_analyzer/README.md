# Skill: trend_analyzer

- **Owner:** Planner / Sensing Team
- **Purpose:** Fetch and aggregate trending topics from MoltBook and other social sources, returning scored trend candidates for campaign planning.

## JSON Input (example)

```json
{
  "mcp_request": {
    "request_id": "00000000-0000-0000-0000-000000000001",
    "timestamp": "2026-02-06T12:00:00Z",
    "caller": { "agent_id": "planner-uuid", "role": "Planner" }
  },
  "query": {
    "sources": ["moltbook", "social_api"],
    "since": "2026-02-01T00:00:00Z",
    "max_items": 200,
    "filters": { "region": "global", "language": "en" }
  },
  "options": {
    "ensemble": true,
    "include_examples": true,
    "use_semantic_memory": true
  }
}
```

## JSON Output (example)

```json
{
  "mcp_response": {
    "request_id": "00000000-0000-0000-0000-000000000001",
    "timestamp": "2026-02-06T12:00:05Z"
  },
  "trends": [
    {
      "topic": "lofi_beats",
      "score": 0.82,
      "velocity": 0.12,
      "examples": [
        {
          "text": "...",
          "source": "moltbook",
          "ts": "2026-02-05T10:00:00Z",
          "ref_id": "weaviate-123"
        }
      ],
      "metadata": { "tags": ["music", "vibes"] }
    }
  ],
  "ensemble_score": 0.78,
  "confidence": 0.88,
  "diagnostics": {
    "sources_used": ["moltbook", "social_api"],
    "model_versions": { "trend_model": "v1.2" }
  }
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

class TrendExample(BaseModel):
    text: str
    source: str
    ts: datetime
    ref_id: Optional[str]

class Trend(BaseModel):
    topic: str
    score: float
    velocity: float
    examples: List[TrendExample]
    metadata: Dict[str, List[str]]

class FetchTrendsRequest(BaseModel):
    mcp_request: MCPRequest
    query: Dict[str, Optional[object]]
    options: Dict[str, bool]

class FetchTrendsResponse(BaseModel):
    mcp_response: Dict[str, str]
    trends: List[Trend]
    ensemble_score: float
    confidence: float
    diagnostics: Dict[str, object]
```

## Notes (MCP & Database)

- This skill MUST be invoked via an MCP envelope (`mcp_request`). All responses should return an `mcp_response` envelope for traceability.
- Persist selected trend candidates and the full response diagnostics into `campaign_metadata` as an append-only audit envelope when the Planner converts trends into a PoI.
- When `use_semantic_memory` is enabled, store exemplar text objects into Weaviate and save the returned object IDs in the diagnostics and/or `campaign_metadata` for provenance.
