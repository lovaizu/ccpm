"""Lane's command, which the user runs on their own computer. It decides what goes where in the
user's plugin. No other part of Lane writes there.

- `lay.py print <proposal>` shows each step of the proposal as it'll read once laid, and exits 1
  with what's wrong where the proposal can't stand.
- `lay.py write <proposal>` lays a proposal that `print` would show: the sentences into the steps,
  `hooks/lanes.json`, `hooks/hooks.json`, and Lane's code. It has `claude plugin validate` check
  the plugin, and removes the proposal's folder once the check passes.
- `lay.py up <plugin folder>` brings the plugin's copy of Lane's code, its hook entries, and the
  sentences in its steps to this version of Lane.

Exit codes: 0 when done, 1 when the proposal or the plugin is wrong, and 2 when the command is.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from typing import IO, NamedTuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "hooks", "lane", "domain")]

import entries
import laid
import lane_code
import lanes
import plugin
import proposal
import routes
import sentences
import step

USAGE = (
    "lay.py: run it as `lay.py print <proposal>`, `lay.py write <proposal>` or"
    " `lay.py up <plugin folder>`"
)
# A span of a step in backticks.
SPAN = re.compile(r"`([^`]+)`")


class _Part(NamedTuple):
    """A part's text as `lay.py write` lays it, and the roles whose steps it holds."""

    part: step.Part
    names: list[str]
    text: str


def main(argv: list[str], out: IO[str], err: IO[str], lane: str) -> int:
    """Runs the command in argv with Lane at the folder given, and gives the exit code. It writes
    what it shows to out, and what's wrong to err."""
    if len(argv) != 3 or argv[1] not in ("print", "write"):
        err.write(USAGE + "\n")
        return 2
    try:
        checked = proposal.checked(argv[2])
    except proposal.Refused as refused:
        err.write("".join(f"lay.py: {f}\n" for f in refused.faults))
        return 1
    if argv[1] == "print":
        _show(checked, out)
        return 0
    return _write(checked, out, err, lane)


def _laid_before(root: str) -> laid.Laid | None:
    """The lanes laid in the plugin before, or None where `lay.py` can read none."""
    try:
        return laid.read(root)
    except laid.Unlaid:
        return None


def _names(checked: proposal.Checked, before: laid.Laid | None) -> list[tuple[str, step.Part]]:
    """The skill that the routes name, then each role with lanes or named by the routes, each with
    its part. The names of the lanes laid before follow, where the proposal gives them no more and
    their parts are still there, so that their sentences come out."""
    given = checked.laid.routes
    found = [(given.orchestrator, checked.skill)] if given is not None and checked.skill else []
    found += list(checked.parts.items())
    if before is None:
        return found
    names = {n for n, _ in found}
    old = [r.name for r in before.roles]
    if before.routes is not None:
        old += routes.named(before.routes)
        skill = before.routes.orchestrator
        if skill not in names:
            try:
                found.append((skill, step.part(checked.root, plugin.skill(checked.root, skill))))
            except plugin.Fault:
                pass
            names.add(skill)
    for name in dict.fromkeys(n for n in old if ":" not in n and n not in names):
        try:
            found.append((name, step.part(checked.root, plugin.subagent(checked.root, name))))
        except plugin.Fault:
            continue
    return found


def _parts(checked: proposal.Checked) -> list[_Part]:
    """Each part of the skill and the roles, with its text as `lay.py write` lays it."""
    before = _laid_before(checked.root)
    found: dict[str, _Part] = {}
    for name, part in _names(checked, before):
        if part.path in found:
            found[part.path].names.append(name)
            continue
        adds: dict[int, list[str]] = {}
        drops: dict[int, list[str]] = {}
        for each in laid.sentences(checked.laid, name, part.steps):
            if each.step is not None:
                adds.setdefault(each.step, []).append(lanes.sentence(each.lane, each.takes))
                drops.setdefault(each.step, []).extend(lanes.earlier(each.lane, each.takes))
        for each in laid.sentences(before, name, part.steps) if before else []:
            if each.step is not None:
                said = [
                    lanes.sentence(each.lane, each.takes),
                    *lanes.earlier(each.lane, each.takes),
                ]
                drops.setdefault(each.step, []).extend(said)
        text = sentences.said(part.text, part.steps, adds, drops) if part.steps else part.text
        found[part.path] = _Part(part, [name], text)
    return list(found.values())


def _commands(said: list[laid.Said]) -> list[str]:
    """Each command that the sentences let a role run, as they write it."""
    found = []
    for each in said:
        where = lanes.commands_place(each.lane)
        if where:
            found += lanes.placed(each.lane, each.takes)[where]
    return list(dict.fromkeys(found))


def _show(checked: proposal.Checked, out: IO[str]) -> None:
    """Shows the routes, and each step as `lay.py write` would lay it."""
    out.write(
        f"{checked.manifest.name}: the lanes of {checked.root}, as lay.py write would lay them\n"
    )
    if checked.laid.routes is not None:
        out.write("\n" + _routes_shown(checked.laid.routes))
    for each in _parts(checked):
        for name in each.names:
            said = laid.sentences(checked.laid, name, each.part.steps)
            out.write("\n" + _shown(checked, name, said, each))
    for path, adapter in checked.adapters.items():
        out.write(f"\nadapter {path}\n")
        for given, gave in adapter.tried:
            out.write(f"- given {json.dumps(given)}\n  gives {json.dumps(gave)}\n")


