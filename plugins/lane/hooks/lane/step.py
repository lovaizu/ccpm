"""step.py, the command by which a role or the skill gives a Step's Mark, run as
`script_calls.step_command` gives it: a command of its own, which the guard checks at its call and
whose Mark the guard adds at its PostToolUse, so that the script itself only exits 0."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "domain"))

from shell import run


def main(argv: Sequence[str], env: Mapping[str, str], root: str) -> tuple[int, str, str]:
    """Gives a Step's Mark as a command of its own.

    Takes: the role or skill and the Step's number, as its two arguments, the environment, and the
    plugin's folder, none of which it reads, as the guard read the arguments from the command at
    its call.
    Gives: 0, with no words, as the guard let the run through only where it took the Mark.
    Changes: nothing; the guard adds the Mark at the PostToolUse.
    Refuses: nothing.
    Carries: S6 `SA->>SP: step.py <role> <n>` and `SP-->>SA: exits 0`; S5's Note that the skill's
    runs of step.py go as S6 draws.
    """
    raise NotImplementedError("step.main")


if __name__ == "__main__":
    run(main, HERE)
