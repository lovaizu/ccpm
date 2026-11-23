"""What overnight's property-based tests share: no deadline, as a property that writes a queue's
files or runs its tasks through the doubles takes longer on a busy machine. The generators lie in
`overnight_generators.py` beside this file."""

from __future__ import annotations

from hypothesis import settings

settings.register_profile("overnight", deadline=None)
settings.load_profile("overnight")
