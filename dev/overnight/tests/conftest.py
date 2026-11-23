"""What every level of overnight's cases shares: the folder of overnight's code on the import path,
as `scripts/queue.py` puts `domain/` there, this folder and that of the double of Claude Code,
where the bench and the double lie, and `dev/tests/`, where the writer of the double's program
lies, as the type checker finds each there. `scripts/` stays off the
path, as `queue.py` shares its name with the standard library's `queue`."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DOMAIN = os.path.join(TOP, "plugins", "overnight", "domain")
for folder in (DOMAIN, HERE, os.path.join(HERE, "claude"), os.path.join(TOP, "dev", "tests")):
    if folder not in sys.path:
        sys.path.insert(0, folder)
