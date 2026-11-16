"""item.py, the script by which a role or the skill marks an Item of the Step due done, run as
`script_calls.item_command` gives it: the conversation it speaks for by CLAUDE_CODE_SESSION_ID, and
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
    """Takes an Item's Mark only where the adapter gives it for the Step due.

    Takes: the role or skill and the Item's ID, as its two arguments; CLAUDE_CODE_SESSION_ID from
    the environment; and the plugin's folder. It runs the adapter in the folder it runs in, the
    conversation's, as Bash runs it there.
    Gives: 0, where the ID is one of the Items that `adapters.step_items` gives, run as lanes.json's
    adapter of a step's items, for the Step that `marks.step_due` gives for the one that
    `runs.markers` gives for the role, with its run values; 1, with the Items that
    `marks.items_left` gives, where the ID isn't one of them, or with that no Step is due where
    `runs.markers` gives none or every Step is marked; 2, with why and who must fix it, where the
    adapter fails or lanes.json names none; 2, with why, where the arguments aren't two,
    CLAUDE_CODE_SESSION_ID is missing, the run record or lanes.json can't be read, or lanes.json
    lays no Lane of keeps_steps for the role. Which of several that `runs.markers` gives it takes
    is open, as dev/lane/skeleton-gaps.md says.
    Changes: nothing of Lane's; the guard adds the Mark at the PostToolUse, and the adapter may
    read the plugin's files.
    Refuses: as Gives says, by its exit code.
    Carries: S6 `SA->>IP: item.py <role> <id>`, `IP->>G: asks for the Step due and its Items`, and
    `IP-->>SA: exits 0`, `refuses it, with why and who must fix it`, or `refuses it, with the
    Items left`; S5's Note that the skill's runs of item.py go as S6 draws.
    """
    raise NotImplementedError("item.main")


if __name__ == "__main__":
    run(main, HERE)
