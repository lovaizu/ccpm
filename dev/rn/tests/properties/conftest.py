"""What rn's property-based tests share: no deadline, as a property that writes a run's files takes
longer on a busy machine."""

from __future__ import annotations

from hypothesis import settings

settings.register_profile("rn", deadline=None)
settings.load_profile("rn")
