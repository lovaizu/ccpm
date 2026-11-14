"""Decides whether a new version of gh still gives what rn's double of gh gives, as the
compatibility test of rn's architecture says under Test strategy. For each line of each record of a
run of gh in recorded/, `gh-<version>-<what>.jsonl`, whose results the double gives, it runs the
line's command again on the gh installed, in the state that the line's event names, and compares
what gh gives with the line. A line of gh-manual.jsonl comes from no run, so `trace.py sources`
checks its page instead. Run it as `python3 compatibility.py`, with gh logged in to an account that
can read the repository each command names. It exits 0 where gh agrees with every line, 1 where it
differs, printing each difference on a line, and 2 where it can't run gh or read a record, as a
check that can't run passes nothing."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")


@dataclass(frozen=True)
class Ran:
    """What one run of a gh command gave: its exit code, stdout, and stderr."""

    exit: int
    stdout: str
    stderr: str


def runs() -> list[tuple[str, dict[str, Any]]]:
    """Each record of a run of gh in recorded/ by its file's name, with each of its lines, in the
    order of the files' names and of their lines; none of gh-manual.jsonl, which holds no run."""
    raise NotImplementedError("compatibility.runs")


def rerun(each: dict[str, Any], environ: Mapping[str, str]) -> Ran:
    """What the gh installed gives for the line's `command`, in the state that its event names: with
    no login where the event finds none, as a configuration folder of its own and no GH_TOKEN give
    it, and with the login of `environ` otherwise. Raises CantRun, with why, where gh isn't on the
    PATH."""
    raise NotImplementedError("compatibility.rerun")


def differences(each: dict[str, Any], ran: Ran) -> list[str]:
    """Each way in which what gh gave differs from the line, each naming the line's event: another
    exit code; JSON on stdout with a field at any depth that one holds and the other doesn't, or a
    value of another JSON type; and text on stdout or stderr whose words differ apart from the
    values that change on each run, such as an account, an ID, a number, or a token. An empty list
    where they agree."""
    raise NotImplementedError("compatibility.differences")


def main(argv: list[str], environ: Mapping[str, str]) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `compatibility.py`: 0 and nothing where gh agrees with
    each line; 1 and each difference, a line each, where it differs; 2 and why, with who must fix
    it, where gh can't run or a record can't be read, or with the usage where it's given an
    argument."""
    raise NotImplementedError("compatibility.main")


if __name__ == "__main__":
    status, report, why = main(sys.argv[1:], os.environ)
    print(report, end="")
    print(why, end="", file=sys.stderr)
    raise SystemExit(status)
