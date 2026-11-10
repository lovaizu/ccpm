"""lay.py shows the rules of a proposal as they'll read, and lays the rules that the user approved
into their plugin: each rule's sentence at the end of its step, the hook entries that run the
guard, the rules in hooks/lanes.json, and Lane's code. It alone decides whether a proposal can
stand, and what goes where in the plugin.

Run it as `python3 lay.py print <proposal>`, then `python3 lay.py write <proposal>`."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any

LANE_CODE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks", "lane"
)
sys.path.insert(0, LANE_CODE)  # pragma: no mutate

from domain import laid, steps
from domain.lanes import TYPES

USAGE = "usage: lay.py print <proposal>\n       lay.py write <proposal>"
ENTRY = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py" '
# A span of a step in backticks. print takes one that holds a blank for a command. A span of one
# word may be a file or a result, such as `CHANGELOG.md` or `more`, so print leaves it be.
SPAN = re.compile(r"`([^`]+)`")
PLACE = "keep the proposal as .lane/<yyyymmdd>-<plugin>/<plugin>.json at the root of the repository"


class Refused(Exception):
    """The proposal can't stand, for the reason the message gives."""


def _expect(value: Any, kind: type, where: str) -> Any:
    """The value, where it's of the kind. A value of any other kind, or true or false, which no
    field takes, refuses the proposal."""
    names = {list: "a list", dict: "an object", str: "a text", int: "a whole number"}
    if isinstance(value, bool) or not isinstance(value, kind):
        raise Refused(f"{where}: expected {names[kind]}, found {json.dumps(value)}")
    return value


