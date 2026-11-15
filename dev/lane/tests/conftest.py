"""What every level of Lane's cases shares: the double of Claude Code, the walkthrough's helpers,
and Lane's code on the import path, each folder as the part's own entry puts it there: hook.py and
result.py put hooks/lane/domain/, and scripts/lay.py puts domain/ beside it."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LANE = os.path.join(TOP, "plugins", "lane")
for folder in (
    os.path.join(TOP, "dev", "tests"),
    HERE,
    os.path.join(LANE, "hooks", "lane", "domain"),
    os.path.join(LANE, "domain"),
):
    if folder not in sys.path:
        sys.path.insert(0, folder)
