"""The result script: a subagent of the plugin gives its result by running it as its last step
writes it, `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py <subagent> <result>`. It exits with
no error and says nothing where a route of hooks/lanes.json is from the subagent on the result, or,
where none is from it, the result is `done` and a lane of the subagent's is checked at its end; the
guard keeps the result from the run's PostToolUse. It exits 1 with what is wrong otherwise, which
Claude Code gives as PostToolUseFailure, so nothing is kept. It keeps nothing itself, and the guard
checks the lanes of the end before the command runs, as only the hook is given the run's ID, which
its calls kept are under.

The plugin is the one it lies in, as Claude Code puts the plugin's folder in the step's command;
Python writes no compiled files there, as the step's command cannot say so."""

from __future__ import annotations

import json
import os
import sys
from typing import IO

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
# No module before it on the path has the name of one of lane's.
sys.path.insert(0, os.path.join(HERE, "core", "domain"))  # pragma: no mutate

import guard
import lanes
import routes
import rules
from lanes import run_only

# The plugin's folder, two above this script's in hooks/lane/.
ROOT = os.path.dirname(os.path.dirname(HERE))
USAGE = "give a result as `{command}`."


def plugin_name(root: str) -> str:
    """The plugin's name, as its manifest gives it; lane where it cannot be read, as the step's
    command names no plugin."""
    try:
        with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            given = json.load(f)
    except (OSError, ValueError):
        return "lane"
    name = given.get("name") if isinstance(given, dict) else None
    return name if isinstance(name, str) else "lane"


def said(argv: list[str], root: str) -> str:
    """What is wrong with the result the words give, of the plugin at root; "" where a route is
    from the subagent on it."""
    if len(argv) != 2:
        # One command named gives one.
        forms = run_only.named([routes.command("<subagent>", "<result>")], root)
        form = forms[0]  # pragma: no mutate
        return USAGE.format(command=form)
    name, on = argv
    try:
        laid = rules.read(root)
    except ValueError as why:
        fix = guard.LAY_AGAIN.format(plugin=plugin_name(root))
        return guard.cannot(f"the lanes of {name}", str(why), fix).text
    kinds = [g.lane for g in rules.of(laid, name) or []]
    ons = rules.gives(rules.routes_of(laid), name, kinds)
    if not ons:
        return f"no route is from {name} on a result."
    if on in ons:
        return ""
    commands = run_only.named([routes.command(name, o) for o in ons], root)
    return f"{name} gives no `{on}`. {lanes.sentence('result', commands)}"


def main(argv: list[str], stderr: IO[str], root: str) -> int:
    """Gives 0 where the result the words give is one a route is on, saying nothing; says on
    stderr what is wrong, headed by the plugin's name, and gives 1 otherwise."""
    wrong = said(argv, root)
    if not wrong:
        return 0
    stderr.write(f"{plugin_name(root)}: {wrong}\n")
    return 1


# Run as the command, and not when the tests import it under the name result.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:], sys.stderr, ROOT))
