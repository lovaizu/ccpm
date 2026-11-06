"""A work's rounds, as the Round, verification/round.json in the work's folder, holds each: its
phase and its questions in groups, one run of the evaluator for each; and the Answers of each run,
checked. A round's phase is a value of the run, settled here from the work's folder alone, so a run
that stopped keeps it, by this table:

| Rule | The last content round | It met every question | The last reading round since | Phase |
|---|---|---|---|---|
| R1 | none made | - | - | content |
| R2 | made on a design changed since | - | - | content |
| R3 | made on the design as it is | no | - | content |
| R4 | made on the design as it is | yes | none made | reading |
| R5 | made on the design as it is | yes | fell short | reading |
| R6 | made on the design as it is | yes | met every question | none: the work is made |

A content round asks the kind's questions, of what the work says and does; a reading round asks
those of how it reads, `refactor-doc` or `refactor-code`. A round's files are kept apart in
verification/<round>/ once the next is settled, so verification/ holds the last round's."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from typing import Any

import files
import practices
import runs

CONTENT, READING = "content", "reading"
# Whether a round of each phase asks how the work reads.
READS = {CONTENT: False, READING: True}
ROUND = "round.json"
# A run of the evaluator's Answers, by its group.
GROUP = re.compile(r"G\d+\.json")
# A line of the work, as `<path>:<line>` or `<path>:<from>-<to>`.
LINE = re.compile(r"(?P<path>.+):(?P<first>\d+)(?:-(?P<last>\d+))?")
OPEN = "open is the generator's, or the evaluator's in a reading round"


def phase(content: dict[str, Any] | None, reading_met: bool | None, design: str) -> str | None:
    """The phase of the next round, by the module's table, from the last content round, whether
    the last reading round since met every question, and the design as it is; None where the work
    is made."""
    if content is None or content["design"] != design or not content["met"]:
        return CONTENT
    return None if reading_met else READING


def design_hash(folder: str) -> str:
    """What the work's design tree is now, as its SHA-256; refuses, by files.Unreadable, a design
    file that is not there."""
    path = os.path.join(folder, runs.DESIGN)
    if not os.path.isfile(path):
        raise files.Unreadable(f"there is no design tree {path}")
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def folder_of(work: dict[str, Any]) -> str:
    """The folder of the work's rounds."""
    return os.path.join(work["folder"], runs.VERIFICATION)


def last(work: dict[str, Any]) -> dict[str, Any] | None:
    """The work's last Round; None where none was settled."""
    path = os.path.join(folder_of(work), ROUND)
    return files.load(path, "round") if os.path.exists(path) else None


def group_answers(work: dict[str, Any], settled: dict[str, Any]) -> list[dict[str, Any] | None]:
    """The Answers of each run of the evaluator in the round, in the order of its groups; None for
    a run that gave none, or none in form."""
    found: list[dict[str, Any] | None] = []
    for group in settled["groups"]:
        path = os.path.join(folder_of(work), f"{group['id']}.json")
        try:
            found.append(files.load(path, "answers"))
        except files.Unreadable:
            found.append(None)
    return found


def met(work: dict[str, Any], settled: dict[str, Any]) -> bool:
    """Whether every run of the evaluator in the round answered, met every question it was given,
    and left no point open."""
    return all(
        a is not None and not a["not_met"] and not a.get("open")
        for a in group_answers(work, settled)
    )


