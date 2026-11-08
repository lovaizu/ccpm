"""Decides, for each type of lane, its sentence, what it takes, whether it can stand, and what it's
given on a run. Each type lies in a module of its own, which holds its wording and its checks.

A type's module holds `WORDING`, its sentence, with each place that a take fills written as
`` `<place>` ``. Beside it, a module holds only what differs from the most types:
- `EARLIER`, each wording that Lane laid before, newest first, where Lane laid one.
- `COMMANDS`, the place whose takes are commands that the role may run, where it has one. The
  takes of every other place are paths.
- `TRACE`, true where the type is of the trace kind, naming the call that shows its step done.
- `END`, true where the guard checks the type as the role gives its result.
- `check`, where the type checks a call before it runs.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from types import ModuleType
from typing import Any, NamedTuple

import command

from lanes import (
    edit_only,
    end_by,
    end_when,
    every_item,
    follow_routes,
    hold,
    in_form,
    read_never,
    read_only,
    read_whole,
    run_only,
    run_step,
    test_after,
    write_only,
    write_step,
)

# Each type of lane, by its name.
TYPES: dict[str, ModuleType] = {
    m.__name__.rpartition(".")[2]: m
    for m in (
        read_only,
        read_never,
        read_whole,
        write_only,
        write_step,
        in_form,
        edit_only,
        run_only,
        run_step,
        hold,
        test_after,
        follow_routes,
        end_when,
        every_item,
        end_by,
    )
}
# The types a proposal may name. `lay.py write` lays follow_routes and end_by from the routes and
# from the lanes checked at the end.
PROPOSED = tuple(n for n in TYPES if n not in ("follow_routes", "end_by"))
# A place in a wording, such as `<output>`, with its name.
PLACE = re.compile(r"`<([a-z]+)>`")


class Unchecked(ValueError):
    """A lane that the guard can't check on this call, with what's wrong."""


class Call(NamedTuple):
    """A tool call of a role, as the hook input gives it."""

    # The tool's name, such as Bash.
    tool: str
    # The call's tool_input.
    input: Mapping[str, Any]
    # The folder the call runs in, from which a relative path in it reads.
    cwd: str


class Context(NamedTuple):
    """What a lane's check needs to know of the role beside its own takes."""

    # Each command the role may run, as it runs it, with any dependency's folder still written as
    # `${dependency:<name>}`.
    commands: tuple[str, ...]
    # Each path that read_only lets the role read beside its inputs.
    readable: tuple[str, ...]


def commands_place(name: str) -> str | None:
    """The lane's place whose takes are commands that the role may run, or None."""
    return getattr(TYPES[name], "COMMANDS", None)


def traced(name: str) -> bool:
    """Whether the lane is of the trace kind."""
    return getattr(TYPES[name], "TRACE", False)


def ends(name: str) -> bool:
    """Whether the guard checks the lane as the role gives its result."""
    return getattr(TYPES[name], "END", False)


def places(name: str) -> tuple[str, ...]:
    """The names of the lane's places, in the order its wording shows them."""
    return tuple(PLACE.findall(TYPES[name].WORDING))


def placed(name: str, takes: list[str]) -> dict[str, list[str]]:
    """The takes in each place of the lane: one in each, and the rest in the last."""
    names = places(name)
    found = {n: [t] for n, t in zip(names[:-1], takes)}
    if names:
        found[names[-1]] = list(takes[len(names) - 1 :])
    return found


def listed(things: list[str]) -> str:
    """The things, each in backticks, with commas between them and `or` before the last."""
    quoted = [f"`{t}`" for t in things]
    return quoted[0] if len(quoted) == 1 else ", ".join(quoted[:-1]) + " or " + quoted[-1]


