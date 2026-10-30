"""What each role of a run is given when it first runs turn.py, and the last reply each wrote,
checked against its form: every path whole, as a role's commands and hooks run from the session's
working folder, which the calling AI may move with `cd`, and none of the run's own files, as a
role's lane lets it read anything under a folder it is given."""

from __future__ import annotations

import os
from typing import Any

import call
import folder
import forms
import parts as work_parts

GENERATOR = "generator"
FIRST_USER = "first-user"
# The form each role's reply is checked in, and the command that checks it, by the role; each
# command is named as its form's file is.
FORMS = {GENERATOR: forms.CLAIM, FIRST_USER: forms.FIRST_READING}
CHECKS = {GENERATOR: "claim", FIRST_USER: "reading"}


def laid_out(result: str) -> dict[str, Any]:
    """The run of the result, laid out from its CCS as it is now, from the folder the call was made
    from, with the result as a whole path: an answer kept in the CCS may have added a file, which
    each role is given from then on; stops where no run is going, or turn cannot take the CCS."""
    run = call.laid_out(folder.going(result))
    run["result"] = os.path.abspath(run["call"]["result"])
    return run


def absolute(paths: list[str]) -> list[str]:
    """The paths as whole paths in the folder the call was made from, where turn.py runs."""
    return [os.path.abspath(p) for p in paths]


def without_run_files(paths: list[str], result: str, apart: tuple[str, ...] = ()) -> list[str]:
    """The paths, in their order, without the run's own files: the result, and turn's folder at the
    root, which holds each run's call and replies; and without each file kept `apart`, as the CCS
    is from the first user. A path that is one of them, or inside one, is left out, and a folder
    holding one is given as its entries, sorted, the one on the way opened the same way: a role's
    lane lets it read anything under a folder it is given, and the first user is not to read the
    generator's reply nor the CCS. A path met again, as a checklist the CCS also names, is given
    once."""
    left_out = {os.path.realpath(p) for p in (result, *apart)}
    left_out.add(os.path.join(folder.root(result), ".turn"))
    # The folders a folder given is opened on the way to.
    inside = {os.path.dirname(p) for p in left_out}

    def ours(path: str) -> bool:
        real = os.path.realpath(path)
        return any(real == p or real.startswith(p + os.sep) for p in left_out)

    def opened(path: str) -> list[str]:
        real = os.path.realpath(path)
        if not any(real == f or f.startswith(real + os.sep) for f in inside):
            return [path]
        entries = [os.path.normpath(os.path.join(path, e)) for e in sorted(os.listdir(path))]
        return [p for e in entries if not ours(e) for p in opened(e)]

    return list(dict.fromkeys(p for path in paths if not ours(path) for p in opened(path)))


def files(run: dict[str, Any], role: str, given: list[str]) -> dict[str, Any]:
    """The files of the run the role works on, which its lanes hold it to: what it reads, the work,
    the checklists, the items the caller asks of each part of the work, each by its checklist's
    whole path, where it replies, and the command that checks its reply."""
    return {
        "given": absolute(given),
        "work": absolute(run["work"]),
        "checklists": absolute(run["checklist"]),
        "each": [dict(i, checklist=os.path.abspath(i["checklist"])) for i in run["each"]],
        "reply": folder.reply(run["result"], role),
        "check": f"turn.py {CHECKS[role]} {run['result']}",
    }


def generator(run: dict[str, Any]) -> dict[str, Any]:
    """What the generator is given: the CCS and each file it names, the work among them; the call's
    test, the command it passes after changing the work, or None for none; each item the first
    user's last reading left without Good, with what the receiver would need to get it; the choices
    its own last claim named, which it keeps where the work still rests on them; and the run's
    result, by which it has turn.py print the parts of the work it makes."""
    made_from = without_run_files(run["given"], run["result"])
    return dict(
        files(run, GENERATOR, made_from),
        test=run["call"]["test"],
        needs=needs(run),
        chosen=chosen(run),
        result=run["result"],
    )


def first_user(run: dict[str, Any]) -> dict[str, Any]:
    """What the first user is given: the work, what the receiver has with it and the checklists;
    the receiver, their use, and the parts of the work as it stands; never the CCS nor any reply,
    as a reader shown the maker's claim finds the Good it was told to find."""
    given = without_run_files(run["readable"], run["result"], apart=(run["call"]["ccs"],))
    return dict(
        files(run, FIRST_USER, given), receiver=run["receiver"], use=run["use"], parts=parts(run)
    )


def parts(run: dict[str, Any]) -> list[str]:
    """The parts of the run's work as it stands, each as its lines in a file named by its whole
    path."""
    return work_parts.parts(absolute(run["work"]))


def last(run: dict[str, Any], role: str) -> str | None:
    """The last reply the role wrote, None where it wrote none."""
    try:
        with open(folder.reply(run["result"], role), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def problems(run: dict[str, Any], role: str, text: str) -> list[str]:
    """What is wrong with the role's reply, each said with what to give instead; empty where it is
    filled."""
    work = absolute(run["work"])
    return forms.check(text, JUDGED[role](run), work, FORMS[role], run["each"])


def mended(run: dict[str, Any]) -> list[dict[str, Any]]:
    """The items the generator's claim answers: on a mend, each item the first user's last reading
    left without Good alone, as an item not sent stands as it was; otherwise every item."""
    return [forms.named(i) for i in needs(run)] or run["items"]


def reading(run: dict[str, Any]) -> list[dict[str, Any]] | None:
    """The items of the first user's last reading, each at the lines of its Good or with what the
    receiver would need, as the reading gave them; None where no reading in its form is there."""
    text = last(run, FIRST_USER)
    filled = text is not None and not problems(run, FIRST_USER, text)
    data = forms.parsed(text, ("items",)) if filled else None
    return None if data is None else data["items"]


def needs(run: dict[str, Any]) -> list[dict[str, Any]]:
    """Each item the first user's last reading left without Good, with what the receiver would need,
    as the reading gave it; none where no reading in its form is there."""
    return [i for i in reading(run) or [] if "need" in i]


def chosen(run: dict[str, Any]) -> list[dict[str, str]]:
    """The choices the generator's last claim named; none where no claim naming them in their form
    is there."""
    found = choices(last(run, GENERATOR) or "")
    return [] if found is None else found


def choices(text: str) -> list[dict[str, str]] | None:
    """The choices a claim names, each with why; None where it is not a claim whose choices are in
    their form. Its items are not read, as they answer only what was sent to the generator then."""
    data = forms.parsed(text, ("items", "chosen"))
    if data is None or forms.choice_problems(data["chosen"]):
        return None
    return data["chosen"]


# The items each role's reply answers: the first user every item, whatever the last reading left.
JUDGED = {GENERATOR: mended, FIRST_USER: lambda run: run["items"]}
