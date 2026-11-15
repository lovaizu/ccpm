"""lay.py's command line: what each of its commands, types, steps, print, and write, takes, which
modules it joins, and what it prints with its exit code."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TextIO


def main(
    argv: Sequence[str], stdin: TextIO, env: Mapping[str, str], root: str
) -> tuple[int, str, str]:
    """Runs one command of lay.py.

    Takes: the command line after `lay.py`; standard input, which only print reads; the environment,
    whose CLAUDE_CODE_SESSION_ID names the conversation; and Lane's folder.
    Gives, as the exit code, standard output, and standard error:
    - `types`: 0, with the JSON `{"types": [...], "proposal": <JSON Schema>}` from `lanes.types`
      and `form.proposal_form`, in the form that up's part names.
    - `steps <plugin>`: 0, with the JSON `{"steps": [...], "notes": [...]}` from `steps.read_steps`,
      `laid_copy.read_laid`, and `laid.strip`.
    - `print <plugin>`, with the Proposal on standard input: 0, with what `show.render` gives, once
      `form.read_proposal` and `check.check` take it and `proposals.keep` keeps it; 1, with the
      faults, where the Proposal can't stand; 3, with the faults, where a file of the plugin can't
      carry it.
    - `write <plugin> <ID>`: 0, with each file written and to type /reload-plugins, from
      `write.write`; 1, with why, where it refuses.
    - anything else: 2, with how to call lay.py.
    Changes: what `proposals.keep` and `write.write` change.
    Refuses: as Gives says, by its exit code.
    Carries: S1 `UP->>L: types`, `UP->>L: steps <plugin>`, `UP->>L: print (Proposal)`; S2
    `UP->>L: write <plugin> <ID>`; S4 `UP->>L: steps <plugin>`; and each `L-->>UP` answer.
    """
    raise NotImplementedError
