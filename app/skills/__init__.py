"""app.skills package

Expose skill modules under `app.skills` for test discovery.
"""

from . import trend_analyzer

__all__ = ["trend_analyzer"]
