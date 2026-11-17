"""lay.py's command line: what each of its commands, types, steps, print, and write, takes, which
modules it joins, and what it prints with its exit code."""

from __future__ import annotations

import dataclasses
import json
import os
from collections.abc import Sequence
from typing import TextIO

from form import OutOfForm, proposal_form, read_proposal
from lanes import types
from manifest import plugin_name

from lay import laid, proposals, show, steps, write
from lay.check import Faults, check

# How to call lay.py, as it says where a command line isn't one of its commands.
USAGE = (
    "lay.py: give one of `types`, `steps <plugin>`, `print <plugin>` with the Proposal on standard"
    " input, or `write <plugin> <ID>`\n"
)


def main(argv: Sequence[str], stdin: TextIO, root: str) -> tuple[int, str, str]:
    """Runs one command of lay.py.

    Takes: the command line after `lay.py`; standard input, which only print reads; and Lane's
    folder.
    Gives, as the exit code, standard output, and standard error:
    - `types`: 0, with the JSON `{"types": [...], "proposal": <JSON Schema>}` from `lanes.types`
      and `form.proposal_form`, in the form that up's part names.
    - `steps <plugin>`: 0, with the JSON `{"steps": [...], "notes": [...]}` from `laid.unlaid`.
    - `print <plugin>`, with the Proposal on standard input: 0, with what `show.render` gives, once
      `form.read_proposal`, `laid.unlaid`, `steps.as_held`, and `check.check` take it and
      `proposals.keep` keeps it; 3, with the faults of the plugin's files, where a file of the
      plugin can't carry it, as up can't mend what the user must fix first; else 1, with the
      faults, where the Proposal can't stand.
    - `write <plugin> <ID>`: 0, with each file written and to type /reload-plugins, from
      `write.write`; 1, with why, where it refuses.
    - anything else: 2, with how to call lay.py.
    Changes: what `proposals.keep` and `write.write` change.
    Refuses: as Gives says, by its exit code.
    Carries: S1 `UP->>L: types`, `UP->>L: steps <plugin>`, `UP->>L: print (Proposal)`; S2
    `UP->>L: write <plugin> <ID>`; S3 `UP->>L: steps <plugin>`; and each `L-->>UP` answer.
    """
    command, args = (argv[0], list(argv[1:])) if argv else ("", [])
    if command == "types" and not args:
        listed = [dataclasses.asdict(each) for each in types()]
        return 0, json.dumps({"types": listed, "proposal": proposal_form()}) + "\n", ""
    if command == "steps" and len(args) == 1:
        read, notes = laid.unlaid(args[0])
        held = {
            "steps": [dataclasses.asdict(s) for s in read],
            "notes": [dataclasses.asdict(n) for n in notes],
        }
        return 0, json.dumps(held) + "\n", ""
    if command == "print" and len(args) == 1:
        return _print(os.path.abspath(args[0]), stdin.read())
    if command == "write" and len(args) == 2:
        return _write(os.path.abspath(args[0]), args[1], root)
    return 2, "", USAGE


def _print(plugin: str, text: str) -> tuple[int, str, str]:
    """lay.py print: the Proposal checked, kept, and shown."""
    try:
        proposal = read_proposal(text)
    except OutOfForm as e:
        return 1, "", "lay.py print: the Proposal is out of form:\n" + "\n".join(e.problems) + "\n"
    read = steps.as_held(laid.unlaid(plugin)[0], proposal.routes)
    checked = check(plugin, proposal, read)
    if isinstance(checked, Faults):
        code = 3 if checked.plugin else 1
        return code, "", "\n".join(checked.plugin or checked.proposal) + "\n"
    proposal_id = proposals.keep(plugin, proposal, read)
    shown = laid.as_laid(read, checked.sentences)
    return 0, show.render(proposal, shown, proposal_id, plugin_name(plugin)), ""


def _write(plugin: str, proposal_id: str, root: str) -> tuple[int, str, str]:
    """lay.py write: the Proposal laid, and each file written."""
    try:
        written = write.write(plugin, proposal_id, root)
    except write.Refused as e:
        return 1, "", f"lay.py write: laid nothing: {e}\n"
    lines = []
    for file in dict.fromkeys(s.file for s in written.steps):
        at = [s for s in written.steps if s.file == file]
        noun = "step" if len(at) == 1 else "steps"
        lines.append(
            f"Wrote {noun} {_joined([str(s.number) for s in at])} of {at[0].role} into {file}."
        )
    lines += [
        f"Wrote the checks of {_joined(list(written.roles))} into hooks/hooks.json.",
        "Wrote the lanes laid and the routes into hooks/lanes.json.",
        f"Put {written.lane}'s code in hooks/lane/.",
        "claude plugin validate passed.",
        "Type /reload-plugins, and the checks hold from your next prompt.",
    ]
    return 0, "\n".join(lines) + "\n", ""


def _joined(words: list[str]) -> str:
    """The words joined as a list in a sentence: `a, b and c`."""
    return words[0] if len(words) == 1 else f"{', '.join(words[:-1])} and {words[-1]}"
