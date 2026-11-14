"""What every level of Lane's cases shares: the folders of Lane's code on the import path, as
Claude Code runs the guard and lay.py with their own folders there, and the double of Claude Code in
dev/tests/."""

from __future__ import annotations

import os
import sys

TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for folder in (
    os.path.join(TOP, "plugins", "lane", "hooks", "lane"),
    os.path.join(TOP, "plugins", "lane", "scripts"),
    os.path.join(TOP, "dev", "tests"),
    os.path.dirname(os.path.abspath(__file__)),
):
    if folder not in sys.path:
        sys.path.insert(0, folder)
