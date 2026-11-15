"""result.py, the script by which a role or the skill gives its Result, run as
`script_calls.result_command` gives it: the conversation it speaks for by CLAUDE_CODE_SESSION_ID,
and the exit code and words it gives back. The guard adds the Result at the PostToolUse of a run
that gave 0."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "domain"))

from runs import may_give, where  # noqa: F401


def main(argv: Sequence[str], env: Mapping[str, str], root: str) -> tuple[int, str, str]:
    """Takes a Result where the role may give it in a Run of the conversation.

    Takes: the role or skill and the Result, as its two arguments; CLAUDE_CODE_SESSION_ID from the
    environment; and the plugin's folder.
    Gives: 0, where `runs.may_give` lists the Result for the role in a Run of the conversation that
    `runs.where` gives; 1, with the Results the role may give, where it lists others or none; 2,
    with why, where the arguments aren't two, CLAUDE_CODE_SESSION_ID is missing, or the run record
    or lanes.json can't be read.
    Changes: nothing; the guard adds the Result at the PostToolUse.
    Refuses: as Gives says, by its exit code.
    Carries: S6 `SA->>R: result.py <role> <result>`, `R->>G: asks where each Run stands`, and
    `R-->>SA: exits 0` or `refuses it, with the Results it may give`; S2 and S5's `result.py`.
    """
    raise NotImplementedError


if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], os.environ, os.path.dirname(os.path.dirname(HERE)))
    sys.stdout.write(out)
    sys.stderr.write(err)
    raise SystemExit(code)
