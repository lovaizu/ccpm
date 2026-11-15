"""What every level of rn's cases shares: the folder of rn's code on the import path, as template.py
puts `domain/` there, and the top of the repository, from which the cases take their helpers, the
double of Claude Code, and the code that both plugins' tests share by their paths, as the type
checker finds them there."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DOMAIN = os.path.join(TOP, "plugins", "rn", "domain")
for folder in (DOMAIN, TOP):
    if folder not in sys.path:
        sys.path.insert(0, folder)