def settle(run: str) -> dict[str, Any] | None:
    """Settles the next round of the work the run is at, after the last, whose files it keeps apart;
    gives the Round, or None where the work is made, which leaves the last round as it is. Refuses,
    by files.Unreadable, a work not in its rounds, and a file it cannot read."""
    work = runs.current(runs.load(run))
    if work["at"] != runs.ROUNDS:
        raise files.Unreadable(f"no round of {work['kind']} is due: the work is at {work['at']}")
    design = design_hash(work["folder"])
    before = last(work)
    content, reading_met, number = None, None, 0
    if before is not None:
        number = before["round"]
        done = met(work, before)
        if READS[before["phase"]]:
            content, reading_met = before["content"], done
        else:
            content = {"design": before["design"], "met": done}
    at = phase(content, reading_met, design)
    if at is None:
        return None
    if before is not None:
        keep(work, number)
    name, kind = (runs.READING, work["reading"]) if READS[at] else (runs.STANDARD, work["kind"])
    standard = files.load(os.path.join(work["folder"], name), "standard")
    settled = {
        "round": number + 1,
        "phase": at,
        "design": design,
        "groups": practices.groups(standard, kind),
        "content": content,
        "reading_met": reading_met,
    }
    files.save(os.path.join(folder_of(work), ROUND), settled)
    return settled


def keep(work: dict[str, Any], number: int) -> None:
    """Moves each file of the round's folder into a folder of the round's number."""
    folder = folder_of(work)
    kept = os.path.join(folder, str(number))
    os.makedirs(kept, exist_ok=True)
    for name in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, name)):
            shutil.move(os.path.join(folder, name), os.path.join(kept, name))


def shortfalls(run: str, settled: dict[str, Any] | None) -> list[tuple[str, str]]:
    """Each point the round left open and each question it did not meet, in the order of the
    generator's run and then the evaluator's: its question, and a line that says it."""
    if settled is None:
        return []
    work = runs.current(runs.load(run))
    path = os.path.join(folder_of(work), runs.GENERATOR)
    generator = files.load(path, "answers") if os.path.exists(path) else None
    found = []
    for answers in [generator, *group_answers(work, settled)]:
        for a in (answers or {}).get("open", []):
            found.append((a["question"], f"{a['question']}, left open: {a['what']}"))
        for a in (answers or {}).get("not_met", []):
            found.append((a["question"], f"{a['question']}: {a['lacks']}"))
    return found


def where(run: str) -> str:
    """Where the rounds of the work the run is at stand: `none` before the first, `short` where the
    last fell short, `finished` where a reading round met every question, and `going` otherwise."""
    work = runs.current(runs.load(run))
    settled = last(work)
    if settled is None:
        return "none"
    if shortfalls(run, settled):
        return "short"
    if READS[settled["phase"]] and met(work, settled):
        return "finished"
    return "going"


def serving(tree: dict[str, Any], question: str) -> list[str]:
    """The decisions that serve the question, directly or through others, in the tree's order."""
    serves = {d.get("id"): d.get("contributes_to", []) for d in tree.get("decisions", [])}

    def reaches(at: str, seen: tuple[str, ...]) -> bool:
        return at not in seen and any(
            q == question or reaches(q, (*seen, at)) for q in serves.get(at, [])
        )

    return [d for d in serves if reaches(d, ())]


def line_fault(line: str, paths: list[str]) -> str:
    """How the line fails to lie in the work, or "" where it does: its form, its order, a file the
    work does not lie in or that is not there, and the file's length."""
    found = LINE.fullmatch(line)
    if not found:
        return f"{line} is not as <path>:<line> or <path>:<from>-<to>"
    path, first = found["path"], int(found["first"])
    end = int(found["last"] or first)
    if first < 1:
        return f"{line} begins before the file's first line"
    if end < first:
        return f"{line} ends before it begins"
    if path not in paths:
        return f"{line} lies in none of the work's paths"
    if not os.path.isfile(path):
        return f"{line} names a file that is not there"
    with open(path, encoding="utf-8") as f:
        count = len(f.read().splitlines())
    if end > count:
        return f"{line} runs past {path}'s {count} lines"
    return ""


