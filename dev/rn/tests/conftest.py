"""What every level of rn's cases shares: the folder of rn's code on the import path, as template.py
puts `domain/` there, the top of the repository, and this folder, where rn's bench and helpers lie,
as the type checker finds each there."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DOMAIN = os.path.join(TOP, "plugins", "rn", "domain")
for folder in (DOMAIN, TOP, HERE):
    if folder not in sys.path:
        sys.path.insert(0, folder)
