"""Decides which files laying a Proposal writes or replaces in the user's plugin, as one change:
each laid sentence in its Step, Lane's hook entries in `hooks/hooks.json` beside the user's own,
`hooks/lanes.json`, and `hooks/lane/`, a copy of Lane's code, after which `claude plugin validate`
must pass, or every file goes back as it was, as the principle Lane's part replaced whole says."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Callable

from domain.laid_set import Laid, LaidSentence, LaidSet, Lane, dumps, load
from proposal import Proposal, role_order
from shown import reads
from steps import Role, Step

# The command of each of Lane's hook entries, which runs the plugin's own copy of the guard.
_GUARD = ["${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py"]
# The events of Lane's hook entries, each with whether a failure of its hook stops the event, as
# Stop and SubagentStop take no onFailure.
_EVENTS = (
    ("UserPromptExpansion", True),
    ("UserPromptSubmit", True),
    ("PreToolUse", True),
    ("PostToolUse", True),
    ("Stop", False),
    ("SubagentStop", False),
)


@dataclass(frozen=True)
class Laying:
    """What laying wrote: each line that `lay.py write` prints, such as `Wrote step 1 of write into
    skills/write/SKILL.md.`, or, where `claude plugin validate` failed, what it said."""

    lines: tuple[str, ...]
    validated: bool


def hook_entries(plugin_root: str) -> dict[str, list[dict[str, object]]]:
    """Lane's hook entries for the plugin, by event, each running the copy of the guard in the
    plugin's own `hooks/lane/`, as the principle The laid plugin runs alone says."""
    entries: dict[str, list[dict[str, object]]] = {}
    for event, blocks in _EVENTS:
        entry: dict[str, object] = {"type": "command", "command": "python3", "args": list(_GUARD)}
        if blocks:
            entry["onFailure"] = "block"
        entries[event] = [{"hooks": [entry]}]
    return entries


def _command(entry: dict[str, Any]) -> str:
    return " ".join([entry["command"], *entry.get("args", [])])


def lay(
    proposal: Proposal,
    found: Sequence[Role],
    plugin_root: str,
    lane_code: str,
    validate: Callable[[str], tuple[bool, str]],
) -> Laying:
    """Lays the Proposal into the plugin in the folder: takes out of each Step and each hook entry
    what the plugin's Laid names, writes each Lane's sentence where its Step doesn't say it
    already, Lane's hook entries, `hooks/lanes.json` with the new Laid as the guard's
    `laid_set.dumps` gives it, and a copy of the folder `lane_code` as `hooks/lane/`, and then runs
    `validate` on the plugin's folder. Where it fails, it puts back each file it changed. Leaves
    every other file of the plugin as it stands."""
    before = load(plugin_root)
    old = before.laid if before else Laid()
    hooks = os.path.join(plugin_root, "hooks")
    had_hooks = os.path.isdir(hooks)
    steps = _laid_steps(proposal, found)
    unheld = [s for role in found for s in role.steps if all(s is not each for each, _ in steps)]
    files = sorted(
        {step.file for role in found for step in role.steps}
        | {"hooks/hooks.json", "hooks/lanes.json"}
    )
    saved = {f: _read(os.path.join(plugin_root, f)) for f in files}
    backup = tempfile.mkdtemp()
    code = os.path.join(hooks, "lane")
    try:
        if os.path.isdir(code):
            shutil.move(code, os.path.join(backup, "lane"))
        lines, laid = _write_steps(plugin_root, steps)
        for step in unheld:
            _write_step(plugin_root, step, step.words)
        lines.append(_write_hooks(plugin_root, proposal, old))
        lines.append(_write_lanes(plugin_root, proposal, laid))
        shutil.copytree(lane_code, code, ignore=shutil.ignore_patterns("__pycache__"))
        lines.append("Put lane's code in hooks/lane/.")
        passed, said = validate(plugin_root)
        if passed:
            return Laying((*lines, "claude plugin validate passed."), True)
        _put_back(plugin_root, saved, backup, had_hooks)
        return Laying((said,), False)
    finally:
        shutil.rmtree(backup)


