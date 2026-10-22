"""The layer: what lane:up runs to have the lanes it proposes printed for the builder's OK, and,
once the builder has given it, written word for word into the builder's plugin from the same file,
so no AI copies what the builder approved.

The proposal is a JSON file lane:up keeps in lane's data folder, `${CLAUDE_PLUGIN_DATA}/<plugin>.json`:

    {"plugin": "<the plugin's folder>",
     "subagents": [{"name": "<subagent>",
                    "steps": [{"step": <number>,
                               "lanes": [{"lane": "<lane>", "takes": ["<thing>", ...]}]}]}]}

Writing puts each lane's sentence at the end of its step in the subagent's file, one entry for each
subagent and each event its lanes are held on in the plugin's hooks/hooks.json, every other entry
left as it was, and lane's code in its hooks/lane/: a relative link to lane's in a plugin of the
ccpm marketplace, a copy with lane's version in VERSION anywhere else; then has Claude Code check
the plugin, and removes the proposal.

Bringing a plugin up, run first on each run of lane:up, puts lane's code in place of an older copy
of it, one whose VERSION is lower than lane's version or missing, and writes each hook lane:up wrote
before in the current form, with the lanes it read from it, every other entry and each step left as
it was; a lane this version no longer lays is left out and said, for the builder to lay again or
leave out.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from typing import Any

LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(LANE, "hooks", "lane")
# The lanes and the reading of a step are lane's code's, which the guard reads them by too.
sys.path.insert(0, CODE)

import lanes
import step
from lanes import in_form

USAGE = "usage: lay.py print <proposal>\n       lay.py write <proposal>\n       lay.py up <plugin>"
# Each hook's command first checks that lane's code can run, and where it cannot, on an event of
# its subagent, read from the event's text by the shell alone, as Claude Code writes it, with or without a blank after
# the colon, says what to install and exits with its event's code; it lets any other event through,
# as its lanes act in their subagent alone.
CHECK = (
    'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
    ' || {{ e=; while IFS= read -r l || [ -n "$l" ]; do e="$e$l"; l=; done;'
    """ case "$e" in *'"agent_type":"{agent}"'*|*'"agent_type": "{agent}"'*)"""
    ' echo "{plugin}: install Python 3.9 or later, run as python3, for its hooks to run" >&2;'
    " exit {code};; esac; exit 0; }}"
)
# The events lanes are held on, each with its own script in lane's code, named after it, and what
# its hook exits with where lane's code cannot run: on a tool call 2, which stops the call; at the
# subagent's end 1, which tells the user and lets the subagent end, as it cannot install Python and
# kept going it would only be asked again.
EVENTS = {"PreToolUse": 2, "SubagentStop": 1}
# The marketplace whose plugins take lane's code through a link to lane beside them, as installing
# copies what a link within the marketplace points to.
MARKETPLACE = "ccpm"
# What the proposal is told to be, when it is not.
AGAIN = "write the proposal again as lane:up's steps give it"


class Stop(Exception):
    """What was wrong, and what to do, where lay.py cannot go on."""


def main(argv: list[str]) -> int:
    """Prints the proposal at the path, or writes it into the plugin, or brings up the plugin at the
    path, and gives 0; prints what was wrong and gives 1."""
    actions = {"print": printed, "write": written, "up": brought_up}
    if len(argv) != 2 or argv[0] not in actions:
        print(USAGE)
        return 1
    try:
        print(actions[argv[0]](argv[1]), end="")
    except Stop as stop:
        print(stop)
        return 1
    return 0


def wrong(what: str) -> Stop:
    """The stop saying what is wrong with the proposal."""
    return Stop(f"lay.py: the proposal {what}; {AGAIN}.")


def proposal(path: str) -> dict[str, Any]:
    """The proposal at the path, checked to be as lane:up writes it, with the plugin's name, and
    each subagent with its file and its lines, and each step with where it is among them."""
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise Stop(f"lay.py: there is no file {path}; {AGAIN}.") from None
    except ValueError:
        raise Stop(f"lay.py: {path} holds no JSON; {AGAIN}.") from None
    root = given.get("plugin") if isinstance(given, dict) else None
    if not isinstance(root, str):
        raise wrong("names no plugin")
    subagents = given.get("subagents")
    if not isinstance(subagents, list) or not subagents:
        raise wrong("gives no subagents")
    return {
        "plugin": root,
        "name": plugin_name(root),
        "subagents": [subagent(root, s) for s in subagents],
    }


def plugin_name(root: str) -> str:
    """The plugin's name, from its manifest, as a hook's command can carry it unquoted."""
    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(manifest, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise wrong(f"names {root} as the plugin, which has no {manifest}") from None
    except ValueError:
        given = None
    name = given.get("name") if isinstance(given, dict) else None
    if not isinstance(name, str) or not re.fullmatch(lanes.NAME, name):
        raise Stop(
            f"lay.py: {manifest} names the plugin by no name of letters, digits and -._; fix it"
            " and run again."
        )
    return name


def subagent(root: str, given: Any) -> dict[str, Any]:
    """A subagent of the proposal, checked, with its file and its lines, and each step with where
    it is among them."""
    name = given.get("name") if isinstance(given, dict) else None
    if not isinstance(name, str) or not re.fullmatch(lanes.NAME, name):
        raise wrong("gives a subagent no name")
    file = step.agent_file(root, name)
    if file is None:
        raise wrong(f"gives {name}, which no file in agents/ names")
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    steps = given.get("steps")
    if not isinstance(steps, list) or not steps:
        raise wrong(f"gives {name} no steps")
    for s in steps:
        number = s.get("step") if isinstance(s, dict) else None
        if not isinstance(number, int):
            raise wrong(f"gives a step of {name} no number")
        where = step.span([line.rstrip("\n") for line in lines], number)
        if where is None:
            raise wrong(f"gives step {number}, which the Steps of {name} do not have")
        laid = s.get("lanes")
        if not isinstance(laid, list) or not laid:
            raise wrong(f"gives step {number} of {name} no lanes")
        for lane in laid:
            lane_check(lane, f"step {number} of {name}", root)
        s["span"] = where
    return {"name": name, "file": file, "lines": lines, "steps": steps}


def lane_check(lane: Any, on: str, root: str) -> None:
    """Stops where the lane is not one lane lays, taking a text with no comma for each thing it
    shows; or, for in_form, where its form is no form lane reads in the plugin at root."""
    known = lane.get("lane") if isinstance(lane, dict) else None
    if known not in lanes.LANES:
        raise wrong(f"gives {known}, which is no lane, on {on}")
    takes = lane.get("takes")
    if not isinstance(takes, list):
        raise wrong(f"gives {known} on {on} no takes")
    if not all(isinstance(t, str) and t and "," not in t for t in takes):
        raise wrong(f"gives {known} on {on} takes that are not each a text with no comma")
    if not lanes.fits(known, takes):
        raise wrong(
            f"gives {known} on {on} takes of another count than its wording and its hook hold"
        )
    if known in ("in_form",):
        try:
            in_form.form(root, takes[1])
        except ValueError as why:
            raise Stop(
                f"lay.py: the form {takes[1]} of in_form on {on} {why}; fix the form or the"
                " proposal and run again."
            ) from None


def sentences(step_given: dict[str, Any]) -> list[str]:
    """The sentence of each lane on the step."""
    return [lanes.sentence(lane["lane"], lane["takes"]) for lane in step_given["lanes"]]


def read_as_laid(lines: list[str], step_given: dict[str, Any]) -> list[str]:
    """The step's lines as they would read with each sentence it does not yet say put at its
    end."""
    start, end = step_given["span"]
    text = step.says([line.rstrip("\n") for line in lines], (start, end))
    added = [s for s in sentences(step_given) if s not in text]
    last = lines[end - 1].rstrip("\n")
    return [*lines[start : end - 1], " ".join([last, *added]) + "\n"]


def printed(path: str) -> str:
    """The proposal as the builder reads it: for each subagent step, its lanes, each under its
    action with its hook, and the step as it would read."""
    blocks = []
    for agent in proposal(path)["subagents"]:
        for s in agent["steps"]:
            name, said = agent["name"], sentences(s)
            out = [f"Lanes on step {s['step']} of {name}, each hook acting in {name} alone:\n"]
            actions = [lanes.LANES[lane["lane"]].ACTION + ":" for lane in s["lanes"]]
            wide, long = max(map(len, actions)), max(map(len, said))
            for action, sentence, lane in zip(actions, said, s["lanes"]):
                hook = f"hook {lane['lane']}{held(lane)}"
                out.append(f"  {action:<{wide}} {sentence:<{long}}  {hook}\n")
            out.append("\n" + "".join(read_as_laid(agent["lines"], s)))
            blocks.append("".join(out))
    return "\n".join(blocks)


def held(lane: dict[str, Any]) -> str:
    """What the lane's hook holds beyond what its sentence shows, as the builder reads it after the
    hook, such as the commands wait_for holds back; "" for a lane whose sentence shows all."""
    shown = lanes.shown(lane["lane"])
    rest = [f"`{t}`" for t in lane["takes"][shown:]] if shown is not None else []
    return f", holding back {', '.join(rest)}" if rest else ""


def run(event: str) -> str:
    """What a hook's command runs for the event: its script in lane's code."""
    return f'exec python3 "${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/{event.lower()}.py"'


def command(plugin: str, agent: str, laid: list[str], event: str = "PreToolUse") -> str:
    """The hook's command running lane's code on the lanes laid in the subagent, held on the
    event."""
    words = " ".join(shlex.quote(w) for w in [agent, *laid])
    return f"{CHECK.format(plugin=plugin, agent=agent, code=EVENTS[event])}; {run(event)} {words}"


def entry(plugin: str, agent: dict[str, Any], event: str = "PreToolUse") -> dict[str, Any] | None:
    """The subagent's entry of hooks.json for the event, None where none of its lanes is held on
    it: its matcher the tools its lanes watch, or for SubagentStop the subagent, as its matcher
    tells agents apart, and its command giving each lane laid."""
    every = [(s["step"], g) for s in agent["steps"] for g in s["lanes"]]
    on_it = [(n, g) for n, g in every if event in lanes.held_on(g["lane"])]
    if not on_it:
        return None
    name = f"{plugin}:{agent['name']}"
    laid = [lanes.word(n, g["lane"], g["takes"]) for n, g in on_it]
    each = [t for _, g in on_it for t in getattr(lanes.LANES[g["lane"]], "TOOLS", ())]
    tools = [name] if event in ("SubagentStop",) else each
    run_it = command(plugin, name, laid, event)
    return {
        "matcher": "|".join(dict.fromkeys(tools)),
        "hooks": [{"type": "command", "timeout": 10, "command": run_it}],
    }


def hooks_read(root: str) -> dict[str, Any]:
    """The plugin's hooks.json, an empty one where there is none; stops where it is not in Claude
    Code's shape."""
    path = os.path.join(root, "hooks", "hooks.json")
    if not os.path.exists(path):
        return {"hooks": {}}
    unshaped = Stop(f"lay.py: {path} is not in the shape Claude Code reads; fix it and run again.")
    try:
        with open(path, encoding="utf-8") as f:
            hooks = json.load(f)
    except ValueError:
        raise unshaped from None
    events = hooks.get("hooks", {}) if isinstance(hooks, dict) else None
    if not isinstance(events, dict):
        raise unshaped
    for event in EVENTS:
        entries = events.get(event, [])
        if not isinstance(entries, list) or not all(map(entry_shaped, entries)):
            raise unshaped
    return hooks


