"""The guard's entry, which each of Lane's hook entries runs as
`python3 <plugin>/hooks/lane/hook.py` on each hook event of Claude Code: it alone holds the form of
Claude Code's hook events and answers, reads each event into the guard's form, and gives Claude Code
the guard's decision. A hook whose script fails stops the call, as its entry's `onFailure` is
`block`."""

from __future__ import annotations

import sys
from collections.abc import Mapping

from domain.event import Event
from domain.guard import Decision


def read(payload: str, environ: Mapping[str, str]) -> tuple[str, Event]:
    """The name of the hook event and the moment it tells, from the JSON payload that Claude Code
    gives on stdin and the hook's environment, whose `CLAUDE_PROJECT_DIR` is the root of the
    repository: a PreToolUse as CALL of its kind of Call; a PostToolUse as RAN, or, of a start or
    a resume, as BEGUN of the subagent that its response names; a PostToolUseFailure as RAN that
    failed; a person's prompt, or a command of a plugin's skill that expands, as TYPED; a prompt
    that tells a subagent's end as REACHED with its status and result; a SubagentStop as ENDS; a
    Stop as TURN_ENDS with each subagent that runs; and each other event as OTHER, in the form that
    the recorded runs of Claude Code show, the acting subagent by `agent_id` alone, never by
    `prompt_id`, which changes as the person types while a subagent runs. Raises
    Fault, naming what it lacks, with Lane to fix it, where the payload isn't such an event."""
    raise NotImplementedError("hook.read")


def answer(name: str, decision: Decision) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr that give Claude Code the decision on the hook event of the
    name, as its hooks reference says: a stop as the event takes one, a PreToolUse's denial with
    its reason, a Stop's or a SubagentStop's block with its reason, a prompt's block, and the
    context that the main conversation reads beside the event where the event takes one."""
    raise NotImplementedError("hook.answer")


def main(stdin: str, environ: Mapping[str, str]) -> tuple[int, str, str]:
    """The guard's answer to the event on stdin, from the laid set of the plugin that holds this
    script and the run records in the system's temporary folder; a stop with why and who must fix
    it where the event can't be read or the laid set can't be loaded."""
    raise NotImplementedError("hook.main")


if __name__ == "__main__":
    import os

    code, out, err = main(sys.stdin.read(), os.environ)
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)
