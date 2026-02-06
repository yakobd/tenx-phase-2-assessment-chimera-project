import pytest
from datetime import datetime, UTC
timestamp = datetime.now(UTC)
from pydantic import ValidationError
try:
    from app.skills.safety_judge import validate_content, ValidateContentRequest, MCPRequest, Artifact
except ImportError:
    validate_content = None


def test_safety_judge_interface_parameters():
    """Asserts that the safety_judge skill accepts the correct parameters and returns a proper response."""
    if validate_content is None:
        pytest.fail("Safety judge module not found - Implementation Missing")

    # Build a valid request matching the spec
    req = ValidateContentRequest(
        mcp_request=MCPRequest(request_id="jc-1", timestamp=datetime.utcnow(), caller={"agent_id":"tester","role":"Judge"}),
        artifact=Artifact(id="a1", campaign_id="c1", type="video", text="hello", media_refs=["s3://b/r.mp4"], render_meta={}),
        checks=["toxicity", "copyright"],
        policy_version="v1"
    )

    resp = validate_content(req)
    assert resp.confidence >= 0.85
    assert resp.verdict in ("pass", "fail", "needs_review")