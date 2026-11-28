"""What every level of overnight's cases shares: the folder of overnight's code on the import path,
as its command puts `scripts/` there, and this folder, where the double of `claude` lies, as the
type checker finds each there."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SCRIPTS = os.path.join(TOP, "plugins", "overnight", "scripts")
for folder in (SCRIPTS, HERE):
    if folder not in sys.path:
        sys.path.insert(0, folder)
