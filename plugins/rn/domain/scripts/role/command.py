"""Decides what rn's hook does once one of rn's roles ends, so that no instruction to a role or
restart of it holds what must happen every time: it checks the role's results against their
schemas and keeps the role going until each holds, moves each deliverable on by its role's result,
and commits and pushes the work that the result moved at once."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any

import form
import push
from fault import Answer, CantRun, Missing, Wrong
from host import Host
from place import WorkPlace
from repository import worktree
from steering import record, rounds

USAGE = "usage: role ended   (Claude Code's input of SubagentStop on stdin)\n"
# The roles of rn, as Claude Code names a plugin's agent in `agent_type`, `rn:<role>`.
_ROLES = {"generator", "refactorer", "evaluator", "fixer", "inspector"}


def main(argv: Sequence[str], given: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `role ended`, with Claude Code's input of the
    SubagentStop event, with rn's folder at `plugin_root`, and git and gh reached through `host`.

    - For an agent that isn't one of rn's roles, as `agent_type` names it `rn:<role>`: 0, doing
      nothing, as another plugin's agent may share a role's name.
    - For one of rn's roles, for each piece of work in the repository that the input's `cwd` lies
      in, as `worktree.works` gives them, and each open deliverable there whose next role is the
      one that ended: 2 with each result in the deliverable's entry that leaves its schema, a
      Round's or a Fix's, a line each as `form.held` names it, changing nothing, so that Claude
      Code keeps the role going with those words until each holds. Otherwise it moves each such
      deliverable on by its result as `record.moved` does, commits and pushes each piece of work
      whose steering that moved as `push.kept` does, as `rn: the <role> ended`, and gives 0, so
      that no other role's work still being written is committed, and a push that git refuses
      waits for the next.
    - 1 with `role: <what's wrong>` where something `push.kept` needs is Missing or git fails,
      as the role can't mend either, so that the role ends, and the orchestrator's next script
      meets it.
    - 2 with the usage where the arguments are other than `ended`.
    """
    if list(argv) != ["ended"]:
        return 2, "", USAGE
    hook = json.loads(given)
    agent = str(hook.get("agent_type") or "")
    role = agent[len("rn:") :]
    if not agent.startswith("rn:") or role not in _ROLES:
        return 0, "", ""
    schemas = os.path.join(plugin_root, "domain", "schemas")
    works = worktree.works(str(hook["cwd"]), host)
    faults = [fault for work in works for fault in _faults(work, role, schemas)]
    if faults:
        return 2, "", "".join(f"role: {each}\n" for each in faults)
    try:
        for work in works:
            _kept(work, role, schemas, host)
    except (Missing, CantRun) as stopped:
        return 1, "", f"role: {stopped}\n"
    return 0, "", ""


def _faults(work: WorkPlace, role: str, schemas: str) -> list[str]:
    """Each result of the role in the work that leaves its schema, in words."""
    found = []
    for folder in _entries(work, role, schemas).values():
        try:
            rounds.results(folder, schemas)
        except Wrong as why:
            found.append(str(why))
    return found


def _kept(work: WorkPlace, role: str, schemas: str, host: Host) -> None:
    """Moves each deliverable whose next role is the role on by its result, then commits and pushes
    the work where that moved its steering."""
    held = _steering(work, schemas)
    if held is None:
        return
    results = {
        path: rounds.results(folder, schemas)
        for path, folder in _entries(work, role, schemas).items()
    }
    steering = record.moved(held, results)
    if steering == held:
        return
    with open(work.steering, "w", encoding="utf-8") as f:
        json.dump(steering, f, indent=2, ensure_ascii=False)
        f.write("\n")
    push.kept(work, f"rn: the {role} ended", None, host)


def _entries(work: WorkPlace, role: str, schemas: str) -> dict[str, str]:
    """For each open deliverable whose next role is the role and that has an entry, the entry's
    folder, by the deliverable's path; none where the work has no steering yet, before its first
    aim."""
    steering = _steering(work, schemas)
    found: dict[str, str] = {}
    for number, step in enumerate(steering["state"]["steps"] if steering else [], 1):
        for each in step["deliverables"]:
            if each["status"] == "open" and "entry" in each and _next(each) == role:
                folder = rounds.folder_of(work, number, each["path"])
                found[each["path"]] = os.path.join(folder, each["entry"])
    return found


def _next(each: dict[str, Any]) -> str:
    return str(each.get("next", "generator"))


def _steering(work: WorkPlace, schemas: str) -> dict[str, Any] | None:
    if not os.path.isfile(work.steering):
        return None
    return form.held(work.steering, os.path.join(schemas, "steering.schema.json"), "the steering")
