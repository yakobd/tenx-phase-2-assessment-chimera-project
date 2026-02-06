def fetch_trends(request_data: dict):
    """
    Returns a mock trend structure to satisfy the TDD contract.
    """
    return {
        "trends": [
            {
                "topic": "AI Governance",
                "score": 0.92,
                "examples": [
                    {"ts": "2026-02-06T12:00:00Z"}
                ]
            },
            {
                "topic": "Decentralized Finance",
                "score": 0.87,
                "examples": [
                    {"ts": "2026-02-06T11:30:00Z"}
                ]
            },
        ]
    }