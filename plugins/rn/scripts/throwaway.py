"""throwaway.py, as a generator tries its deliverable:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py <deliverable> <command>`. It runs
`domain/throwaway.py`, which says what it takes and gives."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "domain"))

import throwaway
from fault import end

if __name__ == "__main__":
    end(throwaway.main(sys.argv[1:], os.getcwd()))
