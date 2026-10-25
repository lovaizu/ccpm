"""What turn:up runs for what must come out the same on every run, and each role for what it is
given: the call started or the run gone on with, as turn's flow says, each print in pages short
enough for the shell to show whole. Python looks first in this file's folder, so turn's own
modules are found before any of the same name."""

from __future__ import annotations

import json
import sys
from typing import IO, Any

import call
import run

USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py next <result> [< <your check or questions as JSON, the answer as it came,"
    " or the agent ID as JSON>]\n"
    "       turn.py next <result> <page>\n"
    "       turn.py questions <result>\n"
    "       turn.py parts <result>"
)
# A page of what turn.py prints is short enough for one read of the shell's output to show it whole.
PAGE = 20000


def main(argv: list[str], stdin: IO[str]) -> int:
    """What turn.py runs: the call checked and the run started or gone on with, each step's outcome
    taken, giving the next move, what the orchestrator judges, or the result written; the questions
    the run asks now, and the parts of the work. Prints what comes next and gives 0, or prints what
    was wrong and gives 1."""
    try:
        if argv[:1] == ["start"] and len(argv) == 2:
            print(json.dumps(run.start(argv[1]), ensure_ascii=False))
        elif argv[:1] == ["next"] and len(argv) == 2:
            print(printed(argv[1], run.next_step(argv[1], stdin.read()), "1"))
        elif argv[:1] == ["next"] and len(argv) == 3:
            print(printed(argv[1], run.view(argv[1]), argv[2]))
        elif argv[:1] == ["questions"] and len(argv) == 2:
            print(json.dumps(run.questions(argv[1]), ensure_ascii=False))
        elif argv[:1] == ["parts"] and len(argv) == 2:
            print(json.dumps(run.parts(argv[1]), ensure_ascii=False))
        else:
            print(USAGE)
            return 1
    except call.Stop as stop:
        print(stop)
        return 1
    return 0


def printed(result: str, out: dict[str, Any], page: str) -> str:
    """What turn.py prints: a move as the line it tells and the tool call itself, last, as one JSON
    line; anything else as JSON, in pages."""
    if "move" in out:
        move = json.dumps(out["move"], ensure_ascii=False)
        return f"{out['line']}\n{move}" if "line" in out else move
    return paged(result, out, page)


def paged(result: str, out: dict[str, Any], page: str) -> str:
    """A page of what turn.py prints, headed by its number among all where there is more than one,
    so the orchestrator sees whole what it judges however long it is, as the shell cuts a long
    print short; stops at a page not among them."""
    text = json.dumps(out, ensure_ascii=False)
    pages = [text[i : i + PAGE] for i in range(0, len(text), PAGE)]
    if not page.isdigit() or not 1 <= int(page) <= len(pages):
        raise call.Stop(f"turn: page {page} is not one of 1 to {len(pages)}")
    # A print in one page comes as it is.
    if not pages[1:]:
        return pages[0]
    head = (
        f"{next(iter(out))}, page {page} of {len(pages)}: see every page, each with"
        f" `turn.py next {result} <page>` in a command of its own with no pipe or redirect"
    )
    return head + "\n" + pages[int(page) - 1]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], sys.stdin))
