"""lay.py's course: the lanes and routes the user proposes printed for their approval as each step
will read; once approved, written word for word into their plugin from the same file, so no AI
copies what was approved, with Claude Code's check of the plugin run and the proposal removed; and
a plugin laid before brought up to lane's code, its hooks written in the current form, the
sentences its steps say in a wording lane laid before put in the current one, and its lanes said.

The routes are laid as sentences in the steps beside the lanes: follow_routes' on the step of the
skill they start from, and the result command on the last step of each subagent giving a result, or
with a lane checked at its end, `done` where no route is from it. A proposal giving routes replaces
those laid before, and the sentences of those before come out; one giving none keeps them, with
their sentences. A subagent's adapters are written with their cases into the plugin's
hooks/adapters/, and those of the proposal removed from beside it. Subagents whose entries name one
part share its steps, so a proposal laying different lanes on a step of it is refused."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

import entries
import lanes
import placed
import routes
import rules
import step
import steps
from proposal import Stop, plugin_name, proposal, skill_lines, subagent


def laid_before(root: str) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any] | None]:
    """Each subagent the plugin at root lays lanes in, by its name, with its steps as a proposal
    gives them, and the routes laid, as its hooks/lanes.json holds them; none where it is not
    there. Stops where it is there and cannot be read, as the lanes approved before would be
    lost."""
    laid = read_before(root)
    return {a["name"]: a["steps"] for a in laid["subagents"]}, rules.routes_of(laid)


def read_before(root: str) -> dict[str, Any]:
    """The plugin's hooks/lanes.json, as `laid_before` reads it; none laid where it is not
    there."""
    if not os.path.exists(os.path.join(root, rules.FILE)):
        return {"subagents": []}
    try:
        return rules.read(root)
    except ValueError as why:
        raise Stop(f"lay.py: {root}/{why}; fix it and run again.") from None


def routed(
    given: dict[str, Any] | None,
    name: str,
    lines: list[str],
    laid: list[dict[str, Any]],
    results: list[str] | None = None,
) -> list[dict[str, Any]]:
    """The steps the routes lay sentences on in the subagent or skill of the name, whose file has
    the lines and whose steps lay the lanes given: follow_routes on the skill's step, and the result
    command on its last step where it gives a result, by a route from it, by the results of its
    own given, or `done` with a lane checked at its end."""
    found = []
    if given is not None and given["orchestrator"] == name:
        found.append({"step": given["step"], "lanes": [{"lane": "follow_routes", "takes": []}]})
    ends = any(lanes.ends(g["lane"]) for s in laid for g in s["lanes"])
    ons = routes.gives(given, name, ends, results)
    last = step.last([line.rstrip("\n") for line in lines])
    if ons and last is not None:
        commands = [routes.command(name, on) for on in ons]
        found.append({"step": last, "lanes": [{"lane": "result", "takes": commands}]})
    return found


def merged(*given: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The steps given, each step's lanes together under its number, in the order each first
    comes."""
    found: dict[int, list[dict[str, Any]]] = {}
    for each in given:
        for s in each:
            found.setdefault(s["step"], []).extend(s["lanes"])
    return [{"step": n, "lanes": lanes_of} for n, lanes_of in found.items()]


def skills(*given: dict[str, Any] | None) -> list[str]:
    """The skill each of the routes given starts from, once each; none for routes not given."""
    return list(dict.fromkeys(r["orchestrator"] for r in given if r))