def sentence(name: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with the takes in each place."""
    return _made(TYPES[name].WORDING, name, takes)


def earlier(name: str, takes: list[str]) -> list[str]:
    """The lane's sentence in each wording that Lane laid before the current one, newest first."""
    return [_made(w, name, takes) for w in getattr(TYPES[name], "EARLIER", ())]


def _made(wording: str, name: str, takes: list[str]) -> str:
    found = placed(name, takes)
    return PLACE.sub(lambda m: listed(found[m[1]]), wording)


def stands(name: str, takes: list[str]) -> list[str]:
    """What keeps the lane from standing with the takes, none where it can stand.

    A lane stands with a take for each of its places, no empty take, a value given for the start
    as a part of a take only in a command, and a dependency's folder only in a command.
    """
    names = places(name)
    if len(takes) < len(names):
        return [
            (
                f"{name} takes a thing for each of its places, {' and '.join(names)}, and is given"
                f" {len(takes)}"
            )
        ]
    faults = []
    if any(not t.strip() for t in takes):
        faults.append(f"{name} is given an empty thing")
    for where, things in placed(name, takes).items():
        if where == commands_place(name):
            continue
        for thing in things:
            for value in command.values(thing):
                if thing != "{" + value + "}":
                    faults.append(
                        f"{name} holds the value {{{value}}} as a part of `{thing}`, and Lane"
                        " matches only a command by its parts"
                    )
            for dependency in command.dependencies(thing):
                faults.append(
                    f"{name} names the dependency {dependency} in `{thing}`, and a dependency's"
                    " folder stands only in a command"
                )
    return faults


def given(
    name: str,
    takes: list[str],
    values: dict[str, list[str] | None],
    root: str,
    project: str,
) -> dict[str, list[str]] | None:
    """What the lane takes in each place on a run, or None where the start gives null for a value
    that a path takes, so that the lane lets the call through.

    Each value and the plugin's folder go into a path, which reads from the project's folder. A
    command reads as `command.expanded` gives it, so that a value of null leaves it out. The lane is
    one that `stands`.

    It raises Unchecked where a take names a value that the start wasn't given, or given empty.
    """
    found: dict[str, list[str]] = {}
    for where, things in placed(name, takes).items():
        found[where] = []
        for thing in things:
            for value in command.values(thing):
                _check_value(value, values)
            if where == commands_place(name):
                found[where] += command.expanded(thing, root, values)
                continue
            texts = _texts(thing, values)
            if texts is None:
                return None
            found[where] += [_path(t, root, project) for t in texts]
    return found


def _check_value(name: str, values: dict[str, list[str] | None]) -> None:
    if name not in values:
        raise Unchecked(f"the start was given no value `{name}`")
    if values[name] is not None and not any(values[name] or []):
        raise Unchecked(f"the start was given `{name}` empty")


def _texts(thing: str, values: dict[str, list[str] | None]) -> list[str] | None:
    """The texts that a whole take stands for: a value's non-empty texts, or the take itself."""
    found = command.VALUE.fullmatch(thing)
    if not found:
        return [thing]
    texts = values[found[1]]
    return None if texts is None else [t for t in texts if t]


def _path(text: str, root: str, project: str) -> str:
    return os.path.normpath(os.path.join(project, text.replace(command.ROOT, root)))


def called_path(call: Call) -> str | None:
    """The absolute path that a Read, Grep, Write, Edit, or NotebookEdit call names, read from the
    folder the call runs in, or None for another tool. A Grep given no path reads its folder."""
    if call.tool in ("Read", "Write", "Edit"):
        named = call.input.get("file_path")
    elif call.tool == "NotebookEdit":
        named = call.input.get("notebook_path")
    elif call.tool == "Grep":
        named = call.input.get("path") or "."
    else:
        return None
    if not isinstance(named, str):
        raise Unchecked(f"the {call.tool} call names no path that Lane reads")
    return os.path.normpath(os.path.join(call.cwd, named))


def under(path: str, folders: list[str]) -> bool:
    """Whether the path is one of the files or folders, or lies under one of them."""
    real = os.path.realpath(path)
    for folder in folders:
        top = os.path.realpath(folder)
        if real == top or real.startswith(top.rstrip(os.sep) + os.sep):
            return True
    return False
