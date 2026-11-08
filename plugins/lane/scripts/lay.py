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
import proposal
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
    roles: list[laid.Role]
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


def _parts(checked: proposal.Checked) -> list[_Part]:
    """Each part of the proposal's roles, with its text as `lay.py write` lays it."""
    before = _laid_before(checked.root)
    found: dict[str, _Part] = {}
    for role in checked.laid.roles:
        part = checked.parts[role.name]
        if part.path in found:
            found[part.path].roles.append(role)
            continue
        adds: dict[int, list[str]] = {}
        drops: dict[int, list[str]] = {}
        for lane in role.lanes:
            adds.setdefault(lane.step, []).append(lanes.sentence(lane.lane, list(lane.takes)))
            drops.setdefault(lane.step, []).extend(lanes.earlier(lane.lane, list(lane.takes)))
        old = before.role(role.name) if before else None
        for lane in old.lanes if old else ():
            takes = list(lane.takes)
            said = [lanes.sentence(lane.lane, takes), *lanes.earlier(lane.lane, takes)]
            drops.setdefault(lane.step, []).extend(said)
        text = sentences.said(part.text, part.steps, adds, drops) if part.steps else part.text
        found[part.path] = _Part(part, [role], text)
    return list(found.values())


def _commands(role: laid.Role) -> list[str]:
    """Each command that the role may run, as its lanes write it."""
    found = []
    for lane in role.lanes:
        where = lanes.commands_place(lane.lane)
        if where:
            found += lanes.placed(lane.lane, list(lane.takes))[where]
    return list(dict.fromkeys(found))


def _show(checked: proposal.Checked, out: IO[str]) -> None:
    """Shows each role's steps as `lay.py write` would lay them."""
    out.write(
        f"{checked.manifest.name}: the lanes of {checked.root}, as lay.py write would lay them\n"
    )
    for each in _parts(checked):
        for role in each.roles:
            out.write("\n" + _shown(checked.root, role, each))


def _shown(root: str, role: laid.Role, each: _Part) -> str:
    """What `print` shows of the role, from its part as `lay.py write` lays it."""
    where = os.path.relpath(each.part.path, root)
    if not each.part.steps:
        said = [lanes.sentence(lane.lane, list(lane.takes)) for lane in role.lanes]
        return (
            f"{role.name}, in {where}, which holds no numbered list, so {role.name} is given"
            " these as it starts:\n" + "".join(f"- {s}\n" for s in said)
        )
    lines = [f"{role.name}, in {where}"]
    commands = _commands(role)
    if any(lane.lane == "run_only" for lane in role.lanes):
        lines.append("commands: " + ", ".join(f"`{c}`" for c in commands))
        for item in step.numbered(each.text):
            for span in dict.fromkeys(SPAN.findall(item.says)):
                if " " in span and not any(
                    c == span or c.endswith((" " + span, "/" + span)) for c in commands
                ):
                    lines.append(
                        f"step {item.number} names `{span}`, which {role.name} may not run"
                    )
    lines += [f"{item.number}. {item.says}" for item in step.numbered(each.text)]
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
    held = tuple(f"{checked.manifest.name}:{r.name}" for r in checked.laid.roles)
    existing = _json(os.path.join(hooks, "hooks.json"))
    _save(os.path.join(hooks, "hooks.json"), entries.merged(existing, checked.manifest.name, held))
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
