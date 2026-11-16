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

from form import OutOfForm, read_lanes
from lanes.keeps_steps import at_result
from lanes.kind import Broken
from run_record import Unreadable
from runs import may_give, where
from shell import run


def main(argv: Sequence[str], env: Mapping[str, str], root: str) -> tuple[int, str, str]:
    """Takes a Result where the role may give it in a Run of the conversation.

    Takes: the role or skill and the Result, as its two arguments; CLAUDE_CODE_SESSION_ID from the
    environment; and the plugin's folder.
    Gives: 0, where `runs.may_give` lists the Result for the role in a Run of the conversation that
    `runs.where` gives; 1, with the Results the role may give, where it lists others or none; 1,
    for the skill's Result, with the sentence of the skill's Lane of keeps_steps and the Step due,
    where `lanes.keeps_steps.at_result` breaks it for a Run of the skill that hasn't ended; 2,
    with why, where the arguments aren't two, CLAUDE_CODE_SESSION_ID is missing, or the run record
    or lanes.json can't be read.
    Changes: nothing; the guard adds the Result at the PostToolUse.
    Refuses: as Gives says, by its exit code.
    Carries: S6 `SA->>R: result.py <role> <result>`, `R->>G: asks where each Run stands`, and
    `R-->>SA: exits 0` or `refuses it, with the Results it may give`; S2 and S5's `result.py`;
    S5 `alt a Lane of keeps_steps on the skill finds a Step unmarked in the latest pass` and
    `CC-->>M: result.py refuses it, with that Lane's sentence and the Step due`.
    """
    if len(argv) != 2:
        return 2, "", "result.py: give the role and its Result, as `result.py writer written`\n"
    session_id = env.get("CLAUDE_CODE_SESSION_ID")
    if not session_id:
        return 2, "", "result.py: CLAUDE_CODE_SESSION_ID is missing; run it by Claude Code's Bash\n"
    role, result = argv
    try:
        conversation = where(root, session_id)
        proposal = read_lanes(os.path.join(root, "hooks", "lanes.json")).proposal
    except (OSError, OutOfForm, Unreadable) as e:
        return 2, "", f"result.py: hooks/lanes.json or the run record can't be read: {e}\n"
    allowed = may_give(conversation, role, proposal.routes)
    if result not in allowed:
        named = " or ".join(f"`{each}`" for each in allowed) or "nothing"
        return 1, f"result.py: {role} may give {named} now, not `{result}`.\n", ""
    for each in (r for r in conversation.runs if r.skill == role and not r.ended):
        verdict = at_result(proposal.lanes, each, root, proposal.routes)
        if isinstance(verdict, Broken):
            return 1, f"result.py: {verdict.sentence}\n{verdict.may}\n", ""
    return 0, "", ""


if __name__ == "__main__":
    run(main, HERE)
