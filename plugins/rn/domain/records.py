"""A round's records checked before the role that wrote one gives its result, as Q11 of the plugin
best practice asks of what a machine can see: the generator's Making record, each file it names
made, each intent it names one of the turn's kind, and the try record written after it where it
names commands; and an evaluator's Answers, each intent of its group answered once, none outside
it, and each line it quotes standing in what the evaluator may read. Each check gives the result
the role gives."""

from __future__ import annotations

import os
import re
from typing import Any

import files
import practices
import runs
import starts
import trees
from starts import Stop

SPACE = re.compile(r"\s+")


def flat(text: str) -> str:
    """The text with each run of blanks read as one space, as a line quoted may wrap otherwise."""
    return SPACE.sub(" ", text).strip()


def turn_at(path: str) -> tuple[str, str, dict[str, Any], bool]:
    """The run, the round, the deliverable at hand and whether its turn is of how it reads, of the
    record at the path; refuses, by Stop, a record outside the round of the turn at hand."""
    round_ = os.path.dirname(os.path.normpath(path))
    turn = os.path.dirname(round_)
    run = os.path.dirname(os.path.dirname(turn))
    tree = starts.the_tree(run)
    n = trees.at_hand(tree)
    d = trees.numbered(tree, n) if n is not None else None
    reading = d is not None and starts.reads(d)
    if d is None or runs.turn_of(run, d["path"], reading) != turn:
        raise Stop(f"{path} lies in no round of the turn at hand")
    if runs.last(turn) != round_:
        raise Stop(f"{path} lies in no round of the turn at hand")
    return run, round_, d, reading


def record(path: str) -> str:
    """Checks the record at the path, a Making record or an Answers: what the role reads, with the
    result it gives. Refuses, by Stop, a record that doesn't hold."""
    run, round_, d, reading = turn_at(path)
    data = starts.practice_of(run, starts.turn_kind(d, reading))
    if os.path.basename(path) == runs.MADE:
        return made(path, run, round_, data)
    matched = runs.ANSWERS.fullmatch(os.path.basename(path))
    if matched is None:
        raise Stop(f"{path} is neither generator.json nor evaluator-G<n>.json")
    return judged(path, round_, d, data, matched[1])


def made(path: str, run: str, round_: str, data: dict[str, Any]) -> str:
    """Checks the Making record at the path."""
    record_ = files.load(path, "making-record")
    found = [
        f"{p}, which it names as made, isn't there"
        for p in record_["made"]
        if not os.path.exists(p)
    ]
    ids = practices.intents(data)
    for each in record_["decided"] + record_["open"]:
        if each["intent"] not in ids:
            found.append(f"{each['intent']} is no intent of the best practice")
    tried = os.path.join(round_, runs.TRY)
    late = not os.path.isfile(tried) or os.path.getmtime(tried) < os.path.getmtime(path)
    if record_.get("commands") and late:
        found.append(f"no try record follows it: run throwaway.py {run}")
    if found:
        raise Stop("\n".join(found))
    given = "open" if record_["open"] else "made"
    return f"rn: the Making record holds. {starts.GIVE.format(result=given)}: {path} holds."


def judged(path: str, round_: str, d: dict[str, Any], data: dict[str, Any], group: str) -> str:
    """Checks the Answers at the path of the group's evaluator."""
    answers = files.load(path, "answers")
    groups = practices.groups(data)
    number = int(group[1:])
    if number > len(groups):
        raise Stop(f"the best practice has no group {group}")
    ids = groups[number - 1]
    given = [a["question"] for a in answers["met"] + answers["not_met"]]
    twice = {q for q in given if given.count(q) > 1}  # pragma: no mutate
    found = [f"{q} is answered more than once" for q in sorted(twice)]
    found += [
        f"{q} is no intent of {group}"
        for q in given + [o["question"] for o in answers["open"]]
        if q not in ids
    ]
    found += [f"{q} has no answer" for q in ids if q not in given]
    record_ = runs.made_of(round_) or {"made": []}
    texts = []
    for p in [*record_["made"], *d.get("inputs", []), os.path.join(round_, runs.TRY)]:
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                texts.append(flat(f.read()))
    for each in answers["met"]:
        for quoted in each["lines"]:
            if not any(flat(quoted) in t for t in texts):
                said = f"{each['question']} quotes a line that stands in none of what you read"
                found.append(f"{said}: {quoted}")
    if found:
        raise Stop("\n".join(found))
    result = "open" if answers["open"] else "more" if answers["not_met"] else "good"
    return f"rn: the Answers hold. {starts.GIVE.format(result=result)}: {path} holds."
