"""start_with: the subagent runs the script its step names before anything else, such as turn's
`scripts/turn.py given`, which gives it what it works from."""

from __future__ import annotations

import shell
import step
from call import Call

ACTION = "begin"
WORDING = "First run `<script>`."
# Any call may begin the subagent's work, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
# What runs a script named after it, as the steps tell; a script may also be run by its path.
INTERPRETERS = (["python3"], ["sh"])
# How a step names a script of its plugin, by the plugin's folder Claude Code puts in.
PLUGIN = step.ROOT + "/"


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call is made before the subagent has run a script taken, and runs none itself;
    never where what it did before is not known, as a stop then would hold even once the script
    has run."""
    if call.before is None:
        return False
    return not any(runs(c, takes) for c in [*call.before, call])


def runs(call: Call, takes: list[str]) -> bool:
    """Whether the call runs a script taken: a command whose program, after python3 or sh, is the
    script by its path, or a path ending in it, such as the plugin's folder put in for
    `${CLAUDE_PLUGIN_ROOT}`, with the words after it beginning with those taken after the script.
    A take is read as the step writes the command, by the shell's words as a call's are, after
    python3 or sh, its script named from the plugin's folder where it begins with
    `${CLAUDE_PLUGIN_ROOT}/`; a take naming no script is run by no call."""
    found = []
    for words in call.what if call.action in ("run",) else []:
        ran = program(words)
        path = ran[0] if ran else ""
        for taken in (program(shell.words(t)) for t in takes):
            if not taken:
                continue
            script, *after = taken
            script = script.removeprefix(PLUGIN)
            named = path == script or path.endswith("/" + script)
            found.append(named and ran[1:][: len(after)] == after)
    return any(found)


def program(words: list[str]) -> list[str]:
    """A command's words from its program on, python3 or sh before it left out."""
    return words[1:] if words[:1] in INTERPRETERS else words
