"""The runner, as the `overnight` command starts it apart from the user's session to run the
queue: `python3 <plugin>/scripts/runner <folder of the works>`. It runs `run` of the code in
scripts/overnight, whose `queue` module says what it does, with the real `claude`, clock, and
sleep."""

from __future__ import annotations

import datetime
import os
import sys
import time

# Python puts this folder first on the import path. The code imports its package from scripts/,
# this folder's parent, so that folder takes its place. Also in ../overnight/__main__.py.
sys.path[0] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from overnight import claude
from overnight.queue import run

if __name__ == "__main__":
    run(sys.argv[1], claude.run, datetime.datetime.now, time.sleep)