def _read(path: str) -> str | None:
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _put_back(plugin_root: str, saved: dict[str, str | None], backup: str, had_hooks: bool) -> None:
    """Puts back each file as it was before laying, and hooks/ as it was."""
    for file, text in saved.items():
        path = os.path.join(plugin_root, file)
        if text is None and os.path.exists(path):
            os.remove(path)
        elif text is not None:
            _write(path, text)
    code = os.path.join(plugin_root, "hooks", "lane")
    shutil.rmtree(code, ignore_errors=True)
    if os.path.isdir(os.path.join(backup, "lane")):
        shutil.move(os.path.join(backup, "lane"), code)
    if not had_hooks:
        shutil.rmtree(os.path.join(plugin_root, "hooks"))


def _laid_steps(proposal: Proposal, found: Sequence[Role]) -> list[tuple[Step, list[Lane]]]:
    """Each Step that a Lane lies on, with its Lanes, by the Proposal's order of roles."""
    by_name = {role.name: role for role in found}
    laid = []
    for name in role_order(proposal):
        for step in by_name[name].steps:
            lanes = [
                lane for lane in proposal.lanes if (lane.role, lane.step) == (name, step.number)
            ]
            if lanes:
                laid.append((step, lanes))
    return laid


def _write_steps(
    plugin_root: str, steps: Sequence[tuple[Step, list[Lane]]]
) -> tuple[list[str], list[LaidSentence]]:
    """Writes each Step as it reads once laid, and gives a `Wrote` line for each role's file, with
    each sentence laid."""
    laid: list[LaidSentence] = []
    wrote: dict[tuple[str, str], list[int]] = {}
    for step, lanes in steps:
        follows = step.words
        for lane in lanes:
            if lane.sentence not in follows:
                laid.append(LaidSentence(step.file, follows, lane.sentence))
                follows = f"{follows} {lane.sentence}"
        _write_step(plugin_root, step, reads(step, [lane.sentence for lane in lanes]))
        wrote.setdefault((step.role, step.file), []).append(step.number)
    lines = [
        f"Wrote {_numbers(numbers)} of {role} into {file}."
        for (role, file), numbers in wrote.items()
    ]
    return lines, laid


def _numbers(numbers: Sequence[int]) -> str:
    if len(numbers) == 1:
        return f"step {numbers[0]}"
    return "steps " + _joined([str(n) for n in numbers])


def _joined(words: Sequence[str]) -> str:
    return ", ".join(words[:-1]) + f" and {words[-1]}" if len(words) > 1 else words[0]


def _write_step(plugin_root: str, step: Step, laid: str) -> None:
    """Writes the Step's line in its file as it reads once laid."""
    path = os.path.join(plugin_root, step.file)
    text = _read(path) or ""
    lines = text.split("\n")
    place = next(n for n, line in enumerate(lines) if line.startswith(step.words))
    lines[place] = laid
    _write(path, "\n".join(lines))


def _write_hooks(plugin_root: str, proposal: Proposal, old: Laid) -> str:
    """Writes Lane's hook entries into hooks/hooks.json in place of those it laid before, beside
    the user's own, and gives its `Wrote` line."""
    path = os.path.join(plugin_root, "hooks", "hooks.json")
    given = json.loads(_read(path) or '{"hooks": {}}')
    hooks: dict[str, list[dict[str, Any]]] = given.setdefault("hooks", {})
    for event in list(hooks):
        kept = []
        for group in hooks[event]:
            own = [e for e in group.get("hooks", []) if (event, _command(e)) not in old.hooks]
            if own:
                kept.append(dict(group, hooks=own))
        hooks[event] = kept
    for event, groups in hook_entries(plugin_root).items():
        hooks[event] = [*hooks.get(event, []), *groups]
    _write(path, json.dumps(given, indent=2) + "\n")
    return f"Wrote the checks of {_joined(role_order(proposal))} into hooks/hooks.json."


def _write_lanes(plugin_root: str, proposal: Proposal, laid: list[LaidSentence]) -> str:
    """Writes hooks/lanes.json, and gives its `Wrote` line."""
    laid_set = LaidSet(
        plugin=proposal.plugin,
        skills=proposal.skills,
        roles=tuple(role_order(proposal)),
        lanes=proposal.lanes,
        routes=proposal.routes,
        text_adapter=proposal.text_adapter,
        results_adapter=proposal.results_adapter,
        laid=Laid(
            tuple(laid),
            tuple((event, " ".join(["python3", *_GUARD])) for event, _ in _EVENTS),
        ),
    )
    _write(os.path.join(plugin_root, "hooks", "lanes.json"), dumps(laid_set))
    return "Wrote the lanes laid and the routes into hooks/lanes.json."
