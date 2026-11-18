"""How Lane's sentences sit in a plugin's Steps: each sentence after the Step's own words, none
where the Step already says it word for word, so that a later Lane takes its own words out and
keeps the user's."""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from form import Laid, LaidSentence, read_lanes

from lay.steps import Step, items, read_steps


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
    Gives: each Step with each sentence that it still holds word for word, after a space, taken
    out, and a Note for each sentence that no Step holds, which the user changed: the Step of the
    sentence's number stays as it reads, and the Note names the sentence laid and, as `now`, that
    Step's last sentences, as many as the laid one holds, since Lane laid its sentence after the
    Step's own words. A sentence is sought in the Step of its number, then in each later Step of
    its file after the one that held the sentence before it, as a Step that the user added before
    it moves it down. A sentence ends at a `.`, `!`, or `?` outside backticks that a space
    follows.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: each Step without the text that the Laid names`, and S3 `L-->>UP: each
    Step without each sentence of the Laid that it still holds word for word`.
    """
    kept = list(steps)
    notes = []
    after: dict[str, int] = {}
    for sentence in sorted(laid.sentences, key=lambda x: (x.file, x.step)):
        held = _holding(kept, sentence, after.get(sentence.file, 0))
        if held is None:
            notes.extend(_changed(kept, sentence))
            continue
        step = kept[held]
        at = step.text.rfind(f" {sentence.text}")
        text = step.text[:at] + step.text[at + 1 + len(sentence.text) :]
        kept[held] = dataclasses.replace(step, text=text)
        after[sentence.file] = step.number
    return tuple(kept), tuple(notes)


def _holding(steps: Sequence[Step], sentence: LaidSentence, after: int) -> int | None:
    """The index of the Step that holds the sentence after a space: the Step of its number, else
    the first later Step of its file after the number `after`; None where none does."""
    ours = [(i, s) for i, s in enumerate(steps) if s.file == sentence.file]
    first = [i for i, s in ours if s.number == sentence.step]
    later = [i for i, s in ours if s.number > max(after, sentence.step)]
    for i in first + later:
        if f" {sentence.text}" in steps[i].text:
            return i
    return None


def _changed(steps: Sequence[Step], sentence: LaidSentence) -> list[Note]:
    """The Note of a sentence that no Step holds, on the Step of its number, none where the file
    holds no such Step."""
    return [
        Note(s.file, s.number, sentence.text, _last_sentences(s.text, len(_starts(sentence.text))))
        for s in steps
        if (s.file, s.number) == (sentence.file, sentence.step)
    ]


def _starts(text: str) -> list[int]:
    """Where each sentence of the text starts: at its beginning, and after each `.`, `!`, or `?`
    outside backticks that a space follows."""
    starts = [0]
    quoted = False
    for i, char in enumerate(text):
        quoted = quoted != (char == "`")
        if not quoted and char in ".!?" and text[i + 1 : i + 2] == " ":
            starts.append(i + 2)
    return starts


def _last_sentences(text: str, count: int) -> str:
    """The text's last sentences, as many as `count`, or the whole text where it holds fewer."""
    return text[_starts(text)[-count:][0] :]


def unlaid(plugin: str) -> tuple[tuple[Step, ...], tuple[Note, ...]]:
    """Each Step of the plugin without the text that its Laid names.

    Takes: the plugin's folder.
    Gives: what `strip` gives of the Steps that `steps.read_steps` reads, by the Laid of the
    plugin's hooks/lanes.json, none where it holds no such file, as Lane never laid in it.
    Changes: nothing.
    Refuses: what `steps.read_steps` refuses, and form.OutOfForm where hooks/lanes.json is out of
    its form.
    Carries: S1 `L->>ST: reads each Step` and `L->>LS: reads the Laid`, S2's check that the Steps
    read as print read them, and S3's reading of the Laid and each Step.
    """
    path = os.path.join(plugin, "hooks", "lanes.json")
    laid = read_lanes(path).laid if os.path.isfile(path) else Laid(())
    return strip(read_steps(plugin), laid)


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


def lay(plugin: str, steps: Sequence[Step]) -> Laid:
    """Writes each Step as laid in place of what the Laid added.

    Takes: the plugin's folder, each Step as it will read once laid, its own words first, as
    `as_laid` gives it.
    Gives: the new Laid, which names the text after each Step's own words, as `unlaid` reads them
    before the lay.
    Changes: each file of the plugin that holds a Step whose text changes.
    Refuses: OSError, where a file can't be written, so that lay.py write puts back each file.
    Carries: S2 `L->>ST: writes each Lane's sentence in place of the Laid's`.
    """
    own = {(step.file, step.number): step.text for step in unlaid(plugin)[0]}
    written = tuple(
        LaidSentence(step.file, step.number, step.text[len(own[(step.file, step.number)]) + 1 :])
        for step in steps
        if step.text != own[(step.file, step.number)]
    )
    for file in dict.fromkeys(step.file for step in steps):
        _write(plugin, file, {step.number: step.text for step in steps if step.file == file})
    return Laid(written)


def _write(plugin: str, file: str, texts: Mapping[int, str]) -> None:
    """Writes the file of the plugin with each Step that the texts name, by its number, as they
    give it, where one of them changes."""
    path = os.path.join(plugin, file)
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    changed = [(i, n) for i, n, text in items(lines) if texts.get(n, text) != text]
    for index, number in changed:
        lines[index] = f"{number}. {texts[number]}"
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
