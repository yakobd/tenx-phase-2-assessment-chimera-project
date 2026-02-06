import pytest
import asyncio
from datetime import datetime
from app.skills.trend_analyzer import fetch_trends, FetchTrendsRequest, MCPRequest, Query, Options

@pytest.mark.asyncio # Needed because your new function is 'async'
async def test_trend_data_contract():
    """
    Asserts that the trend data structure matches the API contract.
    """
    # 1. Arrange: Create the complex request object your code now requires
    mock_request = FetchTrendsRequest(
        mcp_request=MCPRequest(
            request_id="test-123",
            timestamp=datetime.utcnow(),
            caller={"agent_id": "tester", "role": "Planner"}
        ),
        query=Query(sources=["moltbook"], since=datetime.utcnow(), max_items=100, filters={"region": "global"}),
        options=Options(ensemble=True, include_examples=True, use_semantic_memory=False)
    )
    
    # 2. Act: Call the async function
    response = await fetch_trends(request=mock_request)
    
    # 3. Assert: Check if it meets our 0.85 Governance Threshold
    assert response.confidence >= 0.85
    assert len(response.trends) > 0
    assert response.trends[0].topic == "sample_topic"
    # Ensure MCP envelope propagated
    assert response.mcp_response.request_id == "test-123"