"""What every level of rn's cases shares: the folders of rn's code on the import path, as tree.py,
record.py, throwaway.py, and the adapters put `domain/` there, the double of Claude Code in
dev/tests/, and this folder, which holds the example the cases take their words from, with the
double of gh."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FOLDERS = (
    os.path.join(TOP, "plugins", "rn", "domain"),
    os.path.join(TOP, "plugins", "rn", "hooks", "adapters"),
    os.path.join(TOP, "dev", "tests"),
    os.path.join(HERE, "gh"),
    HERE,
)
sys.path[:0] = [folder for folder in FOLDERS if folder not in sys.path]
