"""Decides what rn's hook does once one of rn's roles ends, so that no instruction to a role or
restart of it holds what must happen every time: it checks each result of each run against its
schema and keeps the role going until each holds, takes a pruner's result into the steering, as
the steering keeps one writer, and commits and pushes each run's changes at once."""

from __future__ import annotations

import glob
import json
import os
from collections.abc import Sequence
from typing import Any

import form
import push
from fault import Answer, CantRun, Missing, Wrong
from host import Host
from place import RunPlace
from repository import worktree
from steering import record, rounds

USAGE = "usage: role ended   (Claude Code's input of SubagentStop on stdin)\n"
# The roles of rn, as Claude Code names a plugin's agent in `agent_type`.
_ROLES = {"pruner", "generator", "refactorer", "evaluator", "fixer", "inspector"}


def main(argv: Sequence[str], given: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `role ended`, with Claude Code's input of the
    SubagentStop event, with rn's folder at `plugin_root`, and git and gh reached through `host`.

    - For an agent that isn't one of rn's roles, as `agent_type` names it, `rn:<role>` or
      `<role>`: 0, doing nothing.
    - For one of rn's roles, for each run of the repository that the input's `cwd` lies in, as
      `worktree.runs` gives them: 2 with each result that leaves
      its schema, the pruner's or a Round's or a Fix's, a line each as `form.held` names it,
      changing nothing, so that Claude Code keeps the role going with those words until each
      holds. Otherwise it takes the pruner's result, where there's one, into the steering as
      `record.taken_in` makes it and removes the result, moves each deliverable on by its next
      role's result as `record.moved` does, then commits and pushes each run whose
      worktree holds a change as `push.kept` does, as `rn: <the result's message>` for the
      pruner's and `rn: the <role> ended` for any other, and gives 0.
    - 1 with `role: <what's wrong>` where something `push.kept` needs is Missing, or 2 where it
      CantRun, the commit kept where only the push failed, as the role can't mend either.
    - 2 with the usage where the arguments are other than `ended`.
    """
    if list(argv) != ["ended"]:
        return 2, "", USAGE
    hook = json.loads(given)
    role = str(hook.get("agent_type") or "").split(":")[-1]
    if role not in _ROLES:
        return 0, "", ""
    schemas = os.path.join(plugin_root, "domain", "schemas")
    runs = worktree.runs(str(hook["cwd"]), host)
    faults = [fault for run in runs for fault in _faults(run, schemas)]
    if faults:
        return 2, "", "".join(f"role: {each}\n" for each in faults)
    try:
        for run in runs:
            _kept(run, role, schemas, host)
    except (Missing, CantRun) as stopped:
        return (1 if isinstance(stopped, Missing) else 2), "", f"role: {stopped}\n"
    return 0, "", ""


def _faults(run: RunPlace, schemas: str) -> list[str]:
    """Each result of the run that leaves its schema, or that the steering refuses, in words."""
    found = []
    if os.path.isfile(run.pruner):
        try:
            result = form.held(
                run.pruner, os.path.join(schemas, "pruner.schema.json"), "the pruner's result"
            )
            record.taken_in(_steering(run, schemas), result)
        except Wrong as why:
            found.append(str(why))
    for root in sorted(glob.glob(os.path.join(run.rounds, "*", "*"))):
        try:
            rounds.entries(root, schemas)
        except Wrong as why:
            found.append(str(why))
    return found


def _kept(run: RunPlace, role: str, schemas: str, host: Host) -> None:
    """Takes the pruner's result into the steering, where there's one, moves each deliverable on
    by its next role's result, then commits and pushes the run where its worktree holds a change;
    a run with no steering yet, before its first weighing, has nothing to keep."""
    message = f"rn: the {role} ended"
    held = _steering(run, schemas)
    steering = held
    if os.path.isfile(run.pruner):
        result = form.held(
            run.pruner, os.path.join(schemas, "pruner.schema.json"), "the pruner's result"
        )
        steering = record.taken_in(steering, result)
        os.remove(run.pruner)
        message = f"rn: {result['message']}"
    if steering is None:
        return
    steering = record.moved(steering, _results(run, steering, schemas))
    if steering != held:
        with open(run.steering, "w", encoding="utf-8") as f:
            json.dump(steering, f, indent=2, ensure_ascii=False)
            f.write("\n")
    if host(["git", "status", "--porcelain"], run.worktree).out.strip():
        push.kept(run, steering, message, host)


def _results(run: RunPlace, steering: dict[str, Any], schemas: str) -> dict[str, Any]:
    """For each open deliverable with an entry, the results that its entry holds, by role."""
    found = {}
    for number, step in enumerate(steering["state"]["steps"], 1):
        for each in step["deliverables"]:
            if each["status"] != "open" or "entry" not in each:
                continue
            folder = os.path.join(rounds.folder_of(run, number, each["path"]), each["entry"])
            found[each["path"]] = rounds.results(folder, schemas)
    return found


def _steering(run: RunPlace, schemas: str) -> dict[str, Any] | None:
    if not os.path.isfile(run.steering):
        return None
    return form.held(run.steering, os.path.join(schemas, "steering.schema.json"), "the steering")
