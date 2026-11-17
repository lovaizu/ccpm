"""The order in which lay.py write lays an approved Proposal in a plugin, what it checks before it
changes a file, and how it puts back each file it changed where a later step fails."""

from __future__ import annotations

import os
import shutil
from collections.abc import Sequence
from dataclasses import dataclass

from events import hook_entries
from form import LanesFile, Proposal, write_lanes
from manifest import plugin_name

from lay import claude, hooks_file, laid, proposals, steps
from lay.check import Checked, check
from lay.claude import Validation
from lay.steps import Step


class Refused(Exception):
    """lay.py write laid nothing, and why: no such Proposal, the Steps changed since print, or
    validate didn't pass and each file was put back, with what it said."""


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


def write(plugin: str, proposal_id: str, root: str) -> Written:
    """Lays the Proposal of the ID in the plugin.

    Takes: the plugin's folder, the Proposal's ID, and Lane's folder, whose hooks/lane/ it copies.
    Gives: each file written, once `claude plugin validate` passes.
    Changes: in this order, each Step's file by `laid.lay`, hooks/hooks.json by
    `hooks_file.replace_entries`, hooks/lane/ by a copy of Lane's whole in place of what it held,
    and hooks/lanes.json by `form.write_lanes`; and, where validate doesn't pass or a step raises,
    each Step's file and each file under hooks/ put back as it was, a file it made removed, and
    an empty folder under hooks/ not kept.
    Refuses: Refused, where `proposals.find` finds no Proposal; where the Steps that `laid.unlaid`
    reads now, held as print held them, differ from those kept; and where validate
    doesn't pass. An error that a step raises comes out as it was raised, once each file is put
    back.
    Carries: S2 `UP->>L: write <plugin> <ID>` through each arrow from L to `L-->>UP: each file
    written, and to type /reload-plugins`.
    """
    kept = proposals.find(plugin, proposal_id)
    if kept is None:
        raise Refused(f"no Proposal for {plugin} has the ID {proposal_id}")
    if steps.as_held(laid.unlaid(plugin)[0], kept.proposal.routes) != kept.steps:
        raise Refused(
            f"the steps in {plugin} changed since lay.py print showed {proposal_id}; propose again"
        )
    checked = check(plugin, kept.proposal, kept.steps)
    # lay.py print keeps a Proposal only once check gives it Checked, with the same Steps.
    assert isinstance(checked, Checked)
    laid_steps = laid.as_laid(kept.steps, checked.sentences)
    order = [(lane.file, lane.step) for lane in kept.proposal.lanes]
    changed = sorted(
        (s for s in laid_steps if s not in kept.steps),
        key=lambda s: order.index((s.file, s.number)),
    )
    before = _held(plugin, [s.file for s in kept.steps])
    try:
        validation = _lay(plugin, kept.proposal, laid_steps, root)
    except BaseException:
        _put_back(plugin, before)
        raise
    files = (
        *dict.fromkeys(s.file for s in changed),
        "hooks/hooks.json",
        "hooks/lane/",
        "hooks/lanes.json",
    )
    roles = tuple(dict.fromkeys(lane.role for lane in kept.proposal.lanes))
    return Written(files, tuple(changed), roles, plugin_name(root), validation.said)


def _lay(plugin: str, proposal: Proposal, laid_steps: Sequence[Step], root: str) -> Validation:
    """Writes each file of the lay in its order, and gives what validate said once it passes;
    Refused where it doesn't."""
    written = laid.lay(plugin, laid_steps)
    hooks_file.replace_entries(plugin, hook_entries())
    copy = os.path.join(plugin, "hooks", "lane")
    if os.path.isdir(copy):
        shutil.rmtree(copy)
    shutil.copytree(
        os.path.join(root, "hooks", "lane"), copy, ignore=shutil.ignore_patterns("__pycache__")
    )
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), LanesFile(proposal, written))
    validation = claude.validate(plugin)
    if not validation.passed:
        raise Refused(f"claude plugin validate didn't pass: {validation.said}")
    return validation


# Each file that a lay may change, by its path from the plugin's folder, with its bytes and its
# mode.
Held = dict[str, tuple[bytes, int]]


def _held(plugin: str, files: Sequence[str]) -> Held:
    """Each Step's file and each file under hooks/, as they stand before a lay."""
    for folder, _, names in os.walk(os.path.join(plugin, "hooks")):
        files = [*files, *(os.path.relpath(os.path.join(folder, n), plugin) for n in names)]
    held: Held = {}
    for file in files:
        with open(os.path.join(plugin, file), "rb") as f:
            held[file] = (f.read(), os.stat(f.fileno()).st_mode)
    return held


def _put_back(plugin: str, held: Held) -> None:
    """hooks/ removed with all that the lay made in it, and each file written again as it was
    held, with each folder it lies in."""
    hooks = os.path.join(plugin, "hooks")
    # Made first, so that a lay that failed before it made hooks/ is put back alike.
    os.makedirs(hooks, exist_ok=True)
    shutil.rmtree(hooks)
    for file, (data, mode) in held.items():
        path = os.path.join(plugin, file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        os.chmod(path, mode)
