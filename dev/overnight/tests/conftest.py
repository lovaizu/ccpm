"""What every level of overnight's cases shares: the folder of overnight's code on the import path,
as its scripts put `domain/` there, and this folder, where the stand-in of Claude Code and the
helpers lie, as the type checker finds each there."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DOMAIN = os.path.join(TOP, "plugins", "overnight", "domain")
for folder in (DOMAIN, HERE):
    if folder not in sys.path:
        sys.path.insert(0, folder)
