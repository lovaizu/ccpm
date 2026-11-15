"""What rn's prompts' unit cases share: the top of the repository on the import path, from which the
cases take the walkthrough's bench by its path, as the type checker finds it there."""

from __future__ import annotations

import os
import sys

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4))
if TOP not in sys.path:
    sys.path.insert(0, TOP)
