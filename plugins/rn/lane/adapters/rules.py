"""Decides the steps of each turn of rn's orchestrator and of each start of its generator and
evaluator, and the rules of each step, as Lane asks them: the turn's event's own step and those
that every event shares, and for a role the files each step reads, writes, and never reads, the
commands it runs, the practices of its kind's best practice as its checklist, and its check at the
end."""

from __future__ import annotations

import os
import sys
from typing import Any

# rn's code lies in domain/, which comes on the import path before it's imported.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

import json
from collections.abc import Sequence
from datetime import date

import practice
from check import form
from fault import Answer, Wrong, end
from repository import host
from repository.place import RunPlace, made, named
from repository.worktree import newest

# The orchestrator's roles: the skills of rn that a run stands on.
_ORCHESTRATOR = ("rn:on", "rn:up", "rn:dn", "rn:ty", "rn:gm")
Rule = dict[str, Any]
# The rule of each step of the orchestrator's turn but its last: the turn ends there on a refusal
# that only the user can mend, where nothing else can move.
_BLOCKED: Rule = {"type": "result", "ends": ["blocked"]}
# The plain commands by which the orchestrator's review searches the repository's files, beside
# the Glob and Grep tools, which no rule of a step holds, as the tools differ by OS.
_LOOKS = ("find", "grep")

# A start as Lane gives it, in the form of Lane's rules.in.schema.json, and its steps that rn
# gives back, in the form of its rules.out.schema.json.
Given = dict[str, Any]
Steps = dict[str, Any]


def steps(given: Given, cwd: str, plugin_root: str) -> Steps:
    """The steps of the turn or the start, each held in order with its rules, each path as Lane
    compares it, `os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))`, so that a folder
    outside the repository comes as `../...`, and each command of rn's scripts as
    `python3 <plugin_root>/scripts/<script> <subcommand>`.

    Takes: the turn or the start as Lane gives it, a turn with each earlier turn of the run in
    `turns`; the folder that the conversation works in, the top of the user's repository; and rn's
    folder.
    Gives, for a turn of the orchestrator, whose role is the run's skill, `rn:on`, `rn:up`,
    `rn:dn`, `rn:ty`, or `rn:gm`, the steps of the event that its prompt starts, the run's first
    turn's by its skill:
    - for `/rn:on`, the hearing: `hear` alone, writing nothing and running no command;
    - for a new request, the user's words in the turn right after that of `/rn:on`, the run's
      first or one whose prompt is the typed command: `start`, running only `repository.py new`,
      on the run that `place.named` names from today and the words;
    - else, on the run that the turn concerns, the event's own step: `find` for `/rn:up`, running
      only `repository.py find`; `record` for `/rn:ty`, running only `tree.py signoff`; for
      `/rn:dn`, `stop`, writing nothing, then `pause`, running only `repository.py pause`, and no
      step after them; and `take` for any other prompt or a role's end, writing only the run's
      design tree and running no command. That run is, where the latest turn that typed `/rn:on`
      or `/rn:up`, the turn's own among them, typed `/rn:on`, the one that the request made, as
      `place.made` finds it from the request's words; else the one that
      `repository.worktree.newest` gives;
    - after the event's own step, but for a pause: `review`, writing only the run's design tree
      and running only `find` and `grep`, as the Glob and Grep tools that also search differ by
      OS; `touched`, writing only the design tree, running only `tree.py touched`, with the
      checklist of the command `tree.py touched <run>`; `commit`, running only `tree.py commit`;
      and `move`, writing nothing and running only `repository.py put-up` and `tree.py cut`.
    Each step of a turn but its last ends on `blocked`, so that a refusal that only the user can
    mend, such as `repository.py new`'s where origin names no default branch, ends the turn; the
    last keeps no such rule, as Lane judges the last step's result rule at each end with every step
    done. Where no run is found, past the hearing and a new request, the turn takes `find` alone,
    running only `repository.py find`, so that the orchestrator asks which run to pick up.
    For `rn:generator`, whose prompt is the path of its Cut from `cwd`: `read`, reading whole the
    Cut, the best practice's `best-practice.md`, so that a folder without one holds the step, and
    each input that is a file, writing nothing and running no command; `decide`, with the best
    practice's `decide` items as its checklist, writing only the Round's folder, running no
    command, and ending on `point`; `make`, with its `make` items as its checklist, writing only
    the deliverable's paths; `try`, writing only the Round's folder, from which the generator goes
    back to `decide` by Lane's `lane-back`, which needs no rule of rn's; and `check`, running only
    `repository.py checks`, with the check `check.py generator <cut>`, and the results `made` or,
    ending, `point`.
    For `rn:evaluator`, whose prompt is the path of its Cut from `cwd`, steps that never read the
    design tree, the generator's Cut and result, or another Round: `read`, reading whole the Cut,
    writing nothing and running no command; `start`, running only `repository.py trial`, writing
    nothing; `try`, writing only the folder of the people's starting state that
    `repository.trial.folder` names; and `judge`, with each condition's ID as its checklist,
    writing only the Round's folder, with the check `check.py evaluator <cut>` and the result
    `judged`. The generator's `make` and `try`, and the evaluator's `try`, run any command, as the
    people's own commands run there.
    Changes: nothing.
    Refuses: Wrong where the role is none of rn's, or a role's prompt names no Cut in its form,
    naming what's wrong.
    """
    role, prompt = given["role"], given["prompt"]
    if role in _ORCHESTRATOR:
        return {"steps": _turn(given, cwd, plugin_root)}
    if role == "rn:generator":
        return {"steps": _generator(_cut(prompt, cwd, "generator"), prompt, cwd, plugin_root)}
    if role == "rn:evaluator":
        return {"steps": _evaluator(_cut(prompt, cwd, "evaluator"), prompt, cwd, plugin_root)}
    raise Wrong(
        f"{role!r} is no role of rn's; rn gives the steps of {', '.join(_ORCHESTRATOR)},"
        " rn:generator, and rn:evaluator"
    )


