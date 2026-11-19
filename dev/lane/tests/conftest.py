"""What every level of Lane's cases shares: the folder of Lane's guard on the import path, as
hooks/hooks.json runs guard.py from there, the folder of Lane's route adapter, the folder of the
double of Claude Code and the helpers that both plugins' tests share, and this folder, where Lane's
bench lies, as the type checker finds each there."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GUARD = os.path.join(TOP, "plugins", "lane", "hooks", "lane")
ROUTE_ADAPTER = os.path.join(TOP, "plugins", "lane", "adapters")
for folder in (GUARD, ROUTE_ADAPTER, os.path.join(TOP, "dev", "tests"), HERE):
    if folder not in sys.path:
        sys.path.insert(0, folder)