def entry_shaped(entry: Any) -> bool:
    """Whether an entry of hooks.json is an object whose hooks are a list of objects."""
    each = entry.get("hooks", []) if isinstance(entry, dict) else None
    return isinstance(each, list) and all(isinstance(h, dict) for h in each)


def words(command: Any, event: str) -> list[str]:
    """The words a hook's command gives the event's script in lane's code, the first the subagent
    as `<plugin>:<subagent>`, each after it a lane laid; none for a command that runs no script of
    lane's, names no subagent so, or gives words the shell cannot read."""
    found = re.search(rf'/hooks/lane/{event.lower()}\.py"?(.*)', str(command))
    try:
        given = shlex.split(found[1]) if found else []
    except ValueError:
        return []
    return given if given and lanes.AGENT.fullmatch(given[0]) else []


def hooks_with(hooks: dict[str, Any], plugin: str, agent: dict[str, Any]) -> None:
    """Puts the subagent's entry of each event its lanes are held on into the hooks: where lane:up
    wrote one for it before, in the place of the first, after every other entry otherwise; and
    takes out those lane:up wrote for it before on an event none of its lanes is held on now."""
    events = hooks.setdefault("hooks", {})
    for event in EVENTS:
        entries = events.get(event, [])
        mark = [f"{plugin}:{agent['name']}"]
        ours = [
            any(words(h.get("command"), event)[:1] == mark for h in e.get("hooks", []))
            for e in entries
        ]
        place = ours.index(True) if True in ours else len(entries)
        others = [e for e, our in zip(entries, ours) if not our]
        new = entry(plugin, agent, event)
        kept = [*others[:place], *([new] if new else []), *others[place:]]
        # An event the hooks hold no entry of is left out, not written as an empty list.
        if kept or entries:
            events[event] = kept


