# Skill: video_assembler

- **Owner:** Worker / Rendering Team
- **Purpose:** Assemble and render video artifacts from provided assets and rendering specs, producing media URIs and metadata for downstream validation and publishing.

## JSON Input (example)

```json
{
  "mcp_request": {
    "request_id": "00000000-0000-0000-0000-000000000010",
    "timestamp": "2026-02-06T12:15:00Z",
    "caller": { "agent_id": "worker-uuid", "role": "Worker" }
  },
  "task": {
    "task_id": "11111111-1111-1111-1111-111111111111",
    "campaign_id": "22222222-2222-2222-2222-222222222222",
    "spec": { "format": "mp4", "resolution": "1080p", "duration_s": 60 },
    "assets": [{ "type": "video", "ref_id": "s3://bucket/source.mp4" }],
    "deadline": "2026-02-06T13:00:00Z"
  }
}
```

## JSON Output (example)

```json
{
  "mcp_response": {
    "request_id": "00000000-0000-0000-0000-000000000010",
    "timestamp": "2026-02-06T12:20:00Z"
  },
  "result": {
    "artifact_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "task_id": "11111111-1111-1111-1111-111111111111",
    "campaign_id": "22222222-2222-2222-2222-222222222222",
    "media_metadata": {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "uri": "s3://bucket/rendered/video.mp4",
      "media_type": "video",
      "size_bytes": 12345678,
      "checksums": { "sha256": "deadbeef..." },
      "features": { "duration_s": 60, "resolution": "1080p" },
      "embedding_ref": "weaviate-asset-456"
    },
    "render_telemetry": {
      "worker_version": "v1",
      "model_versions": { "editor": "v3" }
    },
    "semantic_refs": ["weaviate-asset-456"]
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

class Asset(BaseModel):
    type: str
    ref_id: str

class TaskSpec(BaseModel):
    format: str
    resolution: str
    duration_s: int

class TaskMessage(BaseModel):
    mcp_request: MCPRequest
    task_id: str
    campaign_id: str
    spec: TaskSpec
    assets: List[Asset]
    deadline: Optional[datetime]

class MediaMetadata(BaseModel):
    id: str
    uri: str
    media_type: str
    size_bytes: int
    checksums: Dict[str, str]
    features: Dict[str, object]
    embedding_ref: Optional[str]

class WorkerResult(BaseModel):
    mcp_response: Dict[str, str]
    result: Dict[str, object]
```

## Notes (MCP & Database)

- The `video_assembler` should write `content_assets` rows for each produced artifact (link `campaign_id`, `worker_id`, `uri`, `features`, `embedding_ref`).
- Audit the render operation by inserting an append-only `campaign_metadata` envelope containing the `task` and resulting `media_metadata` (signed or timestamped) for traceability.
- All invocations and responses must be proxied via MCP envelopes to ensure traceability and to enable replay/testing by the Planner and Judge.
