#!/usr/bin/env python3
"""Decides the steps and rules that hold a start of the generator or an evaluator, from the Cut
that its prompt names: what it writes and never reads, the items of each step's checklist, its
check, and the results that end it."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import Wrong, end
from schemas import form
from tree import rounds

# The path of a Cut of a run's Round, as scripts/cut.py prints it for the start's prompt.
CUT = re.compile(r"\S*\.rn/[^/\s]+/rounds/\d+/[^/\s]+\.cut\.json")

# The rules of a step that writes nothing.
NOTHING = [{"type": "writes", "paths": []}]


def main(given: str, cwd: str, plugin: str) -> tuple[int, str, str]:
    """Gives Lane the steps of a start, as Lane runs this adapter for each start of a role that
    lane/rules.json names with no steps.

    Takes: the run, the start's role, and its prompt, on standard input in the form of Lane's
    rules.in.schema.json; the folder of the run's worktree; and rn's folder.
    Gives: 0 with `{"steps": [...]}`, in the form of Lane's rules.out.schema.json, the steps of
    `domain/generator.md` or `domain/evaluator.md` by their numbers, each with `order`, and, from
    the Cut that the prompt names, its result beside it at `<role>[-<group>].json`:
    - for `rn:generator`: at step 1, `writes` of no path; at step 2, a `checklist` of each
      `N<n>.<m>` of the Cut's best practice that its maker takes while deciding, the m-th practice
      of the condition N<n>, `writes` of the result alone, and a `result` that `ends` on `point`;
      at step 3, a `checklist` of each that its maker takes while making, and `writes` of the
      deliverable's path and the result; at step 4, `writes` of the result, the `check`
      `python3 <rn>/scripts/check.py generator <Cut>`, and a `result` of `made`;
    - for `rn:evaluator`: at step 1, `writes` of no path; at step 2, `reads_none` of the run's
      design-tree.json and of each generator's Cut of the Round, in any slot, with the result
      beside it, and no `writes`, as its trial writes what its people's use writes; at step 3, a
      `checklist` of the ID of each condition of its Cut and `writes` of no path; at step 4,
      `writes` of the result, the `check` `python3 <rn>/scripts/check.py evaluator <Cut>`, and a
      `result` of `judged`.
    1 with what Wrong says, such as Lane's input out of its form, a prompt that names no Cut of a
    run's Round, a Cut out of its form, a Cut or a result of its Round that isn't JSON, or a Cut
    that names no best practice of rn's.
    Changes: nothing.
    Refuses: nothing beyond the exit codes above."""
    try:
        cut = _cut(given)
        held = form.read(
            os.path.join(cwd, cut),
            os.path.join(plugin, "domain", "schemas", "cut.schema.json"),
            cut,
        )
        steps = (
            _generator(held, cut, plugin)
            if held["role"] == "generator"
            else _evaluator(held, cut, cwd, plugin)
        )
    except Wrong as wrong:
        return 1, "", f"rules.py: {wrong}\n"
    return 0, json.dumps({"steps": steps}) + "\n", ""


def _cut(given: str) -> str:
    """The path of the Cut that the prompt of Lane's input names; Wrong where the input leaves its
    form or the prompt names none."""
    try:
        value: Any = json.loads(given)
    except ValueError as error:
        raise Wrong(f"Lane's input isn't JSON: {error}") from None
    if not isinstance(value, dict) or not isinstance(value.get("prompt"), str):
        raise Wrong("Lane's input takes the form of rules.in.schema.json, with the start's prompt")
    found = CUT.search(value["prompt"])
    if found is None:
        raise Wrong(
            f"the start's prompt names no Cut of a run's Round, such as"
            f" .rn/<run>/rounds/<n>/generator.cut.json: {value['prompt']!r}"
        )
    return found.group()


def _practices(held: dict[str, Any], cut: str, plugin: str) -> dict[str, list[str]]:
    """Each practice of the best practice of the Cut at `cut`, by when its maker takes it, decide
    or make, as N<n>.<m>, the m-th practice of the condition N<n>, read once for both steps; Wrong
    where rn has no such best practice."""
    name = held["best_practice"]
    practices = os.path.join(plugin, "domain", "best-practices")
    path = os.path.join(practices, name, "best-practice.json")
    if not os.path.isfile(path):
        raise Wrong(
            f"{cut}: best_practice: rn has no best practice {name}, only a folder of {practices}"
        )
    with open(path, encoding="utf-8") as f:
        factors = json.load(f)["goal"]["critical_success_factors"]
    taken: dict[str, list[str]] = {"decide": [], "make": []}
    for condition in (n for c in factors for n in c["necessary_conditions"]):
        for m, item in enumerate(condition["items"], 1):
            taken[item["at"]].append(f"{condition['id']}.{m}")
    return taken


def _steps(*rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Steps 1 onward of the role's prompt, each with order before its own rules."""
    return [
        {"name": str(n), "rules": [{"type": "order"}, *each]} for n, each in enumerate(rules, 1)
    ]


def _end(role: str, cut: str, plugin: str, result: str) -> list[dict[str, Any]]:
    """The last step's rules: the writes of the result beside the Cut, rn's check of the role, and
    the result that the role gives."""
    check = os.path.join(os.path.normpath(plugin), "scripts", "check.py")
    return [
        {"type": "writes", "paths": [_result(cut)]},
        {"type": "check", "check": f"python3 {shlex.quote(check)} {role} {shlex.quote(cut)}"},
        {"type": "result", "results": [result]},
    ]


def _result(cut: str) -> str:
    """The path of the result beside the Cut."""
    return cut.removesuffix(".cut.json") + ".json"


def _generator(held: dict[str, Any], cut: str, plugin: str) -> list[dict[str, Any]]:
    """The generator's steps, from its Cut at `cut`."""
    taken = _practices(held, cut, plugin)
    return _steps(
        NOTHING,
        [
            {"type": "checklist", "items": taken["decide"]},
            {"type": "writes", "paths": [_result(cut)]},
            {"type": "result", "ends": ["point"]},
        ],
        [
            {"type": "checklist", "items": taken["make"]},
            {"type": "writes", "paths": [held["deliverable"]["path"], _result(cut)]},
        ],
        _end("generator", cut, plugin, "made"),
    )


def _evaluator(held: dict[str, Any], cut: str, cwd: str, plugin: str) -> list[dict[str, Any]]:
    """An evaluator's steps, from its Cut at `cut` in the worktree `cwd`."""
    run = os.path.dirname(os.path.dirname(os.path.dirname(cut)))
    round_ = os.path.dirname(cut) + "/"
    made = [rounds.path(run, s) for s in rounds.each(os.path.join(cwd, run))]
    makers = [m for m in made if m.startswith(round_ + "generator")]
    unread = [f"{run}/design-tree.json", *(p for m in makers for p in (m, _result(m)))]
    return _steps(
        NOTHING,
        [{"type": "reads_none", "paths": unread}],
        [{"type": "checklist", "items": held["conditions"]}, *NOTHING],
        _end("evaluator", cut, plugin, "judged"),
    )


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd(), os.path.join(HERE, "..", "..")))