def _role_file(plugin: str, name: str) -> tuple[str, str]:
    """The role's file under the plugin, and its text. A role with no file, or one that doesn't
    run in the background, refuses the proposal."""
    relative = f"agents/{name}.md"
    try:
        with open(os.path.join(plugin, relative), encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise Refused(f"{relative} isn't there") from None
    front = text.split("---")[1] if text.startswith("---") else ""
    if "background: true" not in front.split("\n"):
        raise Refused(
            f"{relative} doesn't set `background: true`, as Lane holds only a role run in the"
            " background"
        )
    return relative, text


def parse(path: str) -> tuple[str, str, dict[str, Any]]:
    """The repository's root, the plugin's folder, and the proposal at the path, held to its form
    and to the plugin's files. Raises Refused where it can't stand."""
    folder = os.path.dirname(os.path.abspath(path))
    if os.path.basename(os.path.dirname(folder)) != ".lane":
        raise Refused(PLACE)
    root = os.path.dirname(os.path.dirname(folder))
    try:
        with open(path, encoding="utf-8") as f:
            proposal = json.load(f)
    except FileNotFoundError:
        raise Refused("it isn't there") from None
    except ValueError:
        raise Refused("it isn't JSON") from None
    _expect(proposal, dict, "$")
    name = _expect(proposal.get("plugin"), str, "$.plugin")
    plugin = os.path.join(root, name)
    if not os.path.isfile(os.path.join(plugin, ".claude-plugin", "plugin.json")):
        raise Refused(f"{name}/.claude-plugin/plugin.json isn't there")
    for r, role in enumerate(_expect(proposal.get("subagents"), list, "$.subagents")):
        where = f"$.subagents[{r}]"
        _expect(role, dict, where)
        role_name = _expect(role.get("name"), str, f"{where}.name")
        relative, text = _role_file(plugin, role_name)
        held = _expect(role.get("steps"), list, f"{where}.steps")
        if not held:
            raise Refused(f"{where}.steps: expected at least one step")
        for s, step in enumerate(held):
            _expect(step, dict, f"{where}.steps[{s}]")
            number = _expect(step.get("step"), int, f"{where}.steps[{s}].step")
            try:
                steps.laid(text, number, "", [])
            except steps.StepsError as error:
                raise Refused(f"{relative}: {error}") from None
            lanes = _expect(step.get("lanes"), list, f"{where}.steps[{s}].lanes")
            if not lanes:
                raise Refused(f"{where}.steps[{s}].lanes: expected at least one lane")
            for k, lane in enumerate(lanes):
                at = f"{where}.steps[{s}].lanes[{k}]"
                _expect(lane, dict, at)
                kind = _expect(lane.get("lane"), str, f"{at}.lane")
                takes = _expect(lane.get("takes"), list, f"{at}.takes")
                for t, each in enumerate(takes):
                    _expect(each, str, f"{at}.takes[{t}]")
                if kind not in TYPES:
                    known = ", ".join(TYPES)
                    raise Refused(
                        f"{role_name} step {number}: no type {kind}; the types are {known}"
                    )
                wrong = TYPES[kind].refused(takes)
                if wrong:
                    raise Refused(f"{role_name} step {number}: {wrong}")
    return root, plugin, proposal


def _sentences(lanes: list[dict[str, Any]]) -> list[str]:
    """The sentence of each rule, in order."""
    return [TYPES[lane["lane"]].sentence(lane["takes"]) for lane in lanes]


def _numbers(found: list[int]) -> str:
    """`step 2`, `steps 2 and 3`, or `steps 1, 2 and 3`."""
    *rest, last = [str(n) for n in found]
    if not rest:
        return f"step {last}"
    return f"steps {', '.join(rest)} and {last}"


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _laid(plugin: str, roles: dict[str, list[dict[str, Any]]]) -> dict[str, tuple[str, str]]:
    """Each role's file under the plugin, with its text as the rules lay it: each sentence at the
    end of its step, in place of the sentences that hooks/lanes.json says were laid before."""
    before = laid.read(os.path.join(plugin, "hooks"))
    texts = {}
    for name, held in roles.items():
        relative, text = _role_file(plugin, name)
        gone = []
        if isinstance(before, dict):
            for step in before["subagents"].get(name, {"steps": []})["steps"]:
                gone += _sentences(step["lanes"])
        for step in held:
            for sentence in _sentences(step["lanes"]):
                text = steps.laid(text, step["step"], sentence, gone)
        texts[name] = (relative, text)
    return texts


def _shown(name: str, held: list[dict[str, Any]], text: str) -> str:
    """What print shows of a role: a row for each rule and each command a step names that the
    role may not run, the commands it may run, and each step with a rule as it'll read."""
    rows: dict[int, list[tuple[str, str, str]]] = {}
    for step in held:
        for lane in step["lanes"]:
            kind = TYPES[lane["lane"]]
            rows.setdefault(step["step"], []).append(
                (f"{kind.ACTION}:", kind.sentence(lane["takes"]), lane["lane"])
            )
    commands = list(
        dict.fromkeys(each for step in held for lane in step["lanes"] for each in lane["takes"])
    )
    said = steps.read(text)
    numbers = max(len(f"step {number}") for number in [*said, *rows])
    actions = max(len(row[0]) for each in rows.values() for row in each)
    sentences = max(len(row[1]) for each in rows.values() for row in each)
    lines = [f"Lanes of {name}, each checked only in {name}:"]
    for number in sorted({*said, *rows}):
        at = f"step {number}".ljust(numbers)
        lines += [
            f"  {at}  {action.ljust(actions)} {sentence.ljust(sentences)}  type {kind}"
            for action, sentence, kind in rows.get(number, [])
        ]
        lines += [
            f"  {at}  names `{span}`, which {name} may not run"
            for span in dict.fromkeys(SPAN.findall(said.get(number, "")))
            if " " in span and span not in commands
        ]
    *rest, last = [f"`{command}`" for command in commands]
    named = f"{', '.join(rest)} or {last}" if rest else last
    lines += [f"  commands: {name} may run only {named}", ""]
    lines += [f"{number}. {said[number]}" for number in sorted(rows)]
    return "\n".join(lines) + "\n"


def show(path: str) -> int:
    """Shows the proposal at the path as write would lay it, and writes nothing. Gives 1 where it
    can't stand."""
    try:
        _, plugin, proposal = parse(path)
    except Refused as refused:
        print(f"lay.py: {path}: {refused}", file=sys.stderr)
        return 1
    roles = {role["name"]: role["steps"] for role in proposal["subagents"]}
    texts = _laid(plugin, roles)
    print("\n".join(_shown(name, held, texts[name][1]) for name, held in roles.items()), end="")
    return 0


def write(path: str) -> int:
    """Lays the proposal at the path, and says what it did. Gives 1 where it can't stand or the
    plugin doesn't pass claude plugin validate."""
    try:
        root, plugin, proposal = parse(path)
    except Refused as refused:
        print(f"lay.py: {path}: {refused}", file=sys.stderr)
        return 1
    hooks = os.path.join(plugin, "hooks")
    roles = {role["name"]: role["steps"] for role in proposal["subagents"]}
    for name, (relative, text) in _laid(plugin, roles).items():
        _write(os.path.join(plugin, relative), text)
        print(
            f"Wrote {_numbers([step['step'] for step in roles[name]])} of {name} into {relative}."
        )

    entries_path = os.path.join(hooks, "hooks.json")
    try:
        with open(entries_path, encoding="utf-8") as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = {"hooks": {}}
    own = [
        entry
        for entry in entries["hooks"].get("PreToolUse", [])
        if not any(
            "/hooks/lane/hook.py" in each.get("command", "") for each in entry.get("hooks", [])
        )
    ]
    guard = {"matcher": "*", "hooks": [{"type": "command", "command": ENTRY + proposal["plugin"]}]}
    entries["hooks"]["PreToolUse"] = [*own, guard]
    _write(entries_path, json.dumps(entries, indent=2) + "\n")
    print(f"Wrote the checks of {' and '.join(roles)} into hooks/hooks.json.")
    _write(
        os.path.join(hooks, "lanes.json"),
        json.dumps(laid.laid(proposal["plugin"], roles), indent=2) + "\n",
    )
    print("Wrote the lanes laid into hooks/lanes.json.")
    code = os.path.join(hooks, "lane")
    if os.path.isdir(code):
        shutil.rmtree(code)
    shutil.copytree(LANE_CODE, code, ignore=shutil.ignore_patterns("__pycache__"))
    print("Put lane's code in hooks/lane/.")

    try:
        validated = subprocess.run(
            ["claude", "plugin", "validate", plugin], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        print(
            "claude plugin validate couldn't run, as claude isn't on PATH. Install Claude Code,"
            " and run lay.py write again."
        )
        return 1
    if validated.returncode != 0:
        print(validated.stdout + validated.stderr, end="")
        print("Fix what claude plugin validate found, and run lay.py write again.")
        return 1
    print("claude plugin validate passed.")
    os.remove(path)
    print(f"Removed the proposal {os.path.relpath(os.path.abspath(path), root)}.")
    folder = os.path.dirname(os.path.abspath(path))
    if not os.listdir(folder):
        os.rmdir(folder)
        print(f"Removed its folder {folder}.")
    return 0


def main(argv: list[str]) -> int:
    """Runs the command that argv names."""
    command = COMMANDS.get(argv[1]) if len(argv) == 3 else None
    if command:
        return command(argv[2])
    print(USAGE, file=sys.stderr)
    return 2


COMMANDS = {"print": show, "write": write}

if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv))
