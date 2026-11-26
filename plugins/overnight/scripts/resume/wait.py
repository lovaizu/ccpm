"""Decides when the waiter resumes the session: it sleeps out its interval, then becomes the
command it was given, the headless run that resumes the session. It runs as
`python3 wait.py <seconds> <command> [<argument> ...]`, which only resume's hook gives it."""

from __future__ import annotations

import os
import sys
import time

if __name__ == "__main__":
    time.sleep(float(sys.argv[1]))
    os.execv(sys.argv[2], sys.argv[2:])
