"""The result written where the call says once the first user has ended, from the last replies
alone: each item's lines and each need from the first user's last reading, and the choices from the
generator's last claim; then the run's folder removed, the result alone staying."""

from __future__ import annotations

import os
import shutil
from typing import Any

import call
import folder
import forms
import parts as work_parts
import prompts
from prompts import FIRST_USER, GENERATOR

# What the calling AI does where a reply the result is written from is missing or out of its form:
# a call again starts the role again, which writes it.
AGAIN = "call turn again with the same call, which goes on from what the run's folder holds"


def named(line: str, made: list[str]) -> str:
    """The lines with their file named as it is among the files made, each by the name the CCS
    gives it or the folder it is in, as the first user is given the work by whole paths and the
    calling AI reads the result by the CCS's names; the reading's check has held each range to a
    file of the work."""
    found = forms.LINES.match(line)
    assert found
    real = os.path.realpath(found.group(1))
    path = next(m for m in made if os.path.realpath(m) == real)
    return path + line[found.end(1) :]


def ended(run: dict[str, Any]) -> dict[str, str]:
    """Writes the result of the run and removes its folder; gives the result as the call names it.
    Stops, writing nothing, where the first user's last reading is not there or not filled, or the
    generator's last claim is not there or its choices are out of their form."""
    reading = prompts.reading(run)
    if reading is None:
        raise call.Stop(
            f"turn: the first user's reading at {folder.reply(run['result'], FIRST_USER)} is not"
            f" there or not filled; {AGAIN}"
        )
    choices = prompts.choices(prompts.last(run, GENERATOR) or "")
    if choices is None:
        raise call.Stop(
            f"turn: the generator's claim at {folder.reply(run['result'], GENERATOR)} is not there"
            f" or its choices are out of their form; {AGAIN}"
        )
    given = {forms.key_of(i): i for i in reading}
    # Each item in the checklists' order, as the reading gave it, named as the CCS names it.
    answered = [dict(given[forms.key_of(i)], **i) for i in run["items"]]
    # What was made: each file the CCS names, and each file the generator made in a folder it
    # names, from that folder's name.
    made = work_parts.files(run["work"])
    for item in answered:
        if "lines" in item:
            item["lines"] = [named(line, made) for line in item["lines"]]
    folder.write(
        run["call"]["result"],
        {
            "work": made,
            "items": [i for i in answered if "lines" in i],
            "left": [i for i in answered if "need" in i],
            "chosen": choices,
        },
    )
    kept = folder.folder(run["result"])
    shutil.rmtree(kept)
    # turn's folder goes once it holds no other run, so no empty folder is left in the repository.
    if not os.listdir(os.path.dirname(kept)):
        os.rmdir(os.path.dirname(kept))
    return {"returned": run["call"]["result"]}
