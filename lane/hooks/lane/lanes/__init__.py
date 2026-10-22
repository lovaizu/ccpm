"""The lanes lane lays, one module each holding its action, its wording as the README's Lanes writes
it, the tools it watches and its check; and the lanes a hook's command lays, each a sentence of a
subagent's step with the check that notices a drift from it.

A lane is held on a tool call, the PreToolUse event, or, where its module names the events, on the
subagent about to end, the SubagentStop event, or on both; each event's script runs the lanes held
on it. A lane's check, `drifts(call, takes, root)`, is given the call, or how the subagent ends,
what the lane takes and the plugin's folder, where a lane finds a file of the plugin it takes, such
as in_form's form; it gives whether the call drifts, or, where it says more than the sentence, the
point it drifts by, "" for none. A lane's module may name, beside its action, wording and check,
the events it is held on, how many of the things it takes its sentence shows, and the most things
it takes.

A hook's command gives the subagent as `<plugin>:<name>`, as Claude Code gives it in the event's
agent_type, and each lane as `<step>:<lane>:<what it takes>`, the things taken joined by commas. A
thing taken written `{<name>}` is given for each run, and put in before the lane's check, as
started.py reads it."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from typing import Any

import call
import hook
import started
import step

from lanes import (
    as_printed,
    end_when,
    every_item,
    follow_next,
    hands_off,
    in_form,
    read_only,
    read_whole,
    start_with,
    test_after,
    wait_for,
    write_only,
)

LANES = {
    "start_with": start_with,
    "read_only": read_only,
    "read_whole": read_whole,
    "write_only": write_only,
    "in_form": in_form,
    "hands_off": hands_off,
    "test_after": test_after,
    "as_printed": as_printed,
    "follow_next": follow_next,
    "wait_for": wait_for,
    "end_when": end_when,
    "every_item": every_item,
}
# Where a wording shows what the lane takes, in quotes.
TAKEN = re.compile(r"`<[a-z]+>`")
# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
AGENT = re.compile(rf"{NAME}:{NAME}")
LANE = re.compile(r"(?P<step>[0-9]+):(?P<lane>[a-z_]+):(?P<takes>.*)")


def held_on(lane: str) -> tuple[str, ...]:
    """The events the lane is held on: those its module names, PreToolUse alone where it names
    none."""
    return getattr(LANES[lane], "EVENTS", ("PreToolUse",))


def slots(lane: str) -> int:
    """How many places the lane's wording shows for what it takes."""
    return len(TAKEN.findall(LANES[lane].WORDING))


def shown(lane: str) -> int | None:
    """How many of the things the lane takes its sentence shows, None for all."""
    return getattr(LANES[lane], "SHOWN", None)


