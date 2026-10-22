"""start_with: the subagent runs the script its step names before anything else, such as turn's
`scripts/turn.py given`, which gives it what it works from."""

from __future__ import annotations

from call import Call

ACTION = "begin"
WORDING = "First run `<script>`."
# Any call may begin the subagent's work, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
# What runs a script named after it, as the steps tell; a script may also be run by its path.
INTERPRETERS = (["python3"], ["sh"])


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
    `${CLAUDE_PLUGIN_ROOT}`, with the words after it beginning with those taken after the script."""
    found = []
    for words in call.what if call.action in ("run",) else []:
        program = words[1:] if words[:1] in INTERPRETERS else words
        path = program[0] if program else ""
        for script, *after in (t.split() for t in takes):
            named = path == script or path.endswith("/" + script)
            found.append(named and program[1:][: len(after)] == after)
    return any(found)
