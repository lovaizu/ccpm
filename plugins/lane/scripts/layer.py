"""The layer's course: the lanes the building AI proposes printed for its approval, and, once
approved, written word for word into its plugin from the same file, so no AI copies what was
approved; and, before it proposes lanes on a plugin laid before, the plugin's copy of lane's code
brought up where it is older, with the hooks the layer wrote before, and the lanes laid said."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
from typing import Any

import entries
import lanes
import lanes_json
import placed
import step
import steps
from proposal import Stop, plugin_name, proposal


def printed(path: str) -> str:
    """The proposal as the building AI reads it: for each subagent step, its lanes, each under its
    action with its hook, and the step as it would read; a step whose lanes are all taken out is
    shown so."""
    given = proposal(path)
    before = laid_before(given["plugin"], given["name"])
    blocks = []
    for agent in given["subagents"]:
        for s in steps.steps_laid(before, given["name"], agent):
            out = [*steps.listed(agent["name"], s), "\n", *steps.read_as_laid(agent["lines"], s)]
            blocks.append("".join(out))
    blocks += [adapter_shown(a) for a in given["adapters"]]
    return "\n".join(blocks)


def written(path: str) -> str:
    """Writes the proposal into the plugin, has Claude Code check it, removes the proposal, its
    adapters beside it and its folder once nothing else is left there, and gives what was
    written. The lanes laid in hooks/lanes.json are those laid before in each other
    subagent the plugin's agents/ still has, and the proposal's in each of its subagents."""
    given = proposal(path)
    root, plugin = given["plugin"], given["name"]
    hooks = entries.hooks_read(root)
    before = laid_before(root, plugin)
    laid, values = dict(before), values_before(root, plugin)
    said = []
    for agent in given["subagents"]:
        lines = agent["lines"]
        for s in steps.steps_laid(before, plugin, agent):
            start, end = s["span"]
            lines[start:end] = steps.read_as_laid(lines, s)
            where = os.path.relpath(agent["file"], root)
            said.append(f"Wrote step {s['step']} of {agent['name']} into {where}.\n")
        with open(agent["file"], "w", encoding="utf-8") as f:
            f.write("".join(lines))
        laid[f"{plugin}:{agent['name']}"] = [
            {"step": s["step"], "lanes": s["lanes"]} for s in agent["steps"]
        ]
        values[f"{plugin}:{agent['name']}"] = agent.get("adapter")
        said.append(f"Wrote the hook of {agent['name']} into hooks/hooks.json.\n")
    said += entries.gone_out(hooks, plugin, root)
    kept = {a: s for a, s in laid.items() if step.agent_file(root, a.split(":")[1]) is not None}
    for agent, on in kept.items():
        entries.hooks_with(hooks, plugin, hooked(root, agent.split(":")[1], on))
    entries.hooks_written(root, hooks)
    lanes_json.lanes_written(root, kept, values)
    said.append("Wrote the lanes laid into hooks/lanes.json.\n")
    copies = [a for a in given["adapters"] if a["beside"]]
    for adapter in copies:
        os.makedirs(os.path.dirname(os.path.join(root, adapter["path"])), exist_ok=True)
        for source in (adapter["source"], os.path.splitext(adapter["source"])[0] + ".json"):
            shutil.copyfile(
                source, os.path.join(root, "hooks", "adapters", os.path.basename(source))
            )
        said.append(f"Wrote the adapter {adapter['path']} with its cases.\n")
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
    said += ["claude plugin validate passed.\n", f"Removed the proposal {path}.\n"]
    for adapter in copies:
        for source in (adapter["source"], os.path.splitext(adapter["source"])[0] + ".json"):
            os.remove(source)
        said.append(f"Removed the adapter {adapter['source']} and its cases from beside it.\n")
    # The proposal's folder, `.lane/<yyyymmdd>-<plugin>/`, goes once nothing of the building AI's
    # is left in it, `.lane/` kept, as turn keeps `.turn/`.
    day = os.path.dirname(os.path.abspath(path))
    folder = os.path.join(day, plugin, "adapters")
    for place in (folder, os.path.dirname(folder)):
        if os.path.isdir(place) and not os.listdir(place):
            os.rmdir(place)
    if not os.listdir(day):
        os.rmdir(day)
        said.append(f"Removed its folder {day}.\n")
    return "".join(said)


def brought_up(root: str) -> str:
    """Brings up the plugin's copy of lane's code where it is older than lane, and each hook the
    layer wrote in it to the current form wherever it is in another, laying the same lanes, kept in
    hooks/lanes.json, every other entry and each step as it was; gives what was done, and each lane
    laid before, for the building AI to keep in its proposal or leave out. Stops, bringing nothing
    up, where the folder holds no plugin's manifest."""
    if not os.path.isfile(os.path.join(root, ".claude-plugin", "plugin.json")):
        raise Stop(
            f"lay.py: {root} holds no .claude-plugin/plugin.json, so it is no plugin's folder;"
            " name the folder of the plugin to lay lanes on."
        )
    name = plugin_name(root)
    hooks = entries.hooks_read(root)
    agents = laid_before(root, name)
    was = placed.older(root)
    said = []
    if was is not None:
        said.append(
            f"Brought lane's code in hooks/lane/ up from {was} to {placed.lane_version()}.\n"
        )
        placed.code_put(root)
    # The hooks are written in the current form wherever they are in another, as a link to lane's
    # code, in a plugin of the ccpm marketplace, is always lane's version while the hooks the layer
    # wrote with an older one are not.
    before = copy.deepcopy(hooks)
    for agent, laid in agents.items():
        plugin, sub = agent.split(":")
        entries.hooks_with(hooks, plugin, hooked(root, sub, laid))
    if hooks != before:
        entries.hooks_written(root, hooks)
        lanes_json.lanes_written(root, agents, values_before(root, name))
        said += [
            f"Wrote the hook of {a.split(':')[1]} into hooks/hooks.json with the lanes it held.\n"
            for a in agents
        ]
    if not said:
        said.append("hooks/lane/ holds no older copy of lane's code.\n")
    values = [
        f"Laid before in {a.split(':')[1]}, its values read by: {json.dumps({'adapter': path})}\n"
        for a, path in values_before(root, name).items()
        if path
    ]
    return "".join([*said, *said_before(root, agents), *values])


