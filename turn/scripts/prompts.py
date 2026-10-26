"""What each role of a run is given as its prompt, and where it writes its reply: every path whole,
as a role's commands and hooks run from the session's working folder, which the calling AI may
move with `cd`, and none of the run's own files, as a role's lane lets it read anything under a
folder it is given."""

from __future__ import annotations

import os
from typing import Any

import forms
import state

GENERATOR = "turn:generator"
FIRST_USER = "turn:first-user"


def reply_path(result: str, agent: str) -> str:
    """Where the role writes its reply, read by the flow alone: in the run's folder, as a whole
    path."""
    return os.path.join(state.folder(result), f"{agent.partition(':')[2]}.json")


def absolute(paths: list[str]) -> list[str]:
    """The paths as whole paths in the folder the call was made from, where the flow runs."""
    return [os.path.abspath(p) for p in paths]


def without_run_files(paths: list[str], result: str, apart: tuple[str, ...] = ()) -> list[str]:
    """The paths, in their order, without the run's own files: the result, and turn's folder at the
    root, which holds each run's state and replies; and without each file kept `apart`, as the CCS
    is from the first user. A path that is one of them, or inside one, is left out, and a folder
    holding one is given as its entries, sorted, the one on the way opened the same way: a role's
    lane lets it read anything under a folder it is given, and the first user is not to read the
    generator's reply nor the CCS. A path met again, as a checklist the CCS also names, is given
    once."""
    left_out = {os.path.realpath(p) for p in (result, *apart)}
    left_out.add(os.path.join(state.root(result), ".turn"))
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


def checked(run: dict[str, Any]) -> list[str]:
    """What the orchestrator reads for its check: the CCS and every file it names but the work,
    as the CCS now names them."""
    read = [p for p in run["given"] if p not in run["work"]]
    return absolute(without_run_files(read, run["call"]["result"]))


def generator(run: dict[str, Any], sent_back: list[dict[str, Any]]) -> dict[str, Any]:
    """What the generator is given: the files it makes the work from, the work, the checklists,
    the call's test, the command it passes after changing the work, or None for none, each item
    sent back with what was found lacking, every answer the calling AI gave, the choices the last
    claim of the run named, which a generator started anew keeps where the work still rests on
    them, the run's result, by which it has turn.py print the parts of the work it makes, and where
    it replies."""
    result = run["call"]["result"]
    return {
        "given": absolute(without_run_files(run["given"], result)),
        "work": absolute(run["work"]),
        "checklists": absolute(run["checklist"]),
        "test": run["call"]["test"],
        "sent_back": sent_back,
        "answers": run.get("answers", []),
        "chosen": run.get("chosen", []),
        "result": os.path.abspath(result),
        "reply": reply_path(result, GENERATOR),
    }


def reader(run: dict[str, Any]) -> dict[str, Any]:
    """What the first user is given: what the receiver has with the work, the checklists, the
    receiver and their use, the parts of the work, and where it replies; not the CCS nor the
    generator's reply, as a reader shown the maker's claim finds the Good it was told to find."""
    result = run["call"]["result"]
    return {
        "given": absolute(without_run_files(run["readable"], result, apart=(run["call"]["ccs"],))),
        "work": absolute(run["work"]),
        "checklists": absolute(run["checklist"]),
        "receiver": run["receiver"],
        "use": run["use"],
        "parts": parts(run),
        "reply": reply_path(result, FIRST_USER),
    }


def remade(run: dict[str, Any]) -> dict[str, Any]:
    """What the first user, kept started, is sent once the work is made again: the work, its parts
    given anew, as a remake may add or take away a section, and where it replies."""
    return {
        "remade": absolute(run["work"]),
        "parts": parts(run),
        "reply": reply_path(run["call"]["result"], FIRST_USER),
    }


def parts(run: dict[str, Any]) -> list[str]:
    """The parts of the run's work as it stands, each as its lines in a file named by its whole
    path."""
    return forms.parts(absolute(run["work"]))
