#!/usr/bin/env python3
"""rn's adapter of a start's text, which Lane's guard runs as
`hooks/adapters/start_text.py <role>`, with `{"running": [{"role", "text", "values"}, ...]}` of each
start that runs on stdin, in the folder that the conversation works in. It decides how a role's Cut
reads in Lane's form, `{"text": ..., "values": {...}}`: the text, one JSON line of the run values
that tree.py's Cut gives, and the values, which the guard holds the role to, for the work of the
role that no start that runs holds."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))


@dataclass(frozen=True)
class StartText:
    """What the adapter gives for a start: its text, and the run values beside it, the text empty
    where no work of the role waits for a start."""

    text: str
    values: dict[str, str] = field(default_factory=dict)


def start_text(role: str, running: list[dict[str, Any]], cwd: str) -> StartText:
    """The text and the run values of the role's next start in the run of the worktree that holds
    `cwd`, from the Cut that tree.py writes for it: for the tree-keeper, its Cut of the run; for the
    generator, the first deliverable doing that no generator running holds; for the evaluator, the
    first group of the first deliverable whose round has no Answers of it and that no evaluator
    running holds. Raises Wrong, with why, where the role is none of rn's or `cwd` lies in no run's
    worktree."""
    raise NotImplementedError("start_text.start_text")


def main(argv: list[str], stdin: str, cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of the adapter with the arguments and the standard input:
    0 with `{"text": ..., "values": {...}}`; 1 with why, where `start_text` refuses or stdin isn't
    `{"running": [...]}`; 2 with the usage where the arguments aren't one role."""
    raise NotImplementedError("start_text.main")


if __name__ == "__main__":
    exit_code, printed, said = main(sys.argv[1:], sys.stdin.read(), os.getcwd())
    sys.stdout.write(printed)
    sys.stderr.write(said)
    raise SystemExit(exit_code)
