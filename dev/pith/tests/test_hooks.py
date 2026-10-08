"""pith's hooks, by the tests every plugin's copy of the hook scripts must pass."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))

from hooks_suite import suite  # noqa: E402

CheckIn, Facts = suite("pith")
