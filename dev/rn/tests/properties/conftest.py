"""The fixtures of rn's property-based tests: the builders of the unit cases on the import path."""

from __future__ import annotations

import os
import sys

sys.path[:0] = [
    folder
    for folder in [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "unit")
    ]
    if folder not in sys.path
]
