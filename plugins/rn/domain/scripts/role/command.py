"""Decides what rn's hook does once one of rn's roles ends, so that no instruction to a role or
restart of it holds what must happen every time: it checks each result of the work against its
schema and keeps the role going until each holds, moves each task on by its role's result,
and removes the trials' folders that the role leaves."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any

import form
from fault import Answer
from host import Host
from place import WorkPlace, version
from repository import trial, worktree
from steering import closed, record, rounds

USAGE = "usage: role ended   (Claude Code's input of SubagentStop on stdin)\n"
# The roles of rn that write a result, as Claude Code names a plugin's agent in `agent_type`.
_ROLES = {"generator", "refactorer", "evaluator", "fixer"}


def main(argv: Sequence[str], given: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `role ended`, with Claude Code's input of the
    SubagentStop event, with rn's folder at `plugin_root`, and git reached through `host`.

    - For an agent that isn't one of rn's roles that write a result, as `agent_type` names it,
      `rn:<role>` or `<role>`: 0, doing nothing.
    - For one of those roles, for each piece of work with something left to do in the worktree
      that the input's `cwd` lies in, the one rn runs in, as `worktree.left` gives them: 2 with
      each result that leaves its schema, a Round's or a Fix's, a line each as `form.held` names
      it, and each entry of a task that this role takes next with no result of the role yet,
      changing nothing, so that Claude Code keeps the role going with those words until each
      holds. Otherwise it moves each task on by its next role's result as `record.moved` does,
      writing the steering where it changes and the closed tasks as `closed.added` does, removes
      each of its trials' folders as `trial.removed` does, and gives 0.
    - 2 with the usage where the arguments are other than `ended`.
    """
    if list(argv) != ["ended"]:
        return 2, "", USAGE
    hook = json.loads(given)
    role = str(hook.get("agent_type") or "").split(":")[-1]
    if role not in _ROLES:
        return 0, "", ""
    schemas = os.path.join(plugin_root, "domain", "schemas")
    works = worktree.left(
        str(hook["cwd"]), host, os.path.join(schemas, "steering.schema.json"), version(plugin_root)
    )
    faults = [fault for work in works for fault in rounds.faults(work, schemas)]
    faults += [fault for work in works for fault in _missing(work, role, schemas)]
    if faults:
        return 2, "", "".join(f"role: {each}\n" for each in faults)
    for work in works:
        _moved(work, schemas)
        trial.removed(work)
    return 0, "", ""


def _missing(work: WorkPlace, role: str, schemas: str) -> list[str]:
    """Each entry of a task that the role takes next and that holds no result of the role, in
    words, as a role that ends without its result leaves its task where it was."""
    held = _steering(work, schemas)
    found = []
    for each in held["tasks"] if held else []:
        if each.get("next", "generator") != role or "entry" not in each:
            continue
        folder = os.path.join(rounds.folder_of(work, each["id"]), each["entry"])
        name = rounds.RESULTS[role][0]
        if not os.path.isfile(os.path.join(folder, name)):
            found.append(f"{folder} holds no {name}; write it as your Output says")
    return found


def _moved(work: WorkPlace, schemas: str) -> None:
    """Moves each task on by its next role's result, writing the steering where it changes, and
    adding each task it completes to the closed tasks; the work with no steering yet, before its
    first aim, has nothing to move."""
    held = _steering(work, schemas)
    if held is None:
        return
    steering, completed = record.moved(held, _results(work, held, schemas))
    closed.added(work, completed, schemas)
    if steering != held:
        with open(work.steering, "w", encoding="utf-8") as f:
            json.dump(steering, f, indent=2, ensure_ascii=False)
            f.write("\n")


def _results(work: WorkPlace, steering: dict[str, Any], schemas: str) -> dict[str, Any]:
    """For each task with an entry, the results that its entry holds, by role."""
    return {
        each["id"]: rounds.results(
            os.path.join(rounds.folder_of(work, each["id"]), each["entry"]), schemas
        )
        for each in steering["tasks"]
        if "entry" in each
    }


def _steering(work: WorkPlace, schemas: str) -> dict[str, Any] | None:
    if not os.path.isfile(work.steering):
        return None
    return form.held(work.steering, os.path.join(schemas, "steering.schema.json"), "the steering")
