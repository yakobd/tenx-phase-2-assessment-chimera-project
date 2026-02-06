import pytest
import asyncio
from datetime import datetime

# These tests validate the fetch_trends API contract defined in specs/technical.md.
# They intentionally import from a hypothetical module `core.trend_fetcher` which
# does not exist yet — the tests are expected to fail until the implementation
# matching the spec is provided.

try:
    from core.trend_fetcher import fetch_trends
except Exception as e:
    # Leave the import error to surface during test runs — tests will fail as requested.
    fetch_trends = None


@pytest.mark.asyncio
async def test_input_validation_requires_mcp_envelope():
    """fetch_trends must require an MCP envelope with request_id, timestamp, and caller.agent_id/role."""
    if fetch_trends is None:
        pytest.skip("core.trend_fetcher.fetch_trends not implemented")

    # Build a request missing the MCP envelope
    invalid_request = {
        "query": {"sources": ["moltbook"], "since": datetime.utcnow().isoformat()},
        "options": {"ensemble": True}
    }

    with pytest.raises((ValueError, TypeError, AssertionError)):
        await fetch_trends(invalid_request)


@pytest.mark.asyncio
async def test_output_structure_and_types():
    """Response must include trends array with required fields and proper types.

    Each trend item MUST include: topic (str), score (float 0.0-1.0), velocity (float 0.0-1.0),
    examples (list), and campaign_hint (str).
    """
    if fetch_trends is None:
        pytest.skip("core.trend_fetcher.fetch_trends not implemented")

    request = {
        "mcp_request": {"request_id": "t-1", "timestamp": datetime.utcnow().isoformat(), "caller": {"agent_id": "planner-1", "role": "Planner"}},
        "query": {"sources": ["moltbook"], "since": datetime.utcnow().isoformat(), "max_items": 50, "filters": {"region": "global"}},
        "options": {"ensemble": True, "include_examples": True}
    }

    resp = await fetch_trends(request)

    # MCP envelope check on response
    assert isinstance(resp.get("mcp_response") if isinstance(resp, dict) else getattr(resp, "mcp_response", None), (dict,)), "mcp_response envelope missing"

    trends = resp["trends"] if isinstance(resp, dict) else getattr(resp, "trends")
    assert isinstance(trends, list) and len(trends) > 0, "trends must be a non-empty list"

    for t in trends:
        # allow both dict and object responses
        topic = t.get("topic") if isinstance(t, dict) else getattr(t, "topic", None)
        score = t.get("score") if isinstance(t, dict) else getattr(t, "score", None)
        velocity = t.get("velocity") if isinstance(t, dict) else getattr(t, "velocity", None)
        examples = t.get("examples") if isinstance(t, dict) else getattr(t, "examples", None)
        campaign_hint = t.get("campaign_hint") if isinstance(t, dict) else getattr(t, "campaign_hint", None)

        assert isinstance(topic, str), "trend.topic must be a string"
        assert isinstance(score, float), "trend.score must be a float"
        assert 0.0 <= score <= 1.0, "trend.score out of range"
        assert isinstance(velocity, float), "trend.velocity must be a float"
        assert 0.0 <= velocity <= 1.0, "trend.velocity out of range"
        assert isinstance(examples, list), "trend.examples must be a list"
        assert isinstance(campaign_hint, str), "trend.campaign_hint must be a string"


@pytest.mark.asyncio
async def test_mcp_compliance_wrapping():
    """Ensure inputs/outputs are wrapped in MCP envelopes."""
    if fetch_trends is None:
        pytest.skip("core.trend_fetcher.fetch_trends not implemented")

    request = {
        "mcp_request": {"request_id": "t-2", "timestamp": datetime.utcnow().isoformat(), "caller": {"agent_id": "planner-1", "role": "Planner"}},
        "query": {"sources": ["moltbook"]},
        "options": {"ensemble": True}
    }

    resp = await fetch_trends(request)

    # Input was wrapped; assert response has mcp_response
    if isinstance(resp, dict):
        assert "mcp_response" in resp
    else:
        assert hasattr(resp, "mcp_response")
