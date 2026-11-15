"""How Lane's sentences sit in a plugin's Steps: each sentence after the Step's own words, none
where the Step already says it word for word, so that a later Lane takes its own words out and
keeps the user's."""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from form import Laid, LaidSentence

from lay.steps import Step, items


@dataclass(frozen=True)
class Note:
    """A sentence that Lane laid and the user changed, kept as the user's words."""

    file: str
    step: int
    laid: str
    now: str


def strip(steps: Sequence[Step], laid: Laid) -> tuple[tuple[Step, ...], tuple[Note, ...]]:
    """Each Step without the text that the Laid names.

    Takes: the Steps as the files hold them, and the Laid.
    Gives: each Step with each sentence that it still holds word for word taken out, and a Note
    for each sentence that the user changed, which stays in the Step as theirs.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: each Step without the text that the Laid names`, S4's loop over each
    sentence that the Laid added, and `L-->>UP: each Step that remains, with the notes`.
    """
    return tuple(steps), ()


def as_laid(steps: Sequence[Step], sentences: Mapping[tuple[str, int], str]) -> tuple[Step, ...]:
    """Each Step as it will read once laid.

    Takes: the Steps without the Laid's text, and each Lane's sentence by its Step's file and
    number.
    Gives: each Step with its sentences after its own words, leaving out a sentence that the Step
    already says.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: the Routes, each Step as it'll read, and the ID`.
    """
    laid = []
    for step in steps:
        sentence = sentences.get((step.file, step.number))
        if sentence and sentence not in step.text:
            step = dataclasses.replace(step, text=f"{step.text} {sentence}")
        laid.append(step)
    return tuple(laid)


def lay(plugin: str, steps: Sequence[Step], version: str) -> Laid:
    """Writes each Step as laid in place of what the Laid added.

    Takes: the plugin's folder, each Step as it will read once laid, and Lane's version.
    Gives: the new Laid, with each sentence written.
    Changes: each file of the plugin that holds a Step whose text changes.
    Refuses: OSError, where a file can't be written, so that lay.py write puts back each file.
    Carries: S2 `L->>ST: writes each Lane's sentence in place of the Laid's`.
    """
    written = []
    for file in dict.fromkeys(step.file for step in steps):
        path = os.path.join(plugin, file)
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        texts = {step.number: step.text for step in steps if step.file == file}
        changed = [
            (index, number, text, texts[number])
            for index, number, text in items(lines)
            if texts.get(number, text) != text
        ]
        for index, number, text, now in changed:
            written.append(LaidSentence(file, number, now[len(text) + 1 :]))
            lines[index] = f"{number}. {now}"
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
    return Laid(version, tuple(written))
