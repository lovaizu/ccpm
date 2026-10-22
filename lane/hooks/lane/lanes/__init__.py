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
agent_type, and each lane as `<step>:<lane>:<what it takes>`, the things taken joined by commas."""

from __future__ import annotations

import os
import re
import sys
from typing import Any

import call
import hook
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
        self.root, self.plugin, self.name = root, *agent.split(":")
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
        # Each lane's check takes what its event gives: the call, or how the subagent ends.
        lane: Any = LANES[self.lane]
        drift = lane.drifts(call.read(event) if end is None else end, self.takes, self.root)
        if not drift:
            return []
        told = step.expanded(said, self.root)
        return [f"{told}\n{drift}" if isinstance(drift, str) else told]


def laid(root: str, words: list[str], held: str = "PreToolUse") -> tuple[str, list[Laid]]:
    """The subagent a hook's command names and the lanes it lays in it, each held on the event
    given; stops with ValueError saying which word is not as lane:up writes it."""
    if not words or not AGENT.fullmatch(words[0]):
        raise ValueError("gives no subagent as <plugin>:<name>")
    found = []
    for w in words[1:]:
        m = LANE.fullmatch(w)
        takes = m["takes"].split(",") if m else []
        if not m or m["lane"] not in LANES or not all(takes) or not fits(m["lane"], takes):
            raise ValueError(f"gives `{w}`, no lane as <step>:<lane>:<what it takes>")
        if held not in held_on(m["lane"]):
            raise ValueError(f"gives `{w}`, no lane held on {held}")
        found.append(Laid(root, words[0], int(m["step"]), m["lane"], takes))
    return words[0], found


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
