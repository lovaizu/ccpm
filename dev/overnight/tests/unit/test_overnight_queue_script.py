"""The unit cases of scripts/queue.py, which each skill and the stacker run: `main`, of a subcommand
that is none of stack, check, and run, and of none, run as the skill runs the script."""

from __future__ import annotations

import subprocess
import sys

import pytest
from overnight_bench import QUEUE_PY

USAGE = (
    "usage: queue.py stack <queue file>\n"
    "       queue.py check [<queue file>]\n"
    "       queue.py run\n"
)


@pytest.mark.supports("test_each_skill_runs_its_script_and_shows_what_it_prints")
@pytest.mark.parametrize("argv", [[], ["show"], ["Stack"]], ids=["none", "another", "another case"])
def test_a_subcommand_of_no_part_gives_2_with_the_usage(argv: list[str]):
    """Given no subcommand, `show`, or `Stack`
    When `queue.py` runs with it
    Then it gives 2 with the usage on its standard error, and prints nothing else"""
    done = subprocess.run(
        [sys.executable, QUEUE_PY, *argv], capture_output=True, text=True, check=False
    )

    assert (done.returncode, done.stdout, done.stderr) == (2, "", USAGE)