def _turn(given: Given, cwd: str, plugin_root: str) -> list[Steps]:
    """The steps of the orchestrator's turn, by the event that its prompt starts: the run's first
    turn's by its skill."""
    skill = given["run"]["skill"]
    said = _said(given["prompt"], skill)
    command = _command(said)
    if command == "/rn:on":
        return [_step("hear", _writes(cwd, []), _commands(plugin_root))]
    typed = [_command(_said(each["prompt"], skill)) for each in given["turns"]]
    if not command and typed[-1:] == ["/rn:on"]:
        run = RunPlace(cwd, named(date.today(), said))
        new = _step("start", _commands(plugin_root, ("repository", "new")), _BLOCKED)
        return [new, *_shared(run, cwd, plugin_root)]
    run = _run_of(given["turns"], [*typed, command], cwd)
    if run is None:
        return [_step("find", _commands(plugin_root, ("repository", "find")))]
    if command == "/rn:dn":
        return [
            _step("stop", _writes(cwd, []), _BLOCKED),
            _step("pause", _commands(plugin_root, ("repository", "pause"))),
        ]
    return [_own(command, run, cwd, plugin_root), *_shared(run, cwd, plugin_root)]


def _own(command: str, run: RunPlace, cwd: str, plugin_root: str) -> Steps:
    """The event's own step on the run: `find` for a pick-up, `record` for a sign-off, and `take`
    for any other event."""
    if command == "/rn:up":
        return _step("find", _commands(plugin_root, ("repository", "find")), _BLOCKED)
    if command == "/rn:ty":
        return _step("record", _commands(plugin_root, ("tree", "signoff")), _BLOCKED)
    return _step("take", _writes(cwd, [run.tree]), _commands(plugin_root), _BLOCKED)


