"""The order in which lay.py write lays an approved Proposal in a plugin, what it checks before it
changes a file, and how it puts back each file it changed where a later step fails."""

from __future__ import annotations

from dataclasses import dataclass


class Refused(Exception):
    """lay.py write laid nothing, and why: no such Proposal, its Run no longer waits, the Steps
    changed since print, or a step failed and each file was put back, with what failed."""


@dataclass(frozen=True)
class Written:
    """Each file that lay.py write wrote, by its path from the plugin's folder."""

    files: tuple[str, ...]


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
    raise NotImplementedError("write.write")
