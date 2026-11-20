"""What Lane's property-based tests share: no deadline, as the guard run through the double of
Claude Code takes longer on a busy machine."""

from __future__ import annotations

from hypothesis import settings

settings.register_profile("lane", deadline=None)
settings.load_profile("lane")
