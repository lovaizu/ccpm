"""What the orchestrator of a flow runs for its next move, with no arguments, as a command of its
own: the flow its plugin's hooks/lanes.json lays, that file found from the path flow.py is run by,
as in a plugin of the ccpm marketplace hooks/lane/ is a link to lane's code and the flow is the
plugin's, beside the link; and the run, from the IDs the guard puts before the command, the
session's and the orchestrator's, as LANE_SESSION and LANE_AGENT. It reads what the guard kept of
the run, the orchestrator's calls and the answer of each `from` subagent, and nothing the
orchestrator writes, and prints a line for the orchestrator to read and, where there is a move,
the move after it, one JSON line in the form follow_next reads, as docs/flow.md's What flow.py
prints says. Where it cannot tell the run, it prints what is wrong on stderr, and exits 1, which
follow_next counts as no run of the script."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from typing import Any

import called
import hook
import lanes_json
import record
from guard import LAY_AGAIN

# The Markdown marks a line of an answer may be set in, left out at its two ends.
MARKS = "*_`"
# Who must fix a plugin whose manifest names no plugin, its name not known.
NAMELESS = "the plugin's maker must fix it"


class Unknown(Exception):
    """Why flow.py cannot tell the run, and who must fix it."""


def main(script: str, environ: Mapping[str, str]) -> int:
    """Prints the next move of the flow of the plugin flow.py is run in by the path given, for the
    run of the IDs in the environment, and gives 0; prints on stderr why it cannot tell the run and
    gives 1."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(script))))
    plugin = plugin_name(root)
    if plugin is None:
        said = "its .claude-plugin/plugin.json names no plugin"
        return stopped("lane", "this plugin", said, NAMELESS)
    try:
        flow = lanes_json.laid(root).get("flow")
    except ValueError as wrong:
        return stopped(plugin, "this plugin", str(wrong), LAY_AGAIN.format(plugin=plugin))
    if flow is None:
        said = "hooks/lanes.json holds no flow"
        return stopped(plugin, "this plugin", said, LAY_AGAIN.format(plugin=plugin))
    try:
        line, move = where(flow, plugin, environ)
    except Unknown as unknown:
        return stopped(plugin, flow["orchestrator"], *unknown.args)
    print(line)
    if move is not None:
        print(json.dumps({"tool": "Agent", "input": {"subagent_type": f"{plugin}:{move}"}}))
    return 0


def plugin_name(root: str) -> str | None:
    """The name of the plugin at root, as its manifest gives it; None where it gives none."""
    try:
        with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            given = json.load(f)
    except (OSError, ValueError):
        return None
    name = given.get("name") if isinstance(given, dict) else None
    return name if isinstance(name, str) else None


def stopped(plugin: str, of: str, wrong: str, fix: str) -> int:
    """Prints on stderr, headed by the plugin, that lane cannot check the flow of the orchestrator
    named, what is wrong and who must fix it; gives 1."""
    said = f"{plugin}: lane cannot check the flow of {of}: {wrong}. {hook.ASK.format(fix=fix)}"
    print(said, file=sys.stderr)
    return 1


def where(flow: dict[str, Any], plugin: str, environ: Mapping[str, str]) -> tuple[str, str | None]:
    """The line flow.py prints for the run of the IDs in the environment, and the subagent the
    move starts, None for none, by the subagent of the flow the orchestrator started last in a call
    that came back, each row of docs/flow.md's table before another winning over it; stops with
    Unknown where the IDs are not given, the calls kept are not found, or the start of a `from`
    subagent was kept with no ID of the subagent."""
    session, agent = environ.get("LANE_SESSION", ""), environ.get("LANE_AGENT", "")
    place = called.place({"session_id": session, "agent_id": agent})
    if place is None:
        raise Unknown(
            "it was run without the session's and the orchestrator's IDs, which the guard puts"
            f" before {lanes_json.FLOW_PY} run as a command of its own",
            LAY_AGAIN.format(plugin=plugin),
        )
    kept = record.read(place)
    if kept is None:
        raise Unknown("the calls the guard kept of it are not found", hook.CLAUDE_CODE)
    order = flow["order"]
    named = {f"{plugin}:{name}": name for name in order}
    starts = [
        (named[k["input"].get("subagent_type")], k.get("agent"))
        for k in kept
        if k.get("tool") == "Agent"
        and not k.get("failed")
        and isinstance(k.get("input"), dict)
        and k["input"].get("subagent_type") in named
    ]
    if not starts:
        return f"Start `{order[0]}`.", order[0]
    last, started = starts[-1]
    back = next((b for b in flow.get("back", []) if b["from"] == last), None)
    if back is not None:
        if not isinstance(started, str):
            raise Unknown(
                f"the start of {last} was kept with no ID of the subagent", hook.CLAUDE_CODE
            )
        answer = called.answer(session, started)
        if answer is None:
            run = f"Run `{lanes_json.FLOW_PY}` again once its answer has come."
            return f"{last} has not answered yet. {run}", None
        if answers(answer, back["while"]):
            return f"{last} answered `{back['while']}`: start `{back['to']}` again.", back["to"]
    after = order[order.index(last) + 1 :]
    if after:
        return f"Start `{after[0]}`.", after[0]
    return "The flow is done.", None


def answers(answer: str, said: str) -> bool:
    """Whether the answer answers the text: a line of it is that text exactly, case as written, once
    the blanks around the line and the Markdown marks MARKS at its two ends are left out, so `more`
    on a line of its own answers `more` and `No more entries need the writer.` does not."""
    return any(line.strip().strip(MARKS) == said for line in answer.splitlines())


# Run as the command, and not when the tests import it under the name flow; by the path it is run
# by, as Python gives it, with no link followed.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(__file__, os.environ))
