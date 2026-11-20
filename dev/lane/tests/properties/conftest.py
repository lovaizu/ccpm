"""What Lane's property-based tests share: the profiles that dev/scripts/quality.sh names in
HYPOTHESIS_PROFILE, `push` on each push and `night` over the whole each night, at its most inputs,
with no deadline, as the guard run through the double of Claude Code takes longer on a busy
machine."""

from __future__ import annotations

import os

from hypothesis import settings

settings.register_profile("push", max_examples=100, deadline=None)
settings.register_profile("night", max_examples=1000, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "push"))
