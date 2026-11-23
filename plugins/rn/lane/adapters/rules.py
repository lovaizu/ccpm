"""Decides the steps of each turn of rn's orchestrator and of each start of its generator and
evaluator, and the rules of each step, as Lane asks them: the turn's event's own step and those
that every event shares, and for a role the files each step reads whole, the practices of its
kind's best practice as its checklist, and its check at the end; and for the evaluator alone, the
files it never reads and the only ones it writes, as it judges in the people's place, apart from
the generator. No step holds a role to the commands it runs or, but the evaluator's, to the files
it writes, as the role's purpose needs no such bind, and each bind is a fence that the role looks
for a way round."""

from __future__ import annotations

import os
import sys
from typing import Any

# rn's code lies in domain/, which comes on the import path before it's imported.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

import json
from collections.abc import Sequence

import practice
from check import form
from fault import Answer, Wrong, end
from repository import host
from repository.place import RunPlace, of_session
from repository.worktree import newest

# The orchestrator's roles: the skills of rn that a run stands on.
_ORCHESTRATOR = ("rn:on", "rn:up", "rn:dn", "rn:ty", "rn:gm")
Rule = dict[str, Any]
# The rule of each step of the orchestrator's turn but its last: the turn ends there on a refusal
# that only the user can mend, where nothing else can move.
_BLOCKED: Rule = {"type": "result", "ends": ["blocked"]}
# The rule of the step `take`: the turn ends there too where the user's words pause or cancel the
# run, as the orchestrator then reports by `paused` or `cancelled`, so that rn's order ends the run.
_LEFT: Rule = {"type": "result", "ends": ["blocked", "paused", "cancelled"]}
# The rule of a pause's last step: the turn gives `paused`, by which rn's order ends the run.
_PAUSED: Rule = {"type": "result", "results": ["paused"]}

# A start as Lane gives it, in the form of Lane's rules.in.schema.json, and its steps that rn
# gives back, in the form of its rules.out.schema.json.
Given = dict[str, Any]
Steps = dict[str, Any]


