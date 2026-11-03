"""lay.py's course: the lanes the developer AI proposes printed for its approval as each step will
read; once approved, written word for word into its plugin from the same file, so no AI copies what
was approved, with Claude Code's check of the plugin run and the proposal removed; and a plugin
laid before brought up to lane's code, its hooks written in the current form and its lanes said."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

import entries
import lanes
import placed
import rules
import step
import steps
from proposal import Stop, plugin_name, proposal


def laid_before(root: str) -> dict[str, list[dict[str, Any]]]:
    """Each subagent the plugin at root lays lanes in, by its name, with its steps as a proposal
    gives them, as its hooks/lanes.json holds them; none where it is not there. Stops where it is
    there and cannot be read, as the lanes approved before would be lost."""
    if not os.path.exists(os.path.join(root, rules.FILE)):
        return {}
    try:
        laid = rules.read(root)
    except ValueError as why:
        raise Stop(f"lay.py: {root}/{why}; fix it and run again.") from None
    return {a["name"]: a["steps"] for a in laid["subagents"]}


def listed(things: list[str]) -> str:
    """The things, listed with commas and `and` before the last."""
    return " and ".join(filter(None, [", ".join(things[:-1]), things[-1]]))


def printed(path: str) -> str:
    """The proposal as the developer AI reads it for its approval: for each subagent, each lane
    under its action with its hook, and each step as it will read; a step whose lanes are all taken
    out is shown so."""
    given = proposal(path)
    before = laid_before(given["plugin"])
    blocks = []
    for agent in given["subagents"]:
        laid = steps.steps_laid(before, agent)
        rows = [(s["step"], lane) for s in laid for lane in s["lanes"]]
        actions = [lanes.LANES[lane["lane"]].ACTION + ":" for _, lane in rows]
        said = [lanes.sentence(lane["lane"], lane["takes"]) for _, lane in rows]
        wide, long = max(map(len, actions)), max(map(len, said))
        out = [f"Lanes of {agent['name']}, each hook acting in {agent['name']} alone:\n"]
        for (number, lane), action, sentence in zip(rows, actions, said):
            out.append(
                f"  step {number}  {action:<{wide}} {sentence:<{long}}  hook {lane['lane']}\n"
            )
        for s in laid:
            if not s["lanes"]:
                out.append(f"  step {s['step']}  no lane: the sentences laid before taken out\n")
        out.append("\n")
        for s in laid:
            out += steps.read_as_laid(agent["lines"], s)
        blocks.append("".join(out))
    return "\n".join(blocks)


def written(path: str) -> str:
    """Writes the proposal into the plugin: each step, the hook entry, the lanes laid and lane's
    code; has Claude Code check the plugin; removes the proposal, and its folder once nothing else
    is left there; and gives what was done. The lanes laid are those laid before in each other
    subagent whose file is still there, and the proposal's in each of its subagents."""
    given = proposal(path)
    root, plugin = given["plugin"], given["name"]
    hooks = entries.read(root)
    before = laid_before(root)
    laid_now = dict(before)
    said = []
    for agent in given["subagents"]:
        said.append(steps_written(root, agent, before))
        laid_now[agent["name"]] = [{"step": s["step"], "lanes": s["lanes"]} for s in agent["steps"]]
    kept = {n: s for n, s in laid_now.items() if step.agent_file(root, n) is not None}
    entries.written(root, entries.put(hooks, plugin, list(kept)))
    said.append(f"Wrote the hooks of {listed(list(kept))} into hooks/hooks.json.\n")
    rules.write(root, [{"name": n, "steps": s} for n, s in kept.items()])
    said.append("Wrote the lanes laid into hooks/lanes.json.\n")
    placed.code_put(root)
    said.append("Put lane's code in hooks/lane/.\n")
    validated(root, path)
    os.remove(path)
    said += ["claude plugin validate passed.\n", f"Removed the proposal {path}.\n"]
    folder = os.path.dirname(os.path.abspath(path))
    if not os.listdir(folder):
        os.rmdir(folder)
        said.append(f"Removed its folder {folder}.\n")
    return "".join(said)


def steps_written(root: str, agent: dict[str, Any], before: dict[str, Any]) -> str:
    """Writes each step lay.py writes in the subagent into its file, as `steps.steps_laid` gives
    them; gives what was written, said."""
    lines = agent["lines"]
    laid = steps.steps_laid(before, agent)
    # Each step is put back where it is, from the last, so a step of more lines than before leaves
    # where the earlier ones are as it was.
    for s in sorted(laid, key=lambda s: s["span"], reverse=True):
        start, end = s["span"]
        lines[start:end] = steps.read_as_laid(lines, s)
    with open(agent["file"], "w", encoding="utf-8") as f:
        f.write("".join(lines))
    numbers = [str(n) for n in sorted(s["step"] for s in laid)]
    which = f"steps {listed(numbers)}" if len(numbers) > 1 else f"step {numbers[0]}"
    return f"Wrote {which} of {agent['name']} into {os.path.relpath(agent['file'], root)}.\n"


def validated(root: str, path: str) -> None:
    """Has Claude Code check the plugin at root; stops with what it found where it finds it
    malformed, the proposal at the path kept to run again, or where claude is not on PATH."""
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


def brought_up(root: str) -> str:
    """Brings up the plugin's copy of lane's code where it is older than lane, and lane's hook entry
    to the current form wherever it is in another, every other entry and each step as it was; gives
    what was done, and each lane laid before, for the developer AI to keep in its proposal or leave
    out. Stops, bringing nothing up, where the folder holds no plugin's manifest."""
    if not os.path.isfile(os.path.join(root, ".claude-plugin", "plugin.json")):
        raise Stop(
            f"lay.py: {root} holds no .claude-plugin/plugin.json, so it is no plugin's folder;"
            " name the folder of the plugin to lay lanes on."
        )
    name = plugin_name(root)
    hooks = entries.read(root)
    before = laid_before(root)
    said = []
    was = placed.older(root)
    if was is not None:
        placed.code_put(root)
        said.append(
            f"Brought lane's code in hooks/lane/ up from {was} to {placed.lane_version()}.\n"
        )
    kept = [n for n in before if step.agent_file(root, n) is not None]
    now = entries.put(hooks, name, kept)
    if now != hooks:
        entries.written(root, now)
        said.append(f"Wrote the hooks of {listed(kept)} into hooks/hooks.json.\n")
    if not said:
        said.append("hooks/lane/ holds no older copy of lane's code.\n")
    for agent, laid in before.items():
        for s in laid:
            for lane in s["lanes"]:
                sentence = lanes.sentence(lane["lane"], lane["takes"])
                held = step.holds(root, agent, s["step"], sentence)
                gone = "" if held else f', whose step no longer says "{sentence}"'
                said.append(
                    f"Laid before on step {s['step']} of {agent}{gone}: {json.dumps(lane)}\n"
                )
    return "".join(said)