def marketplace(folder: str) -> str | None:
    """The name of the marketplace kept in the folder; None where it keeps none, or none that can
    be read."""
    try:
        with open(
            os.path.join(folder, ".claude-plugin", "marketplace.json"), encoding="utf-8"
        ) as f:
            given = json.load(f)
    except (OSError, ValueError):
        return None
    return given.get("name") if isinstance(given, dict) else None


def lanes_own(place: str) -> bool:
    """Whether the folder is lane's code itself, as hooks/lane/ is on lane."""
    # Told by membership rather than `==`, as an order comparison such as `<=` would hold for other
    # paths too, and a mutant making it one would pass every test.
    return os.path.realpath(place) in (os.path.realpath(CODE),)


def lane_version() -> str:
    """lane's version, as its plugin.json gives it."""
    with open(os.path.join(LANE, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def code_put(root: str) -> None:
    """Puts lane's code in the plugin's hooks/lane/, in place of what was there; on lane itself,
    whose hooks/lane/ is that code, leaves it as it is."""
    place = os.path.join(root, "hooks", "lane")
    if lanes_own(place):
        return
    if os.path.islink(place):
        os.remove(place)
    elif os.path.isdir(place):
        shutil.rmtree(place)
    os.makedirs(os.path.dirname(place), exist_ok=True)
    above = os.path.dirname(os.path.abspath(root))
    beside = os.path.join(above, "lane", "hooks", "lane")
    if marketplace(above) == MARKETPLACE and os.path.isdir(beside):
        os.symlink(os.path.join("..", "..", "lane", "hooks", "lane"), place)
        return
    shutil.copytree(CODE, place, ignore=shutil.ignore_patterns("__pycache__"))
    with open(os.path.join(place, "VERSION"), "w", encoding="utf-8") as f:
        f.write(lane_version() + "\n")


def hooks_written(root: str, hooks: dict[str, Any]) -> None:
    """Writes the hooks into the plugin's hooks/hooks.json, indented by two, as Claude Code reads
    them."""
    os.makedirs(os.path.join(root, "hooks"), exist_ok=True)
    with open(os.path.join(root, "hooks", "hooks.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(hooks, indent=2, ensure_ascii=False) + "\n")


def written(path: str) -> str:
    """Writes the proposal into the plugin, has Claude Code check it, removes the proposal, and
    gives what was written."""
    given = proposal(path)
    root, plugin = given["plugin"], given["name"]
    hooks = hooks_read(root)
    said = []
    for agent in given["subagents"]:
        lines = agent["lines"]
        for s in agent["steps"]:
            start, end = s["span"]
            lines[start:end] = read_as_laid(lines, s)
            where = os.path.relpath(agent["file"], root)
            said.append(f"Wrote step {s['step']} of {agent['name']} into {where}.\n")
        with open(agent["file"], "w", encoding="utf-8") as f:
            f.write("".join(lines))
        hooks_with(hooks, plugin, agent)
        said.append(f"Wrote the hook of {agent['name']} into hooks/hooks.json.\n")
    hooks_written(root, hooks)
    code_put(root)
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


def semver(text: str) -> tuple[int, ...]:
    """The version the text gives as major, minor and patch, to be compared as numbers; none,
    which is lower than every version, where it gives none."""
    found = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)", text.strip())
    return tuple(map(int, found.groups())) if found else ()


def older(root: str) -> str | None:
    """The version of the plugin's copy of lane's code, as its VERSION gives it, where the copy is
    older than lane: its version lower, or not given; None where hooks/lane/ is no copy, being a
    link, lane's own or not there, or is a copy of lane's version or a newer."""
    place = os.path.join(root, "hooks", "lane")
    if os.path.islink(place) or not os.path.isdir(place) or lanes_own(place):
        return None
    try:
        with open(os.path.join(place, "VERSION"), encoding="utf-8") as f:
            given = f.read().strip()
    except OSError:
        return "a copy with no VERSION"
    return given if semver(given) < semver(lane_version()) else None


def laid_before(hooks: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Each subagent the hooks lay lanes in, as `<plugin>:<subagent>`, with its lanes as steps of a
    proposal, each lane once, though held on both events; and each lane laid that lane does not lay
    now, as said for lane:up to put to the builder."""
    agents: dict[str, list[dict[str, Any]]] = {}
    left = []
    for event in EVENTS:
        for e in hooks.get("hooks", {}).get(event, []):
            for h in e.get("hooks", []):
                given = words(h.get("command"), event)
                steps = agents.setdefault(given[0], []) if given else []
                for w in given[1:]:
                    lane = lanes.read(w)
                    if lane is None:
                        name = given[0].split(":")[1]
                        left.append(
                            f"Left out `{w}` from the hook of {name}, as lane {lane_version()} lays"
                            " no such lane; ask the builder whether to lay it again or leave it"
                            " out.\n"
                        )
                        continue
                    number, kind, takes = lane
                    s = {"step": number, "lanes": [{"lane": kind, "takes": takes}]}
                    if s not in steps:
                        steps.append(s)
    return agents, list(dict.fromkeys(left))


def brought_up(root: str) -> str:
    """Brings up the plugin's copy of lane's code where it is older than lane, with each hook
    lane:up wrote in it in the current form, laying the same lanes, every other entry and each step
    as it was; gives what was done, and each lane left out, as lane does not lay it now."""
    was = older(root)
    if was is None:
        return "hooks/lane/ holds no older copy of lane's code.\n"
    hooks = hooks_read(root)
    agents, left = laid_before(hooks)
    said = [f"Brought lane's code in hooks/lane/ up from {was} to {lane_version()}.\n"]
    for agent, steps in agents.items():
        plugin, name = agent.split(":")
        hooks_with(hooks, plugin, {"name": name, "steps": steps})
        said.append(f"Wrote the hook of {name} into hooks/hooks.json with the lanes it held.\n")
    hooks_written(root, hooks)
    code_put(root)
    return "".join([*said, *left])


# Run as the command, and not when the tests import it under the name lay. It is written as
# membership rather than `==`, since an order comparison such as `<=` would also tell "__main__"
# from "lay", and a mutant making it one would pass every test.
if __name__ in ("__main__",):
    sys.exit(main(sys.argv[1:]))