def sentence(lane: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with the things it shows put in, one in each place in order,
    the last place taking the rest, each thing in quotes of its own, listed with commas and `or`
    before the last; of a lane that holds more than it shows, such as wait_for, the things it shows
    alone."""
    last, showing = slots(lane) - 1, takes[: shown(lane)]
    parts = iter([*([t] for t in showing[:last]), showing[last:]])

    def listed(_: re.Match[str]) -> str:
        quoted = [f"`{t}`" for t in next(parts)]
        return " or ".join(filter(None, [", ".join(quoted[:-1]), quoted[-1]]))

    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(listed, LANES[lane].WORDING)


def alone(lane: str) -> int:
    """How many of the first things the lane takes stand each alone in a place of its sentence:
    those before its last place, which takes the rest; of a lane that holds more than it shows,
    such as wait_for, the things it shows."""
    showing = shown(lane)
    return slots(lane) - 1 if showing is None else showing


def fits(lane: str, takes: list[str]) -> bool:
    """Whether the lane takes so many things: one or more for each place its wording shows, the last
    taking the rest; of a lane that holds more than it shows, one or more after those it shows; and
    no more than the most its module names, where it names one."""
    showing, most = shown(lane), getattr(LANES[lane], "MOST", len(takes))
    least = slots(lane) if showing is None else showing + 1
    # Told by membership in the counts it takes, as an order comparison such as `<=` against a most
    # that is also the least would be told from `==` by no count, and a mutant making it one would
    # pass every test.
    return len(takes) in range(least, most + 1)


def word(number: int, lane: str, takes: list[str]) -> str:
    """The lane as a hook's command gives it."""
    return f"{number}:{lane}:{','.join(takes)}"


class Laid:
    """A lane laid on a step of a subagent of the plugin at root."""

    def __init__(self, root: str, agent: str, number: int, lane: str, takes: list[str]) -> None:
        self.root, self.agent = root, agent
        self.plugin, self.name = agent.split(":")
        self.number, self.lane, self.takes = number, lane, takes

    def check(self, event: dict[str, Any]) -> list[str]:
        """The lane's sentence where the call drifts from it, as the subagent reads its step, with
        the point it drifts by on the next line where its check gives one; where the step no longer
        says it, that lane:up must be run again; nothing otherwise."""
        # A lane held as the subagent ends lets it end where what it did is not known, or where,
        # told before, it has answered with words alone, so it is told and never held for good.
        end = call.ended(event) if event["hook_event_name"] in ("SubagentStop",) else None
        if end is not None and (end.made is None or end.answered):
            return []
        said = sentence(self.lane, self.takes)
        if not step.holds(self.root, self.name, self.number, said):
            gone = f"step {self.number} of {self.name} no longer says: {said}"
            again = f"lane:up must be run again on {self.plugin}, so its lanes match its steps"
            return [f"{gone} Stop here and reply that {again}."]
        # A lane taking a thing given for each run lets every call through until the subagent
        # has been given it.
        named = started.names(self.takes)
        run = self.run_values(event) if named else {}
        if not set(named) <= set(run):
            return []
        # Each lane's check takes what its event gives: the call, or how the subagent ends.
        lane: Any = LANES[self.lane]
        acted = call.read(event) if end is None else end
        each = started.resolved(self.takes, run, alone(self.lane))
        if self.lane in ("read_only",):
            each = [[*inputs, *self.forms()] for inputs in each]
        drift = next(filter(None, (lane.drifts(acted, t, self.root) for t in each)), "")
        if not drift:
            return []
        told = [step.expanded(said, self.root), *(started.told(n, run[n]) for n in named)]
        return ["\n".join([*told, *([drift] if isinstance(drift, str) else [])])]

    def run_values(self, event: dict[str, Any]) -> dict[str, list[str]]:
        """The run's value of each name the JSON the subagent started from gives: its prompt and
        what each script start_with takes in it printed; none where its record is not found."""
        scripts = [s for t in taken(self.root, self.agent, "start_with") for s in t]
        found = started.texts(event, lambda c: start_with.runs(c, scripts))
        return {} if found is None else started.values(found)

    def forms(self) -> list[str]:
        """The form each in_form lane of the subagent names, by the plugin's folder, which read_only
        lets it read beside its inputs: its step tells it to write in the form, and the form, a
        file of the plugin, holds nothing of the project's work the lane keeps it to."""
        laid_in = taken(self.root, self.agent, "in_form")
        return [step.expanded(named, self.root) for _, named in laid_in]


def taken(root: str, agent: str, lane: str) -> list[list[str]]:
    """What each lane of the kind laid in the subagent, as `<plugin>:<name>`, takes, read from the
    hooks the plugin at root lays; none where its hooks.json is not there or holds no JSON. Read
    there, as a lane may be given in a hook apart from the one asking, such as one held at the
    subagent's end apart from start_with's."""
    try:
        with open(os.path.join(root, "hooks", "hooks.json"), encoding="utf-8") as f:
            hooks = json.load(f)
    except (OSError, ValueError):
        return []
    found = []
    for command in texts(hooks):
        try:
            named, laid_in = laid(root, hook_words(command, "PreToolUse"))
        except ValueError:
            continue
        if named == agent:
            found += [each.takes for each in laid_in if each.lane in (lane,)]
    return found


def texts(value: Any) -> list[str]:
    """Each text a JSON value holds, at any depth, such as each command of a hooks.json."""
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        return [t for v in value for t in texts(v)]
    return [value] if isinstance(value, str) else []


def hook_words(command: Any, event: str) -> list[str]:
    """The words a hook's command gives the event's script in lane's code, the first the subagent
    as `<plugin>:<subagent>`, each after it a lane laid; none for a command that runs no script of
    lane's, names no subagent so, or gives words the shell cannot read."""
    found = re.search(rf'/hooks/lane/{event.lower()}\.py"?(.*)', str(command))
    try:
        words = shlex.split(found[1]) if found else []
    except ValueError:
        return []
    return words if words and AGENT.fullmatch(words[0]) else []


def laid(root: str, words: list[str], held: str = "PreToolUse") -> tuple[str, list[Laid]]:
    """The subagent a hook's command names and the lanes it lays in it, each held on the event
    given; stops with ValueError saying which word is not as lane:up writes it."""
    if not words or not AGENT.fullmatch(words[0]):
        raise ValueError("gives no subagent as <plugin>:<name>")
    found = []
    for w in words[1:]:
        given = read(w)
        if given is None:
            raise ValueError(f"gives `{w}`, no lane as <step>:<lane>:<what it takes>")
        if held not in held_on(given[1]):
            raise ValueError(f"gives `{w}`, no lane held on {held}")
        found.append(Laid(root, words[0], *given))
    return words[0], found


def read(w: str) -> tuple[int, str, list[str]] | None:
    """The step, the lane and what it takes, of a lane as a hook's command gives it; None where it
    is no lane of these as `word` writes it."""
    m = LANE.fullmatch(w)
    takes = m["takes"].split(",") if m else []
    if not m or m["lane"] not in LANES or not all(takes) or not fits(m["lane"], takes):
        return None
    return int(m["step"]), m["lane"], takes


def main(held: str, words: list[str]) -> int:
    """Runs the lanes a hook's command lays, held on the event, on the event Claude Code hands on
    stdin, for the plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT; what the
    event script exits with. A command not in the form lane:up writes lets the subagent go on,
    telling the user, as no subagent or lane can be told from it."""
    try:
        agent, found = laid(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), words, held)
    except ValueError as wrong:
        sys.stderr.write(
            f"lane: the hook's command {wrong}, not as lane:up writes it, so this goes on"
            " unchecked; run lane:up again on the plugin to write its hooks anew\n"
        )
        return hook.UNREAD
    return hook.run(agent.split(":")[0], found, sys.stdin, sys.stderr, agent)