def _shared(run: RunPlace, cwd: str, plugin_root: str) -> list[Steps]:
    """The steps that every event but a pause takes after its own on the run."""
    touched = f"python3 {plugin_root}/scripts/tree.py touched {_rel(run.folder, cwd)}"
    return [
        _step("review", _writes(cwd, [run.tree]), _commands(plugin_root, plain=_LOOKS), _BLOCKED),
        _step(
            "touched",
            _writes(cwd, [run.tree]),
            _commands(plugin_root, ("tree", "touched")),
            {"type": "checklist", "command": touched},
            _BLOCKED,
        ),
        _step("commit", _commands(plugin_root, ("tree", "commit")), _BLOCKED),
        _step(
            "move",
            _writes(cwd, []),
            _commands(plugin_root, ("repository", "put-up"), ("tree", "cut")),
        ),
    ]


def _said(prompt: str, skill: str) -> str:
    """What a turn's prompt says: the prompt, or, for the run's first turn, whose prompt is empty,
    the command of the run's skill."""
    return prompt.strip() or f"/{skill}"


def _command(said: str) -> str:
    """The command of rn that a turn's words type, such as `/rn:ty`, or `` for none."""
    return said.partition(" ")[0] if said.startswith("/rn:") else ""


def _run_of(turns: list[Given], typed: list[str], cwd: str) -> RunPlace | None:
    """The run that the turn concerns, from the command that each turn typed, the turn's own last:
    where the latest `/rn:on` or `/rn:up` is `/rn:on`, the run that the request, the turn right
    after it, made, found by the request's words, or None before the request; else the run that
    `repository.worktree.newest` gives, as `/rn:up` picks it up."""
    begun = [i for i, each in enumerate(typed) if each in ("/rn:on", "/rn:up")]
    if not begun or typed[begun[-1]] == "/rn:up":
        return newest(cwd, host.run)
    request = begun[-1] + 1
    return made(cwd, turns[request]["prompt"]) if request < len(turns) else None


def _cut(prompt: str, cwd: str, role: str) -> Given:
    """The role's Cut that the start's prompt names by its path, held to its form."""
    path = os.path.join(cwd, prompt)
    try:
        with open(path, encoding="utf-8") as file:
            cut = json.load(file)
    except (OSError, ValueError) as error:
        raise Wrong(
            f"the prompt of rn:{role} names no Cut it can read, {prompt!r}: {error}"
        ) from None
    found = form.faults(cut, form.schema(f"{role}-cut"))
    if found:
        raise Wrong(f"{prompt}: isn't a Cut of rn:{role}: {found[0]}")
    return cut


def _generator(cut: Given, prompt: str, cwd: str, plugin_root: str) -> list[Steps]:
    """The generator's steps for its Cut."""
    folder = os.path.join(cwd, cut["best_practice"])
    held = practice.read(folder)
    worktree = os.path.join(cwd, cut["worktree"])
    whole = [os.path.join(cwd, prompt), os.path.join(folder, "best-practice.md")]
    whole += [
        os.path.join(cwd, each) for each in cut["inputs"] if os.path.isfile(os.path.join(cwd, each))
    ]
    node = cut["deliverable"]
    paths = [os.path.join(worktree, each) for each in [node["path"], *node.get("more_paths", [])]]
    round_ = os.path.join(cwd, cut["round"]) + "/"
    return [
        _step(
            "read",
            {"type": "reads_whole", "paths": _rels(whole, cwd)},
            _writes(cwd, []),
            _commands(plugin_root),
        ),
        _step(
            "decide",
            {"type": "checklist", "items": practice.items(held, "decide")},
            _writes(cwd, [round_]),
            _commands(plugin_root),
            {"type": "result", "ends": ["point"]},
        ),
        _step(
            "make",
            {"type": "checklist", "items": practice.items(held, "make")},
            _writes(cwd, paths),
        ),
        _step("try", _writes(cwd, [round_])),
        _step(
            "check",
            _commands(plugin_root, ("repository", "checks")),
            _check(plugin_root, "generator", prompt),
            {"type": "result", "results": ["made"], "ends": ["point"]},
        ),
    ]


