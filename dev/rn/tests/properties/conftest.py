"""What rn's property-based tests share: the profiles of hypothesis that quality.sh names by
HYPOTHESIS_PROFILE, `push` with few inputs on each push and `night` with the most each night, and
`push` where none is named, as a developer runs them by hand. Each input writes a run's folder on
disk, so no input has a deadline."""

from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

settings.register_profile(
    "push", max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow]
)
settings.register_profile(
    "night", max_examples=500, deadline=None, suppress_health_check=[HealthCheck.too_slow]
)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "push"))
