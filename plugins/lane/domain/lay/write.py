"""The order in which lay.py write lays an approved Proposal in a plugin, what it checks before it
changes a file, and how it puts back each file it changed where a later step fails."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass

from events import hook_entries
from form import LanesFile, write_lanes
from manifest import plugin_name
from runs import where

from lay import claude, hooks_file, laid, proposals
from lay.check import Checked, check
from lay.steps import Step


class Refused(Exception):
    """lay.py write laid nothing, and why: no such Proposal, its Run no longer waits, the Steps
    changed since print, or a step failed and each file was put back, with what failed."""


@dataclass(frozen=True)
class Written:
    """Each file that lay.py write wrote, by its path from the plugin's folder; each Step that it
    laid a sentence on, as it now reads, in the order of the Proposal's Lanes; each role whose Lanes
    it laid, in that order; Lane's name; and what claude plugin validate said."""

    files: tuple[str, ...]
    steps: tuple[Step, ...]
    roles: tuple[str, ...]
    lane: str
    validated: str


def write(plugin: str, proposal_id: str, session_id: str, root: str) -> Written:
    """Lays the Proposal of the ID in the plugin.

    Takes: the plugin's folder, the Proposal's ID, the session_id from CLAUDE_CODE_SESSION_ID, and
    Lane's folder, whose hooks/lane/ it copies.
    Gives: each file written, once `claude plugin validate` passes.
    Changes: in this order, each Step's file by `laid.lay`, hooks/hooks.json by
    `hooks_file.replace_entries`, hooks/lane/ by a copy of Lane's whole, and hooks/lanes.json by
    `form.write_lanes`; and, where a step fails or validate doesn't pass, each of them put back as
    it was.
    Refuses: Refused, where `proposals.find` finds no Proposal; where `runs.where` shows that the
    Run of up that showed the ID has ended or showed a later one; where the Steps read now differ
    from those kept; and where a step fails or validate doesn't pass.
    Carries: S2 `UP->>L: write <plugin> <ID>` through each arrow from L to `L-->>UP: each file
    written, and to type /reload-plugins`.
    """
    kept = proposals.find(plugin, proposal_id)
    if kept is None:
        raise Refused(f"no Proposal of {plugin_name(plugin)} has the ID {proposal_id}")
    waiting = [
        run
        for run in where(root, session_id).runs
        if run.skill == "up"
        and not run.ended
        and run.shown[-1:]
        and run.shown[-1].proposal_id == proposal_id
    ]
    if not waiting:
        raise Refused(
            f"no run of up in this conversation waits to lay {proposal_id}; propose again"
        )
    checked = check(plugin, kept.proposal, kept.steps)
    if not isinstance(checked, Checked):
        raise Refused("\n".join(checked.proposal + checked.plugin))
    steps = laid.as_laid(kept.steps, checked.sentences)
    order = [(lane.file, lane.step) for lane in kept.proposal.lanes]
    changed = sorted(
        (s for s in steps if s not in kept.steps), key=lambda s: order.index((s.file, s.number))
    )
    written = laid.lay(plugin, steps, _version(root))
    hooks_file.replace_entries(plugin, hook_entries())
    copy = os.path.join(plugin, "hooks", "lane")
    if os.path.isdir(copy):
        shutil.rmtree(copy)
    shutil.copytree(
        os.path.join(root, "hooks", "lane"), copy, ignore=shutil.ignore_patterns("__pycache__")
    )
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), LanesFile(kept.proposal, written))
    validation = claude.validate(plugin)
    if not validation.passed:
        raise Refused(f"claude plugin validate didn't pass: {validation.said}")
    files = (
        *dict.fromkeys(s.file for s in changed),
        "hooks/hooks.json",
        "hooks/lane/",
        "hooks/lanes.json",
    )
    roles = tuple(dict.fromkeys(lane.role for lane in kept.proposal.lanes))
    return Written(files, tuple(changed), roles, plugin_name(root), validation.said)


def _version(root: str) -> str:
    """Lane's version, as its plugin.json gives it."""
    with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return str(json.load(f)["version"])
