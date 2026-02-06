import pytest
from app.skills.trend_analyzer import fetch_trends

def test_trend_data_contract():
    """Test that fetch_trends returns trends with required fields per specs/technical.md."""
    mock_request = {"sources": ["twitter"], "max_items": 5}
    result = fetch_trends(mock_request)

    assert "trends" in result, "Response missing 'trends' key"
    assert len(result["trends"]) > 0, "Trends list is empty"

    for trend in result["trends"]:
        assert "topic" in trend, "Trend missing 'topic' field"
        assert "score" in trend, "Trend missing 'score' field"
        # Each trend should have an 'examples' array with at least one item containing 'ts' (timestamp)
        assert "examples" in trend and isinstance(trend["examples"], list) and len(trend["examples"]) > 0, "Trend missing 'examples' array"
        for ex in trend["examples"]:
            assert "ts" in ex, "Example missing 'ts' (timestamp) field"