"""The fixtures of Lane's property-based tests: the unit cases' builders on the import path."""

from __future__ import annotations

import os
import sys

UNIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "unit")
if UNIT not in sys.path:
    sys.path.insert(0, UNIT)
