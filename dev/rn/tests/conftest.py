"""What every level of rn's cases shares: the folder of rn's code on the import path, as record.py
puts `domain/` there."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DOMAIN = os.path.join(TOP, "plugins", "rn", "domain")
if DOMAIN not in sys.path:
    sys.path.insert(0, DOMAIN)