def steps(given: Given, cwd: str, plugin_root: str) -> Steps:
    """The steps of the turn or the start, each held in order with its rules, each path as Lane
    compares it, `os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))`, so that a folder
    outside the repository comes as `../...`, and each command of rn's scripts as
    `python3 <plugin_root>/scripts/<script> <subcommand>`.

    Takes: the turn or the start as Lane gives it, a turn with the command it called, typed or by
    the Skill tool, in `command`, and each earlier turn of the run, with its own, in `turns`; the
    folder that the conversation works in, the top of the user's repository; and rn's
    folder.
    Gives, for a turn of the orchestrator, whose role is the run's skill, `rn:on`, `rn:up`,
    `rn:dn`, `rn:ty`, or `rn:gm`, the steps of the event that the command it called starts, the
    run's skill for the run's first turn, so that an AI's Skill call takes the steps of the command
    typed:
    - for `rn:on`, the hearing: `hear` alone;
    - for a new request, the user's words in a turn that called no command, right after one that
      called `rn:on`: `start`, on the run that it makes;
    - else, on the run that the turn concerns, the event's own step: `find` for `rn:up`; `record`
      for `rn:ty`; for `rn:dn`, `stop`, then `pause`, with the result `paused`, and no step after
      them; and `take` for any other command or none, such as an answer or a role's end, ending
      also on `paused` or `cancelled`, as the user's words may pause or cancel the run. That run
      is the one that `place.of_session` gives for the conversation's session, `run.session`;
      else, where no turn called `rn:on` or `rn:up`, or the latest that did, the turn's own among
      them, called `rn:up`, the one that `repository.worktree.newest` gives, as `find` picks it
      up; else none;
    - after the event's own step, but for a pause: `review`; `touched`, with the checklist of the
      command `tree.py touched --session=<run.session>`, which names the run by the session, as a
      request's turn makes the run at its `start`; `commit`; `move`; and `final`, the check of
      the work whole once each deliverable is done, which the orchestrator records at once while
      one isn't.
    Each step of a turn but its last ends on `blocked`, so that a refusal that only the user can
    mend, such as `repository.py new`'s where origin names no default branch, ends the turn; the
    last keeps no such rule, as Lane judges the last step's result rule at each end with every step
    done, and only a pause's last gives a result, `paused`. Where no run is found, past the
    hearing and a new request, the turn takes `find` alone, so that the orchestrator asks which
    run to pick up.
    For `rn:generator`, whose prompt is the path of its Cut from `cwd`: `read`, reading whole the
    Cut, the best practice's `best-practice.md`, so that a folder without one holds the step, each
    input that is a file, and each of the deliverable's paths that is a file; `decide`, with the
    best practice's `decide` items as its checklist, and ending on `point`; `make`, with its `make`
    items as its checklist; `try`, from which the generator goes back to `decide` by Lane's
    `lane-back`, which needs no rule of rn's; and `check`, with the check
    `check.py generator <cut>`, and the results `made` or, ending, `point`.
    For `rn:evaluator`, whose prompt is the path of its Cut from `cwd`, steps that never read the
    design tree, the generator's Cut and result, or another Round: `read`, reading whole the Cut,
    writing nothing; `start`, writing nothing; `try`, writing only the folder of the people's
    starting state that `repository.trial.folder` names; and `judge`, with each condition's ID as
    its checklist, writing only the Round's folder, with the check `check.py evaluator <cut>` and
    the result `judged`.
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
    """The steps of the orchestrator's turn, by the event that the command it called starts, typed
    or by the Skill tool, as Lane gives it, the run's skill for the run's first turn, or by its
    prompt where it called none."""
    command = given["command"]
    if command == "rn:on":
        return [_step("hear")]
    called = [each["command"] for each in given["turns"]]
    session = given["run"]["session"]
    if not command and called[-1:] == ["rn:on"]:
        return [_step("start", _BLOCKED), *_shared(session, plugin_root)]
    if _run_of([*called, command], cwd, session) is None:
        return [_step("find")]
    if command == "rn:dn":
        return [_step("stop", _BLOCKED), _step("pause", _PAUSED)]
    own = _own(command)
    rule = _LEFT if own == "take" else _BLOCKED
    return [_step(own, rule), *_shared(session, plugin_root)]


def _own(command: str | None) -> str:
    """The name of the event's own step on the run: `find` for a pick-up, `record` for a sign-off,
    and `take` for any other event."""
    return {"rn:up": "find", "rn:ty": "record"}.get(command or "", "take")


def _shared(session: str, plugin_root: str) -> list[Steps]:
    """The steps that every event but a pause takes after its own on the conversation's run, named
    by its session."""
    touched = f"python3 {plugin_root}/scripts/tree.py touched --session={session}"
    return [
        _step("review", _BLOCKED),
        _step("touched", {"type": "checklist", "command": touched}, _BLOCKED),
        _step("commit", _BLOCKED),
        _step("move", _BLOCKED),
        _step("final"),
    ]


def _run_of(called: list[str | None], cwd: str, session: str) -> RunPlace | None:
    """The run that the turn concerns, from the command that each turn called, the turn's own last:
    the conversation's own, whose design tree holds its session; else, where the latest `rn:on`
    or `rn:up` is `rn:up`, or none is, the run that `repository.worktree.newest` gives, as `rn:up`
    picks it up; else None, as a request of `rn:on` makes no run where its `new` refuses."""
    own = of_session(cwd, session)
    if own is not None:
        return own
    begun = [each for each in called if each in ("rn:on", "rn:up")]
    return newest(cwd, host.run) if begun[-1:] != ["rn:on"] else None


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
    whole += [each for each in paths if os.path.isfile(each)]
    return [
        _step("read", {"type": "reads_whole", "paths": _rels(whole, cwd)}),
        _step(
            "decide",
            {"type": "checklist", "items": practice.items(held, "decide")},
            {"type": "result", "ends": ["point"]},
        ),
        _step("make", {"type": "checklist", "items": practice.items(held, "make")}),
        _step("try"),
        _step(
            "check",
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
        ),
        _step("start", never, _writes(cwd, [])),
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
    input isn't JSON, lacks any of `run`, `role`, `prompt`, `command`, and `turns`, or `steps`
    refuses it as Wrong. Lane reads any but 0 as steps it couldn't check, and says so with what the
    adapter said.
    Changes: nothing.
    Refuses: nothing; each fault is its exit code.
    """
    try:
        given = json.loads(stdin)
    except ValueError as error:
        return 1, "", f"rules.py: its input isn't JSON: {error}\n"
    try:
        if not isinstance(given, dict) or not {"run", "role", "prompt", "command", "turns"} <= set(
            given
        ):
            raise Wrong("its input isn't a start or a turn as Lane gives it")
        return 0, json.dumps(steps(given, cwd, plugin_root)) + "\n", ""
    except Wrong as wrong:
        return 1, "", f"rules.py: {wrong}\n"


if __name__ == "__main__":
    end(lambda: main(sys.stdin.read(), os.getcwd(), os.path.dirname(os.path.dirname(HERE))))
