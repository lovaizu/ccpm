"""What lane's tests stand on beside what every plugin's tests do: lane's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first."""

from __future__ import annotations

import os
import sys

LANE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "lane")
)
CODE = os.path.join(LANE, "hooks", "lane")
DOMAIN = os.path.join(CODE, "core", "domain")
sys.path[:0] = [DOMAIN, os.path.join(LANE, "..", "..", "dev", "lane")]

import forms  # noqa: F401
import ports  # noqa: F401
import schema  # noqa: F401
import template  # noqa: F401
import testing  # noqa: F401
