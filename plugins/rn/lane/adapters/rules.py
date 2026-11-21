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
from fault import Wrong, end
from repository import host
from repository.place import RunPlace, named
from repository.worktree import newest
from tree import form as tree_form

# The orchestrator's roles, the skills of rn that a run stands on, and rn's subagents.
_ORCHESTRATOR = ("rn:on", "rn:up", "rn:dn", "rn:ty", "rn:gm")
_SCHEMAS = os.path.join(HERE, "..", "..", "domain", "schemas")
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
    """The steps of the turn or the start, each with its rules, each path as Lane compares it,
    `os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))`, so that a folder outside the
    repository, such as the people's starting state or rn's best practices, comes as `../...`, and
    each command of rn's scripts as `python3 <plugin_root>/scripts/<script> <subcommand>`.

    Takes: the turn or the start as Lane gives it; the folder that the conversation works in, the
    top of the user's repository; and rn's folder.
    Gives, for a turn of the orchestrator, whose role is the skill of rn that the run stands on,
    `rn:on`, `rn:up`, `rn:dn`, `rn:ty`, or `rn:gm`, the steps of the event that its prompt starts,
    the run's first turn's by its skill, each held in order and run on the run's folder:
    - for `/rn:on`, the hearing, `hear` alone, writing nothing and running no command, as the
      orchestrator asks the user what they want to make;
    - for a new request, a prompt of the user's words in a turn of `rn:on`, while no run made in
      the conversation lies, the run that `repository.worktree.newest` gives lying with no
      worktree here or with its plan, the deliverable of the kind `design-tree`, done: `start`,
      running only `repository.py new`, on the run that `place.named` names from today and the
      words;
    - else, on the run that `repository.worktree.newest` gives, the event's own step: for a
      pick-up, `/rn:up`, `find`, running only `repository.py find`; for a sign-off, `/rn:ty`,
      `record`, running only `tree.py signoff`; for a send-back, `/rn:gm`, an answer, any other
      prompt of the person, and a role's end, a subagent's end as Claude Code gives it, `take`,
      writing only the run's design tree and running no command; and for a pause, `/rn:dn`,
      `stop`, writing nothing, and `pause`, running only `repository.py pause`, with no step
      after them;
    - after the event's own step, for each event but a pause, the steps that every event shares:
      `review`, writing only the run's design tree and running only `find` and `grep`, the Glob
      and Grep tools going through, as the tools that search differ by OS; `touched`, writing
      only the run's design tree and running only `tree.py touched`, with the checklist whose
      command is `tree.py touched <run>`; `commit`, running only `tree.py commit`; and `move`,
      running only `repository.py put-up` and `tree.py cut`, writing nothing.
    Each step of the turn but its last ends on `blocked`, so that a refusal that only the user can
    mend, where nothing else can move, such as that of `repository.py new` in a repository whose
    origin names no default branch, ends the turn. The last step keeps no such rule, as Lane
    judges the last step's result rule at each end with every step done, and would stop each end
    with no result. A turn other than the hearing and a new request, in a repository with no run
    to pick up, takes the step `find` alone, running only `repository.py find`, so that the
    orchestrator asks the user which run to pick up, and the turn ends.
    For `rn:generator`, whose prompt is the path of its Cut from `cwd`, the steps `read`, `decide`,
    `make`, `try`, and `check`, each held in order: `read` reading whole the Cut, the best
    practice's `best-practice.md`, which every best practice's folder holds, so that a folder
    without one holds the step until it's there, and each input that is a file, writing nothing and
    running no command; `decide` with the best practice's `decide` items as its checklist, writing
    only the Round's folder, where its `generator.json` gives a point, running no command, and
    ending on `point`; `make` with its `make` items as its checklist, writing only the
    deliverable's paths; `try` writing only the Round's folder, from which the generator goes
    back to `decide` by Lane's `lane-back` where a condition that the people meet falls short, as
    Lane holds a step gone back to with no rule of rn's; and `check` running only
    `repository.py checks`, with the check `check.py generator <cut>`, and the results `made` or,
    ending, `point`.
    For `rn:evaluator`, whose prompt is the path of its Cut from `cwd`, the steps `read`, `start`,
    `try`, and `judge`, each held in order and never reading the design tree, the generator's Cut
    and result, or another Round: `read` reading whole the Cut, writing nothing and running no
    command; `start` running only `repository.py trial`, writing nothing; `try` writing only the
    folder of the people's starting state, as `repository.trial.folder` names it; and `judge` with
    each condition's ID as its checklist, writing only the Round's folder, with the check
    `check.py evaluator <cut>` and the result `judged`. The generator's `make` and `try`, and the
    evaluator's `try`, run any command, as the people's own commands run there.
    Changes: nothing.
    Refuses: Wrong where the role is none of rn's, or a role's prompt names no Cut in its form,
    naming what's wrong.
    """
    role, prompt = given["role"], given["prompt"]
    if role in _ORCHESTRATOR:
        return {"steps": _turn(given["run"], role, prompt, cwd, plugin_root)}
    if role == "rn:generator":
        return {"steps": _generator(_cut(prompt, cwd, "generator"), prompt, cwd, plugin_root)}
    if role == "rn:evaluator":
        return {"steps": _evaluator(_cut(prompt, cwd, "evaluator"), prompt, cwd, plugin_root)}
    raise Wrong(
        f"{role!r} is no role of rn's; rn gives the steps of {', '.join(_ORCHESTRATOR)},"
        " rn:generator, and rn:evaluator"
    )


