import pytest
from app.skills.safety_judge import validate_content

def test_safety_judge_parameters():
    """Test that validate_content handles dict input and returns 'verdict' and 'confidence' fields per technical.md."""
    # Minimal valid artifact dict (add required fields as per technical.md)
    mock_artifact = {
        "id": "123",
        "campaign_id": "c1",
        "type": "video",
        "text": "Hello world",
        "media_refs": ["s3://bucket/video.mp4"],
        "render_meta": {"template": "v1", "worker_id": "w1"}
    }
    # The skill should accept a dict and return a dict with 'verdict' and 'confidence'
    result = validate_content(mock_artifact)

    assert isinstance(result, dict), "validate_content should return a dict"
    assert "verdict" in result, "Missing 'verdict' in result"
    assert result["verdict"] in ["pass", "fail", "needs_review"], "Invalid verdict value"
    assert "confidence" in result, "Missing 'confidence' in result"
    assert isinstance(result["confidence"], float), "Confidence should be a float"