def faults(answers: dict[str, Any], given: list[str], paths: list[str], opens: bool) -> list[str]:
    """Each fault of the Answers: a point open where the run may leave none; a question answered
    more than once, or not given; a point open on a question not given; each line that does not lie
    in the work; then each question given with no answer."""
    found = [] if opens or not answers.get("open") else [OPEN]
    named = [a["question"] for a in answers["met"] + answers["not_met"]]
    for q in dict.fromkeys(named):
        # q is taken from named, so it counts once or more there.
        if named.count(q) > 1:  # pragma: no mutate
            found.append(f"{q} is answered more than once")
        if q not in given:
            found.append(f"{q} was not given to this run")
    for a in answers.get("open", []):
        if a["question"] not in given:
            found.append(f"{a['question']}, left open, was not given to this run")
    for a in answers["met"]:
        for line in a["lines"]:
            fault = line_fault(line, paths)
            if fault:
                found.append(f"{a['question']}: {fault}")
    return found + [f"{q} has no answer" for q in given if q not in named]


def made_faults(work: dict[str, Any]) -> list[str]:
    """Each line of the work that holds a note of the template; and where the work is a best
    practice, each way a file of it is out of the form of one."""
    found = []
    for path in work["paths"]:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                left = practices.notes_left(f.read())
            found += [f"{path}:{n} holds a note of the template: delete it" for n in left]
    if work["kind"] != runs.META:
        return found
    for path in work["paths"]:
        try:
            runs.read_practice(path)
        except files.Unreadable as why:
            found.append(str(why).replace(f"the best practice {path}", path))
    return found


def result(answers: dict[str, Any], generator: bool, at: str) -> str:
    """The result the run gives on its Answers."""
    if generator:
        return "open" if answers.get("open") else "made"
    if not READS[at]:
        return "more" if answers["not_met"] else "met"
    if answers.get("open"):
        return "more"
    return "reword" if answers["not_met"] else "good"


def evaluator_values(run: str, work: dict[str, Any], settled: dict[str, Any]) -> list[str]:
    """The run values of each run of the evaluator in the round, a JSON line each."""
    name = runs.READING if READS[settled["phase"]] else runs.STANDARD
    return [
        json.dumps(
            {
                "run": run,
                "phase": settled["phase"],
                "work": work["paths"],
                "standard": os.path.join(work["folder"], name),
                "questions": g["questions"],
                "answers": os.path.join(folder_of(work), f"{g['id']}.json"),
            },
            ensure_ascii=False,
        )
        for g in settled["groups"]
    ]


def check(run: str, path: str) -> tuple[list[str], str, list[str]]:
    """Checks the Answers at the path, the generator's or a run of the evaluator's in the last round
    of the work the run is at: gives each fault, else the result the run gives and the run values it
    hands up, each run of the evaluator's for the generator's `made`, and the generator's for the
    evaluator. Refuses, by files.Unreadable, a path of no run of the round and a file it cannot
    read."""
    work = runs.current(runs.load(run))
    settled = last(work)
    if settled is None:
        raise files.Unreadable(f"no round of {work['kind']} was settled: run rounds.py round")
    name = os.path.relpath(path, folder_of(work))
    groups = {f"{g['id']}.json": g["questions"] for g in settled["groups"]}
    generator = name == runs.GENERATOR
    if not generator and not (GROUP.fullmatch(name) and name in groups):
        raise files.Unreadable(
            f"{path} is no Answers of round {settled['round']}: they lie at"
            f" {os.path.join(folder_of(work), runs.GENERATOR)} and"
            f" {os.path.join(folder_of(work), '<group>.json')}"
        )
    given = [q for g in settled["groups"] for q in g["questions"]] if generator else groups[name]
    answers = files.load(path, "answers")
    opens = generator or READS[settled["phase"]]
    found = faults(answers, given, work["paths"], opens)
    found += made_faults(work) if generator else []
    if found:
        return found, "", []
    gave = result(answers, generator, settled["phase"])
    if not generator:
        return [], gave, [runs.generator_values(run, work)]
    # The generator's run is made where it left no point open.
    return [], gave, [] if answers.get("open") else evaluator_values(run, work, settled)