def _turn(run: Given, role: str, prompt: str, cwd: str, plugin_root: str) -> list[Steps]:
    """The steps of the orchestrator's turn, by the event that its prompt starts: the run's first
    turn's by its skill."""
    said = prompt.strip() or f"/{run['skill']}"
    command = said.partition(" ")[0] if said.startswith("/rn:") else ""
    if command == "/rn:on":
        return [_step("hear", _writes(cwd, []), _commands(plugin_root))]
    found = newest(cwd, host.run)
    find = _commands(plugin_root, ("repository", "find"))
    if role == "rn:on" and not command and not _unsigned(found):
        place = RunPlace(cwd, named(date.today(), said))
        own = _step("start", _commands(plugin_root, ("repository", "new")), _BLOCKED)
    elif found is None:
        return [_step("find", find)]
    elif command == "/rn:dn":
        return [
            _step("stop", _writes(cwd, []), _BLOCKED),
            _step("pause", _commands(plugin_root, ("repository", "pause"))),
        ]
    else:
        place = found
        own = {
            "/rn:up": _step("find", find, _BLOCKED),
            "/rn:ty": _step("record", _commands(plugin_root, ("tree", "signoff")), _BLOCKED),
        }.get(command) or _step(
            "take", _writes(cwd, [place.tree]), _commands(plugin_root), _BLOCKED
        )
    touched = f"python3 {plugin_root}/scripts/tree.py touched {_rel(place.folder, cwd)}"
    return [
        own,
        _step("review", _writes(cwd, [place.tree]), _commands(plugin_root, plain=_LOOKS), _BLOCKED),
        _step(
            "touched",
            _writes(cwd, [place.tree]),
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


def _unsigned(run: RunPlace | None) -> bool:
    """Whether the run lies here with its plan, the deliverable of the kind `design-tree`, not
    done, as the run that a conversation of `/rn:on` made stands until the user signs its plan off
    by `/rn:ty`."""
    if run is None or not os.path.isfile(run.tree):
        return False
    deliverables = tree_form.read(run.tree)["deliverables"]
    return any(each["kind"] == "design-tree" and each["status"] != "done" for each in deliverables)


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
    found = form.faults(cut, os.path.join(_SCHEMAS, f"{role}-cut.schema.json"))
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
            {
                "type": "check",
                "check": f"python3 {plugin_root}/scripts/check.py generator {prompt}",
            },
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
    ids = [
        each["id"]
        for factor in cut["judges_by"]["critical_success_factors"]
        for each in factor["necessary_conditions"]
    ]
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
            {
                "type": "check",
                "check": f"python3 {plugin_root}/scripts/check.py evaluator {prompt}",
            },
            {"type": "result", "results": ["judged"]},
        ),
    ]


def _step(name: str, *rules: Rule) -> Steps:
    """A step held in order, with its rules."""
    return {"name": name, "rules": [{"type": "order"}, *rules]}


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


def main(stdin: str, cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of the adapter, as Lane runs it.

    Takes: what Lane writes on its standard input, the folder it runs in, and rn's folder.
    Gives: 0 with `steps`'s output as one line of JSON; 1 with `rules.py: <what's wrong>` where the
    input isn't JSON or `steps` refuses it as Wrong. Lane stops the turn or the start on any but 0.
    Changes: nothing.
    Refuses: nothing; each fault is its exit code.
    """
    try:
        given = json.loads(stdin)
    except ValueError as error:
        return 1, "", f"rules.py: its input isn't JSON: {error}\n"
    try:
        if not isinstance(given, dict) or not {"run", "role", "prompt"} <= set(given):
            raise Wrong("its input isn't a start or a turn as Lane gives it")
        return 0, json.dumps(steps(given, cwd, plugin_root)) + "\n", ""
    except Wrong as wrong:
        return 1, "", f"rules.py: {wrong}\n"


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd(), os.path.dirname(os.path.dirname(HERE))))
