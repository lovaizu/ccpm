"""Decides what rn's hook does once one of rn's roles ends, so that no instruction to a role or
restart of it holds what must happen every time: it checks each result of the work against its
schema and keeps the role going until each holds, moves each deliverable on by its role's result,
and removes the trials' folders that the role leaves."""

from __future__ import annotations

import glob
import json
import os
from collections.abc import Sequence
from typing import Any

import form
from fault import Answer, Wrong
from host import Host
from place import WorkPlace
from repository import trial, worktree
from steering import record, rounds

USAGE = "usage: role ended   (Claude Code's input of SubagentStop on stdin)\n"
# The roles of rn that write a result, as Claude Code names a plugin's agent in `agent_type`.
_ROLES = {"generator", "refactorer", "evaluator", "fixer"}


def main(argv: Sequence[str], given: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `role ended`, with Claude Code's input of the
    SubagentStop event, with rn's folder at `plugin_root`, and git reached through `host`.

    - For an agent that isn't one of rn's roles that write a result, as `agent_type` names it,
      `rn:<role>` or `<role>`: 0, doing nothing.
    - For one of those roles, for each piece of work in the worktree that the input's `cwd` lies
      in, the one rn runs in, as `worktree.works` gives them: 2 with each result that leaves its
      schema, a Round's or a Fix's, a line each as `form.held` names it, changing nothing, so that
      Claude Code keeps the role going with those words until each holds. Otherwise it moves each
      deliverable on by its next role's result as `record.moved` does, writing the steering where
      it changes, removes each of its trials' folders as `trial.removed` does, and gives 0.
    - 2 with the usage where the arguments are other than `ended`.
    """
    if list(argv) != ["ended"]:
        return 2, "", USAGE
    hook = json.loads(given)
    role = str(hook.get("agent_type") or "").split(":")[-1]
    if role not in _ROLES:
        return 0, "", ""
    schemas = os.path.join(plugin_root, "domain", "schemas")
    works = worktree.works(str(hook["cwd"]), host)
    faults = [fault for work in works for fault in _faults(work, schemas)]
    if faults:
        return 2, "", "".join(f"role: {each}\n" for each in faults)
    for work in works:
        _moved(work, schemas)
        trial.removed(work)
    return 0, "", ""


def _faults(work: WorkPlace, schemas: str) -> list[str]:
    """Each result of the work that leaves its schema, in words."""
    found = []
    for root in sorted(glob.glob(os.path.join(work.rounds, "*", "*"))):
        try:
            rounds.entries(root, schemas)
        except Wrong as why:
            found.append(str(why))
    return found


def _moved(work: WorkPlace, schemas: str) -> None:
    """Moves each deliverable on by its next role's result, writing the steering where it changes;
    the work with no steering yet, before its first aim, has nothing to move."""
    held = _steering(work, schemas)
    if held is None:
        return
    steering = record.moved(held, _results(work, held, schemas))
    if steering != held:
        with open(work.steering, "w", encoding="utf-8") as f:
            json.dump(steering, f, indent=2, ensure_ascii=False)
            f.write("\n")


def _results(work: WorkPlace, steering: dict[str, Any], schemas: str) -> dict[str, Any]:
    """For each open deliverable with an entry, the results that its entry holds, by role."""
    found = {}
    for number, step in enumerate(steering["state"]["steps"], 1):
        for each in step["deliverables"]:
            if each["status"] != "open" or "entry" not in each:
                continue
            folder = os.path.join(rounds.folder_of(work, number, each["path"]), each["entry"])
            found[each["path"]] = rounds.results(folder, schemas)
    return found


def _steering(work: WorkPlace, schemas: str) -> dict[str, Any] | None:
    if not os.path.isfile(work.steering):
        return None
    return form.held(work.steering, os.path.join(schemas, "steering.schema.json"), "the steering")
