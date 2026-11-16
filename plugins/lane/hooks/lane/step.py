"""step.py, the script by which a role or the skill marks a Step done, run as
`script_calls.step_command` gives it: the conversation it speaks for by CLAUDE_CODE_SESSION_ID, and
the exit code and words it gives back. The guard adds the Mark at the PostToolUse of a run that gave
0."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "domain"))

from shell import run


def main(argv: Sequence[str], env: Mapping[str, str], root: str) -> tuple[int, str, str]:
    """Takes a Step's Mark only for the Step due in the role's latest pass.

    Takes: the role or skill and the Step's number, as its two arguments;
    CLAUDE_CODE_SESSION_ID from the environment; and the plugin's folder.
    Gives: 0, where `marks.may_mark` takes the Step for the one that `runs.markers` gives for the
    role in the conversation that `runs.where` gives, with the last Step that
    `lanes.keeps_steps.last_step` gives; 1, with the Step due, where it doesn't, or with that no
    Step is due where `runs.markers` gives none; 2, with why, where the arguments aren't a role
    and a whole number of 1 or more, CLAUDE_CODE_SESSION_ID is missing, the run record or
    lanes.json can't be read, or lanes.json lays no Lane of keeps_steps for the role. Which of
    several that `runs.markers` gives it takes is open, as dev/lane/skeleton-gaps.md says.
    Changes: nothing; the guard adds the Mark at the PostToolUse.
    Refuses: as Gives says, by its exit code.
    Carries: S6 `SA->>SP: step.py <role> <n>`, `SP->>G: asks where the role's Marks stand`, and
    `SP-->>SA: exits 0` or `refuses it, with the Step due`; S5's Note that the skill's runs of
    step.py go as S6 draws.
    """
    raise NotImplementedError("step.main")


if __name__ == "__main__":
    run(main, HERE)