def _evaluator(cut: Given, prompt: str, cwd: str, plugin_root: str) -> list[Steps]:
    """The evaluator's steps for its Cut, none of which reads what the people don't have."""
    round_ = os.path.join(cwd, cut["round"])
    rounds = os.path.dirname(os.path.dirname(round_))
    run_folder = os.path.dirname(rounds)
    others = [
        os.path.join(rounds, deliverable, name) + "/"
        for deliverable in sorted(os.listdir(rounds))
        for name in sorted(os.listdir(os.path.join(rounds, deliverable)))
        if os.path.join(rounds, deliverable, name) != os.path.normpath(round_)
    ]
    never = {
        "type": "reads_none",
        "paths": _rels(
            [
                os.path.join(run_folder, "design-tree.json"),
                os.path.join(round_, "generator-cut.json"),
                os.path.join(round_, "generator.json"),
                *others,
            ],
            cwd,
        ),
    }
    ids = [each["id"] for each in practice.conditions(cut["judges_by"])]
    return [
        _step(
            "read",
            never,
            {"type": "reads_whole", "paths": _rels([os.path.join(cwd, prompt)], cwd)},
            _writes(cwd, []),
            _commands(plugin_root),
        ),
        _step("start", never, _commands(plugin_root, ("repository", "trial")), _writes(cwd, [])),
        _step("try", never, _writes(cwd, [cut["trial"].rstrip("/") + "/"])),
        _step(
            "judge",
            never,
            {"type": "checklist", "items": ids},
            _writes(cwd, [round_ + "/"]),
            _check(plugin_root, "evaluator", prompt),
            {"type": "result", "results": ["judged"]},
        ),
    ]


def _step(name: str, *rules: Rule) -> Steps:
    """A step held in order, with its rules."""
    return {"name": name, "rules": [{"type": "order"}, *rules]}


def _check(plugin_root: str, role: str, prompt: str) -> Rule:
    """The rule of the check at the role's end, `check.py <role> <cut>`."""
    return {"type": "check", "check": f"python3 {plugin_root}/scripts/check.py {role} {prompt}"}


def _commands(plugin_root: str, *named_: tuple[str, str], plain: Sequence[str] = ()) -> Rule:
    """The rule of the commands of rn's scripts, each by its script and subcommand, and of each
    plain command, such as `grep`, by its own words; with none given, the rule lets only Lane's
    reporters through."""
    return {
        "type": "commands",
        "commands": [
            *(f"python3 {plugin_root}/scripts/{name}.py {sub}" for name, sub in named_),
            *plain,
        ],
    }


def _writes(cwd: str, paths: Sequence[str]) -> Rule:
    """The rule of the files a step writes, each as Lane compares it."""
    return {"type": "writes", "paths": _rels(paths, cwd)}


def _rels(paths: Sequence[str], cwd: str) -> list[str]:
    """Each path as Lane compares it."""
    return [_rel(each, cwd) for each in paths]


def _rel(path: str, cwd: str) -> str:
    """The path from the folder that the conversation works in, through no link, a folder keeping
    its closing `/`."""
    shown = os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))
    return shown + "/" if path.endswith("/") else shown


def main(stdin: str, cwd: str, plugin_root: str) -> Answer:
    """The exit code, stdout, and stderr of the adapter, as Lane runs it.

    Takes: what Lane writes on its standard input, the folder it runs in, and rn's folder.
    Gives: 0 with `steps`'s output as one line of JSON; 1 with `rules.py: <what's wrong>` where the
    input isn't JSON, lacks any of `run`, `role`, `prompt`, and `turns`, or `steps` refuses it as
    Wrong. Lane stops the turn or the start on any but 0.
    Changes: nothing.
    Refuses: nothing; each fault is its exit code.
    """
    try:
        given = json.loads(stdin)
    except ValueError as error:
        return 1, "", f"rules.py: its input isn't JSON: {error}\n"
    try:
        if not isinstance(given, dict) or not {"run", "role", "prompt", "turns"} <= set(given):
            raise Wrong("its input isn't a start or a turn as Lane gives it")
        return 0, json.dumps(steps(given, cwd, plugin_root)) + "\n", ""
    except Wrong as wrong:
        return 1, "", f"rules.py: {wrong}\n"


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd(), os.path.dirname(os.path.dirname(HERE))))