def agents(
    given: dict[str, Any], before: dict[str, Any], routes_before: dict[str, Any] | None
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """Each subagent or skill lay.py writes, as `steps.steps_laid` takes it, with the steps it lays
    as each reads before, by its name: the proposal's subagents, and, where the proposal gives
    routes, each skill and subagent they or those before name whose file is there, a skill marked
    so; each with its lanes, the proposal's or those laid before, and the sentences of the routes,
    the proposal's or those laid before."""
    root, now = given["plugin"], given["routes"] or routes_before
    results_before = {a["name"]: a.get("results") for a in read_before(root)["subagents"]}
    names = [a["name"] for a in given["subagents"]]
    if given["routes"]:
        extra = routes.named(given["routes"]) + routes.named(routes_before or given["routes"])
        names += [n for n in dict.fromkeys(extra) if n not in names]
    found, was = [], {}
    for name in names:
        # Each subagent comes once in the proposal, so `is` finds its entry as `==`.
        given_as = [a for a in given["subagents"] if a["name"] == name]  # pragma: no mutate
        agent: dict[str, Any] | None = next(iter(given_as), None)
        if agent is None and name in skills(given["routes"], routes_before):
            if step.skill_file(root, name) is None:
                continue
            file, lines_ = skill_lines(root, name)
            agent = {"name": name, "file": file, "lines": lines_, "steps": [], "skill": True}
        if agent is None:
            if step.agent_file(root, name) is None:
                continue
            kept = [dict(s) for s in before.get(name, [])]
            results = {"results": results_before[name]} if results_before.get(name) else {}
            agent = subagent(root, {"name": name, **results, "steps": kept})
        lines = [line.rstrip("\n") for line in agent["lines"]]
        own = agent.get("results")
        laid = merged(agent["steps"], routed(now, name, agent["lines"], agent["steps"], own))
        laid_now = [{**s, "span": step.span(lines, s["step"])} for s in laid]
        earlier = before.get(name, [])
        was_own = results_before.get(name)
        was[name] = merged(earlier, routed(routes_before, name, agent["lines"], earlier, was_own))
        found.append({**agent, "steps": laid_now})
    shared(root, found, before)
    return found, was


def shared(root: str, found: list[dict[str, Any]], before: dict[str, Any]) -> None:
    """Stops where subagents whose entries name one part would lay different lanes on a step of it,
    those lay.py writes and those laid before in any other subagent sharing it alike, naming them
    and the step."""
    laying = {a["name"]: (a["file"], a["steps"]) for a in found}
    for name, steps_before in before.items():
        file = step.steps_file(root, name)
        if name not in laying and file is not None:
            laying[name] = (file, steps_before)
    by_part: dict[str, list[tuple[str, dict[int, list[str]]]]] = {}
    for name, (file, laid) in laying.items():
        if step.part(root, name) is None:
            continue
        said = {s["step"]: steps.sentences(s) for s in laid}
        by_part.setdefault(os.path.realpath(file), []).append((name, said))
    for part, each in by_part.items():
        for (first, a), (other, b) in zip(each, each[1:]):
            for number in sorted(set(a) | set(b)):
                if a.get(number, []) != b.get(number, []):
                    shown = os.path.relpath(part, os.path.realpath(root))
                    raise Stop(
                        f"lay.py: {first} and {other} share their part {shown}, and would lay"
                        f" different lanes on its step {number}; give them the same lanes there,"
                        " and run again."
                    )


def routes_printed(given: dict[str, Any]) -> str:
    """The routes as the user reads them: the step they are laid on, each route from the
    first start or a subagent's result to the start next, each subagent run several at once, and
    each order of results."""
    rows = [
        ("first" if "on" not in r else f"{r['from']} `{r['on']}`", r.get("to") or "no more")
        for r in given["routes"]
    ]
    wide = max(len(left) for left, _ in rows)
    out = [f"Routes of {given['orchestrator']}, laid on its step {given['step']}:\n"]
    out += [f"  {left:<{wide}}  start {to}\n" for left, to in rows]
    out += [f"  runs at once of {name}\n" for name in given.get("fan_out", [])]
    precedence = given.get("precedence")
    orders = precedence.items() if isinstance(precedence, dict) else [("", precedence or [])]
    for name, taken in (o for o in orders if o[1]):
        of = f" of {name}" if name else ""
        listed = ", ".join(f"`{on}`" for on in taken)
        out.append(f"  results{of} taken first to last: {listed}\n")
    return "".join(out)


def printed(path: str) -> str:
    """The proposal as the user reads it for their approval: the routes it gives, each from a
    subagent on its result to the start next, with the skill's step as it will read; then, for each
    subagent, each lane under its action with its type, and each step as it will read; a step whose
    lanes are all taken out is shown so, and a skill the routes no longer start, with its step."""
    given = proposal(path)
    before, routes_before = laid_before(given["plugin"])
    found, was = agents(given, before, routes_before)
    blocks = []
    if given["routes"]:
        blocks.append(routes_printed(given["routes"]))
    for agent in found:
        laid = steps.steps_laid(was, agent)
        if agent.get("skill"):
            lines = [line for s in laid for line in steps.read_as_laid(agent["lines"], s)]
            if agent["name"] == given["routes"]["orchestrator"]:
                blocks[0] += "\n" + "".join(lines)
            else:
                blocks.append(f"Routes no longer laid on {agent['name']}:\n\n" + "".join(lines))
            continue
        rows_of = [(s["step"], lane) for s in laid for lane in s["lanes"]]
        actions = [lanes.action(lane["lane"]) + ":" for _, lane in rows_of]
        said = [lanes.sentence(lane["lane"], lane["takes"]) for _, lane in rows_of]
        # With no row, no width is used.
        wide = max(map(len, actions), default=0)  # pragma: no mutate
        # The routes' sentences, long, set no width, so the rules' types line up beside theirs.
        rules_said = [s for (_, g), s in zip(rows_of, said) if g["lane"] not in lanes.ROUTED]
        long = max(map(len, rules_said), default=0)  # pragma: no mutate
        out = [f"Lanes of {agent['name']}, each checked only in {agent['name']}:\n"]
        for (number, lane), action, sentence in zip(rows_of, actions, said):
            kind = lanes.kind(lane["lane"])
            out.append(f"  step {number}  {action:<{wide}} {sentence:<{long}}  type {kind}\n")
        for s in laid:
            if not s["lanes"]:
                out.append(f"  step {s['step']}  no lane: the sentences laid before taken out\n")
        for a in agent.get("adapters", []):
            out.append(f"  adapter {a['path']}: its {a['count']} cases given as they say\n")
        out.append("\n")
        for s in laid:
            out += steps.read_as_laid(agent["lines"], s)
        blocks.append("".join(out))
    return "\n".join(blocks)


def written(path: str) -> str:
    """Writes the proposal into the plugin: each step, the hook entries, the lanes laid and the
    routes, and lane's code; has Claude Code check the plugin; removes the proposal, and its folder
    once nothing else is left there; and gives what was done. The lanes laid are those laid before
    in each other subagent whose file is still there, and the proposal's in each of its subagents;
    the routes, the proposal's, or those laid before where it gives none. Each other step saying a
    sentence laid before in a wording lane laid before has it put in the current one, as `lay.py up`
    puts it, as lane's code laid with it checks the current one."""
    given = proposal(path)
    root, plugin = given["plugin"], given["name"]
    hooks = entries.read(root)
    before, routes_before = laid_before(root)
    now = given["routes"] or routes_before
    found, was = agents(given, before, routes_before)
    said = [steps_written(root, agent, was) for agent in found]
    # A subagent written above says each sentence in the current wording, so is reworded in none.
    said += reworded_in(root, before, routes_before)
    laid_now = {a["name"]: a for a in read_before(root)["subagents"]}
    for agent in given["subagents"]:
        lanes_of = [{"step": s["step"], "lanes": s["lanes"]} for s in agent["steps"]]
        named = {k: agent[k] for k in ("adapter", "results") if k in agent}
        laid_now[agent["name"]] = {"name": agent["name"], **named, "steps": lanes_of}
    kept = {n: a for n, a in laid_now.items() if step.agent_file(root, n) is not None}
    hooked = checked(root, list(kept), now)
    entries.written(root, entries.put(hooks, plugin, [n for n in hooked if n not in skills(now)]))
    said.append(f"Wrote the checks of {routes.listed(hooked)} into hooks/hooks.json.\n")
    rules.write(root, list(kept.values()), now)
    what = "the lanes laid and the routes" if now else "the lanes laid"
    said.append(f"Wrote {what} into hooks/lanes.json.\n")
    # An adapter two lanes name is written and removed once.
    each = [a for agent in given["subagents"] for a in agent["adapters"]]
    adapters = list({a["path"]: a for a in each}.values())
    for a in adapters:
        os.makedirs(os.path.join(root, "hooks", "adapters"), exist_ok=True)
        shutil.copyfile(a["source"], os.path.join(root, a["path"]))
        shutil.copyfile(a["cases"], os.path.splitext(os.path.join(root, a["path"]))[0] + ".json")
        said.append(f"Wrote the adapter {a['path']} with its cases.\n")
    placed.code_put(root)
    said.append("Put lane's code in hooks/lane/.\n")
    validated(root, path)
    os.remove(path)
    said += ["claude plugin validate passed.\n", f"Removed the proposal {path}.\n"]
    for a in adapters:
        for file in (a["source"], a["cases"]):
            os.remove(file)
        said.append(f"Removed the adapter {a['source']} and its cases.\n")
    folder = os.path.dirname(os.path.abspath(path))
    for place in (
        os.path.join(folder, given["name"], "adapters"),
        os.path.join(folder, given["name"]),
        folder,
    ):
        if os.path.isdir(place) and not os.listdir(place):
            os.rmdir(place)
            # The folder is in the places as itself, so `is` finds it as `==`; the places under
            # it sort after it.
            if place == folder:  # pragma: no mutate
                said.append(f"Removed its folder {folder}.\n")
    return "".join(said)


def checked(root: str, laid: list[str], now: dict[str, Any] | None) -> list[str]:
    """The names the plugin's checks hold: each subagent of the names laid, then the skill and each
    subagent of the routes, each whose file is there."""
    named = routes.named(now) if now else []
    there = [n for n in named if n in skills(now) and step.skill_file(root, n)]
    there += [n for n in named if step.agent_file(root, n)]
    return list(dict.fromkeys([*laid, *[n for n in named if n in there]]))


def steps_written(root: str, agent: dict[str, Any], before: dict[str, Any]) -> str:
    """Writes each step lay.py writes in the subagent into its file, as `steps.steps_laid` gives
    them; gives what was written, said."""
    lines = agent["lines"]
    laid = steps.steps_laid(before, agent)
    # Each step is put back where it is, from the last, so a step of more lines than before leaves
    # where the earlier ones are as it was.
    # read_as_laid gives as many lines as it is given, so the order changes nothing yet.
    for s in sorted(laid, key=lambda s: s["span"], reverse=True):  # pragma: no mutate
        start, end = s["span"]
        lines[start:end] = steps.read_as_laid(lines, s)
    with open(agent["file"], "w", encoding="utf-8") as f:
        f.write("".join(lines))
    numbers = [str(n) for n in sorted(s["step"] for s in laid)]
    # A subagent lay.py writes has one step or more, so its first is its only where it has one.
    many = len(numbers) > 1  # pragma: no mutate
    first = numbers[0]  # pragma: no mutate
    which = f"steps {routes.listed(numbers)}" if many else f"step {first}"
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


def reworded_in(
    root: str, before: dict[str, list[dict[str, Any]]], routes_before: dict[str, Any] | None
) -> list[str]:
    """Writes each step of the plugin that says a sentence laid before, a lane's or the routes', in
    a wording lane laid before, with that sentence in the current one, as `steps.reworded` gives
    it, every other line as it was; gives what was written, a line for each step."""
    results = {a["name"]: a.get("results") for a in read_before(root)["subagents"]}
    named = routes.named(routes_before) if routes_before else []
    said = []
    for name in dict.fromkeys([*before, *named]):
        file = step.steps_file(root, name, name in skills(routes_before))
        if file is None or not os.path.isfile(file):
            continue
        with open(file, encoding="utf-8") as f:
            lines = f.readlines()
        bare = [line.rstrip("\n") for line in lines]
        laid = before.get(name, [])
        shown = os.path.relpath(file, root)
        written_now = []
        for s in merged(laid, routed(routes_before, name, lines, laid, results.get(name))):
            where = step.span(bare, s["step"])
            if where is None:
                continue
            now = steps.reworded(lines, {**s, "span": where})
            if now != lines[where[0] : where[1]]:
                lines[where[0] : where[1]] = now
                written_now.append(
                    f"Wrote step {s['step']} of {name} into {shown}, its sentences in lane's"
                    " current wording.\n"
                )
        if written_now:
            with open(file, "w", encoding="utf-8") as f:
                f.write("".join(lines))
        said += written_now
    return said


def brought_up(root: str) -> str:
    """Brings up the plugin's copy of lane's code where it is older than lane, lane's hook entry to
    the current form wherever it is in another, every other entry as it was, and each sentence a
    step says in a wording lane laid before to the current one, the rest of each step as it was;
    gives what was done, and each lane laid before, for the user to keep in their proposal or
    leave out. Stops, bringing nothing up, where the folder holds no plugin's manifest."""
    if not os.path.isfile(os.path.join(root, ".claude-plugin", "plugin.json")):
        raise Stop(
            f"lay.py: {root} holds no .claude-plugin/plugin.json, so it is no plugin's folder;"
            " name the folder of the plugin to lay lanes on."
        )
    name = plugin_name(root)
    hooks = entries.read(root)
    before, routes_before = laid_before(root)
    said = []
    was = placed.older(root)
    if was is not None:
        placed.code_put(root)
        said.append(
            f"Brought lane's code in hooks/lane/ up from {was} to {placed.lane_version()}.\n"
        )
    laid = [n for n in before if step.agent_file(root, n) is not None]
    kept = checked(root, laid, routes_before)
    now = entries.put(hooks, name, [n for n in kept if n not in skills(routes_before)])
    if now != hooks:
        entries.written(root, now)
        said.append(f"Wrote the checks of {routes.listed(kept)} into hooks/hooks.json.\n")
    if not said:
        said.append("hooks/lane/ holds no older copy of lane's code.\n")
    said += reworded_in(root, before, routes_before)
    adapters = {a["name"]: a.get("adapter") for a in read_before(root)["subagents"]}
    for agent, laid in before.items():
        if adapters[agent]:
            said.append(f'Laid before on {agent}: {{"adapter": "{adapters[agent]}"}}\n')
        for s in laid:
            for lane in s["lanes"]:
                sentence = lanes.sentence(lane["lane"], lane["takes"])
                held = step.holds(root, agent, s["step"], sentence)
                gone = "" if held else f', whose step no longer says "{sentence}"'
                said.append(
                    f"Laid before on step {s['step']} of {agent}{gone}: {json.dumps(lane)}\n"
                )
    return "".join(said)
