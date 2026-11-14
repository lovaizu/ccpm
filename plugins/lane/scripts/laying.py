"""Decides which files laying a Proposal writes or replaces in the user's plugin, as one change:
each laid sentence in its Step, Lane's hook entries in `hooks/hooks.json` beside the user's own,
`hooks/lanes.json`, and `hooks/lane/`, a copy of Lane's code, after which `claude plugin validate`
must pass, or every file goes back as it was, as the principle Lane's part replaced whole says."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

from proposal import Proposal
from steps import Role


@dataclass(frozen=True)
class Laying:
    """What laying wrote: each line that `lay.py write` prints, such as `Wrote step 1 of write into
    skills/write/SKILL.md.`, or, where `claude plugin validate` failed, what it said."""

    lines: tuple[str, ...]
    validated: bool


def hook_entries(plugin_root: str) -> dict[str, list[dict[str, object]]]:
    """Lane's hook entries for the plugin, by event, each running the copy of the guard in the
    plugin's own `hooks/lane/`, as the principle The laid plugin runs alone says."""
    raise NotImplementedError("laying.hook_entries")


def lay(
    proposal: Proposal,
    found: Sequence[Role],
    plugin_root: str,
    lane_code: str,
    validate: Callable[[str], tuple[bool, str]],
) -> Laying:
    """Lays the Proposal into the plugin in the folder: takes out of each Step and each hook entry
    what the plugin's Laid names, writes each Lane's sentence where its Step doesn't say it
    already, Lane's hook entries, `hooks/lanes.json` with the new Laid, and a copy of the folder
    `lane_code` as `hooks/lane/`, and then runs `validate` on the plugin's folder. Where it fails,
    it puts back each file it changed. Leaves every other file of the plugin as it stands."""
    raise NotImplementedError("laying.lay")