def _routes_shown(given: routes.Routes) -> str:
    """The routes, a line for each, and how the starts at once and their texts go."""
    lines = [f"routes of {given.orchestrator}"]
    for route in given.routes:
        if route.on is None:
            lines.append(f"- {route.source} starts {route.to}")
        elif route.to:
            lines.append(f"- {route.source} gives `{route.on}`: start {route.to}")
        elif route.waits:
            lines.append(f"- {route.source} gives `{route.on}`: the run waits for the person")
        else:
            lines.append(f"- {route.source} gives `{route.on}`: the run ends")
    for role in given.fan_out:
        lines.append(f"- {role} may run several times at once")
    if given.precedence is not None:
        lines.append(
            f"- the results of starts at once, first to last: {json.dumps(given.precedence)}"
        )
    if given.command:
        lines.append(f"- each start's text: what `{given.command} <name>` prints for it")
    return "\n".join(lines) + "\n"


def _shown(checked: proposal.Checked, name: str, said: list[laid.Said], each: _Part) -> str:
    """What `print` shows of the role or the skill of the name, from its part as `lay.py write`
    lays it."""
    where = os.path.relpath(each.part.path, checked.root)
    told = [s for s in said if s.step is None or not each.part.steps]
    lines = [f"{name}, in {where}"]
    role = checked.laid.role(name)
    commands = _commands(said)
    if role is not None and any(lane.lane == "run_only" for lane in role.lanes):
        lines.append("commands: " + ", ".join(f"`{c}`" for c in commands))
        for item in step.numbered(each.text):
            for span in dict.fromkeys(SPAN.findall(item.says)):
                if " " in span and not any(
                    c == span or c.endswith((" " + span, "/" + span)) for c in commands
                ):
                    lines.append(f"step {item.number} names `{span}`, which {name} may not run")
    lines += [f"{item.number}. {item.says}" for item in step.numbered(each.text)]
    if told:
        whom = (
            "the main conversation is told"
            if role is None and checked.skill
            else f"{name} is given"
        )
        lines.append(f"{whom} these as it starts, as no step says them:")
        lines += [f"- {lanes.sentence(s.lane, s.takes)}" for s in told]
    return "\n".join(lines) + "\n"


def _write(checked: proposal.Checked, out: IO[str], err: IO[str], lane: str) -> int:
    """Lays the proposal into the plugin, and gives the exit code. It has Claude Code check the
    plugin, and removes the proposal once the check passes."""
    root = checked.root
    wrote = []
    for each in _parts(checked):
        if each.text != each.part.text:
            with open(each.part.path, "w", encoding="utf-8") as f:
                f.write(each.text)
            wrote.append(f"{os.path.relpath(each.part.path, root)}, the sentences of its lanes")
    hooks = os.path.join(root, "hooks")
    os.makedirs(hooks, exist_ok=True)
    _save(os.path.join(hooks, "lanes.json"), checked.laid.data)
    names = [r.name for r in checked.laid.roles]
    if checked.laid.routes is not None:
        names += routes.named(checked.laid.routes)
    held = tuple(dict.fromkeys(routes.typed(checked.manifest.name, n) for n in names))
    existing = _json(os.path.join(hooks, "hooks.json"))
    _save(os.path.join(hooks, "hooks.json"), entries.merged(existing, checked.manifest.name, held))
    for path, adapter in checked.adapters.items():
        target = os.path.join(root, os.path.dirname(path))
        if os.path.realpath(adapter.folder) != os.path.realpath(target):
            os.makedirs(target, exist_ok=True)
            for name in (os.path.basename(path), os.path.basename(path)[: -len(".py")] + ".json"):
                shutil.copyfile(os.path.join(adapter.folder, name), os.path.join(target, name))
            wrote.append(f"{path} and its cases")
    code = lane_code.lay(lane, root)
    shown = (
        "a link to Lane's code"
        if code.kind == "link"
        else f"a copy of Lane's code at {code.version}"
    )
    wrote += ["hooks/lanes.json", "hooks/hooks.json", f"hooks/lane, {shown}"]
    out.write(
        f"{checked.manifest.name}: lay.py wrote into {root}:\n" + "".join(f"- {w}\n" for w in wrote)
    )
    again = f"run lay.py write {checked.path} again: the proposal is kept."
    try:
        done = subprocess.run(
            ["claude", "plugin", "validate", root], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        err.write(
            "lay.py: claude isn't on PATH, so claude plugin validate couldn't check the plugin."
            f" Install Claude Code, then {again}\n"
        )
        return 1
    if done.returncode != 0:
        found = (done.stdout + done.stderr).strip()
        err.write(
            f"lay.py: claude plugin validate found the plugin malformed:\n{found}\n"
            f"Fix it, then {again}\n"
        )
        return 1
    folder = os.path.dirname(checked.path)
    shutil.rmtree(folder)
    out.write(f"claude plugin validate passed it, so lay.py removed {folder}.\n")
    return 0


def _json(path: str) -> dict | None:
    """The JSON in the file, or None where the file isn't there."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def _save(path: str, data: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv, sys.stdout, sys.stderr, os.path.dirname(HERE)))