def hooked(root: str, name: str, laid: list[dict[str, Any]]) -> dict[str, Any]:
    """The subagent of the name in the plugin at root, as its hooks are written from it: its name,
    the lanes laid in it as steps of a proposal, and whether its entry has it read its part first,
    as step.part finds it."""
    return {"name": name, "steps": laid, "part": step.part(root, name) is not None}


def values_before(root: str, plugin: str) -> dict[str, str | None]:
    """The adapter of the values port each subagent of the plugin at root names, by
    `<plugin>:<name>`, as its hooks/lanes.json holds it; none where it is not there or cannot be
    read, as laid_before then stops."""
    try:
        found = lanes_json.laid(root)["subagents"]
    except ValueError:
        return {}
    return {f"{plugin}:{a['name']}": a.get("adapter") for a in found}


def laid_before(root: str, plugin: str) -> dict[str, list[dict[str, Any]]]:
    """Each subagent the plugin at root lays lanes in, as `<plugin>:<subagent>`, with its lanes as
    steps of a proposal, as its hooks/lanes.json holds them; none where it is not there. Stops where
    it is there and cannot be read, as the lanes approved would be lost."""
    if not os.path.exists(os.path.join(root, "hooks", "lanes.json")):
        return {}
    try:
        found = lanes_json.laid(root)
    except ValueError as why:
        raise Stop(f"lay.py: {root}/{why}; fix it and run again.") from None
    return {f"{plugin}:{a['name']}": a["steps"] for a in found["subagents"]}


def said_before(root: str, agents: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Each lane laid before in each subagent of the plugin at root, as `<plugin>:<name>`,
    each on a step of a proposal, said for the building AI to keep in its proposal or leave out: its
    step, whether the step still says its sentence, and the lane as the proposal gives it."""
    found = []
    for agent, laid in agents.items():
        name = agent.split(":")[1]
        for s in laid:
            for lane in s["lanes"]:
                sentence = lanes.sentence(lane["lane"], lane["takes"])
                held = step.holds(root, name, s["step"], sentence)
                gone = "" if held else f', whose step no longer says "{sentence}"'
                found.append(
                    f"Laid before on step {s['step']} of {name}{gone}: {json.dumps(lane)}\n"
                )
    return found


def adapter_shown(adapter: dict[str, Any]) -> str:
    """The adapter as the print shows it for the building AI's OK: its path, its port and what
    names it, its text, indented, and each case it gives."""
    head = f"Adapter {adapter['path']} of the {adapter['port']} port, for {adapter['by']}"
    lines = adapter["text"].splitlines(True)
    out = [f"{head}, giving each case below:\n"]
    out += [f"    {line}" if line.strip() else "\n" for line in lines]
    for number, case in enumerate(adapter["cases"], 1):
        given, gives = json.dumps(case["given"]), json.dumps(case["gives"])
        out.append(f"  case {number}: given {given}\n    gives {gives}\n")
    return "".join(out)
