"""The layer: what lane:up runs to have the lanes it proposes printed for the building AI's OK,
and, once the building AI has given it, written word for word into its plugin from the same file,
so no AI copies what the building AI approved; and, first on each run of lane:up, to bring the
plugin's copy of lane's code up where it is older, with the hooks lane:up wrote before, and to give
what lane:up reads, which its read_only lane holds it to."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import placed

# The lanes, the hooks' form and the reading of a step are lane's code's, which the guard reads them
# by too.
sys.path.insert(0, placed.CODE)

import entries
import steps
from proposal import Stop, plugin_name, proposal

USAGE = (
    "usage: lay.py print <proposal>\n       lay.py write <proposal>\n"
    "       lay.py up <plugin> <lane's data folder>"
)


def main(argv: list[str]) -> int:
    """Prints the proposal at the path, or writes it into the plugin, or brings up the plugin at the
    path, given lane's data folder, and gives 0; prints what was wrong and gives 1."""
    actions = {"print": printed, "write": written, "up": brought_up}
    # How many arguments each action takes after its name.
    count = {"print": 1, "write": 1, "up": 2}
    given, takes = len(argv) - 1, count.get(argv[0]) if argv else None
    wrong = given != takes  # pragma: no mutate
    if wrong:
        print(USAGE)
        return 1
    try:
        print(actions[argv[0]](*argv[1:]), end="")
    except Stop as stop:
        print(stop)
        return 1
    return 0


def printed(path: str) -> str:
    """The proposal as the building AI reads it: for each subagent step, its lanes, each under its
    action with its hook, and the step as it would read; a step whose lanes are all taken out is
    shown so."""
    given = proposal(path)
    hooks = entries.hooks_read(given["plugin"])
    blocks = []
    for agent in given["subagents"]:
        for s in steps.steps_laid(hooks, given["name"], agent):
            out = [*steps.listed(agent["name"], s), "\n", *steps.read_as_laid(agent["lines"], s)]
            blocks.append("".join(out))
    return "\n".join(blocks)


def written(path: str) -> str:
    """Writes the proposal into the plugin, has Claude Code check it, removes the proposal, and
    gives what was written."""
    given = proposal(path)
    root, plugin = given["plugin"], given["name"]
    hooks = entries.hooks_read(root)
    said = []
    for agent in given["subagents"]:
        lines = agent["lines"]
        for s in steps.steps_laid(hooks, plugin, agent):
            start, end = s["span"]
            lines[start:end] = steps.read_as_laid(lines, s)
            where = os.path.relpath(agent["file"], root)
            said.append(f"Wrote step {s['step']} of {agent['name']} into {where}.\n")
        with open(agent["file"], "w", encoding="utf-8") as f:
            f.write("".join(lines))
        entries.hooks_with(hooks, plugin, agent)
        said.append(f"Wrote the hook of {agent['name']} into hooks/hooks.json.\n")
    said += entries.gone_out(hooks, plugin, root)
    entries.hooks_written(root, hooks)
    placed.code_put(root)
    said.append("Put lane's code in hooks/lane/.\n")
    try:
        done = subprocess.run(
            ["claude", "plugin", "validate", root], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        raise Stop("lay.py: claude is not on PATH; install Claude Code and run again.") from None
    if done.returncode:
        raise Stop(
            f"lay.py: claude plugin validate found {root} malformed:\n{done.stdout}{done.stderr}"
            f"fix what it names, then run `lay.py write {path}` again."
        )
    os.remove(path)
    return "".join(said) + f"claude plugin validate passed.\nRemoved the proposal {path}.\n"


def brought_up(root: str, data: str) -> str:
    """Brings up the plugin's copy of lane's code where it is older than lane, with each hook
    lane:up wrote in it in the current form, laying the same lanes, every other entry and each step
    as it was; gives what was done, each lane left out, as lane does not lay it now, and each lane
    the hooks laid before, for lane:up to put to the building AI, and last what lane:up reads, by
    lane's data folder. Stops, bringing nothing up, where the folder holds no plugin's manifest."""
    if not os.path.isfile(os.path.join(root, ".claude-plugin", "plugin.json")):
        raise Stop(
            f"lay.py: {root} holds no .claude-plugin/plugin.json, so it is no plugin's folder;"
            " name the folder of the plugin to lay lanes on."
        )
    read = reads(root, data, plugin_name(root))
    hooks = entries.hooks_read(root)
    agents, left = entries.laid_before(hooks)
    was = placed.older(root)
    said = []
    if was is not None:
        said.append(
            f"Brought lane's code in hooks/lane/ up from {was} to {placed.lane_version()}.\n"
        )
        placed.code_put(root)
    # The hooks are written in the current form wherever they are in another, as a link to lane's
    # code, in a plugin of the ccpm marketplace, is always lane's version while the hooks lane:up
    # wrote with an older one are not.
    before = json.dumps(hooks)
    for agent, laid in agents.items():
        plugin, name = agent.split(":")
        entries.hooks_with(hooks, plugin, {"name": name, "steps": laid})
    if json.dumps(hooks) != before:
        entries.hooks_written(root, hooks)
        said += [
            f"Wrote the hook of {a.split(':')[1]} into hooks/hooks.json with the lanes it held.\n"
            for a in agents
        ]
    if not said:
        said.append("hooks/lane/ holds no older copy of lane's code.\n")
    return "".join([*said, *left, *steps.said(root, agents), read])


def reads(root: str, data: str, name: str) -> str:
    """What lane:up reads, by whole paths, as one JSON line of `reads`, the value its read_only lane
    takes: the plugin's manifest, skills and agents, which its lanes rest on and nothing else;
    lane's docs/lanes.md, the lanes it proposes; and the proposal, kept in lane's data folder by
    the plugin's name, which a run before may have left, and Claude Code's Write overwrites only
    once read."""
    files = [
        os.path.join(root, ".claude-plugin", "plugin.json"),
        os.path.join(root, "skills"),
        os.path.join(root, "agents"),
        os.path.join(placed.LANE, "docs", "lanes.md"),
        os.path.join(data, f"{name}.json"),
    ]
    return json.dumps({"reads": [os.path.abspath(f) for f in files]}) + "\n"


# Run as the command, and not when the tests import it under the name lay.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
