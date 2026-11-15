"""How the plugins' E2E cases measure a key result and try an installation: a run of
dev/scripts/e2e.py on an E2E test file, the records it keeps, runs added until the mean holds, and a
fresh home that a shell command runs in."""

from __future__ import annotations

import datetime
import json
import os
import statistics
import subprocess
import sys
from collections.abc import Callable, Mapping
from typing import Any

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 2))


def e2e(test: str) -> str:
    """Runs e2e.py once on the E2E test file at the path, and gives the folder of its records."""
    done = subprocess.run(
        [sys.executable, "dev/scripts/e2e.py", "run", test],
        cwd=TOP,
        capture_output=True,
        text=True,
        check=True,
    )
    return os.path.join(TOP, done.stdout.strip().splitlines()[-1])


def jsonl(path: str) -> list[dict[str, Any]]:
    """Each line of the JSON Lines file at the path, leaving out blank lines."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def seconds(stamp: str) -> float:
    """The seconds since the epoch of a time as e2e.py writes it, in UTC."""
    moment = datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    return moment.replace(tzinfo=datetime.timezone.utc).timestamp()


def until_steady(measure: Callable[[], float], step: float) -> float:
    """The mean of the measure over runs, adding a run until one more moves the mean by less than
    the step."""
    values = [measure(), measure()]
    while abs(statistics.mean(values) - statistics.mean(values[:-1])) >= step:
        values.append(measure())
    return statistics.mean(values)


def fresh_home(folder: str) -> dict[str, str]:
    """The environment with the folder as the home and Claude Code's settings in it, which hold no
    plugin yet."""
    return dict(os.environ, HOME=folder, CLAUDE_CONFIG_DIR=os.path.join(folder, ".claude"))


def shell(command: str, env: Mapping[str, str]) -> str:
    """What the command printed, run in a shell with the environment, whatever it exits with."""
    done = subprocess.run(command, shell=True, env=env, capture_output=True, text=True, check=False)
    return done.stdout
