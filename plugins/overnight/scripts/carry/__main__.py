"""carry, as the `overnight` command starts it apart from the user's session to carry one work:
`python3 <plugin>/scripts/carry <work's folder> <work as JSON>`. It runs `carry` of the code in
scripts/overnight, whose `work` module says what it does, with the real `claude`, clock, and
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
from overnight.work import carry, work_of

if __name__ == "__main__":
    carry(sys.argv[1], work_of(sys.argv[2]), claude.run, datetime.datetime.now, time.sleep)
