"""The guard: the lanes a hook's command lays in one subagent, run on the event Claude Code hands
the command's script, each telling the subagent its sentence where a call drifts from it. A thing
a lane takes written `{<name>}` is given for each run, and put in before the lane's check, as
started.py reads it."""

from __future__ import annotations

import os
import sys
from typing import Any

import call
import hook
import hooks_file
import started
import step
from lanes import LANES, alone, sentence, start_with


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
        ending = event["hook_event_name"] == "SubagentStop"  # pragma: no mutate
        end = call.ended(event) if ending else None
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
        if self.lane == "read_only":
            each = [[*inputs, *self.forms()] for inputs in each]
        drift = next(filter(None, (lane.drifts(acted, t, self.root) for t in each)), "")
        if not drift:
            return []
        told = [step.expanded(said, self.root), *(started.told(n, run[n]) for n in named)]
        return ["\n".join([*told, *([drift] if isinstance(drift, str) else [])])]

    def run_values(self, event: dict[str, Any]) -> dict[str, list[str]]:
        """The run's value of each name the JSON the subagent started from gives: its prompt and
        what each script start_with takes in it printed; none where its record is not found."""
        scripts = [s for t in hooks_file.taken(self.root, self.agent, "start_with") for s in t]
        found = started.texts(event, lambda c: start_with.runs(c, scripts))
        return {} if found is None else started.values(found)

    def forms(self) -> list[str]:
        """The form each in_form lane of the subagent names, by the plugin's folder, which read_only
        lets it read beside its inputs: its step tells it to write in the form, and the form, a
        file of the plugin, holds nothing of the project's work the lane keeps it to."""
        laid_in = hooks_file.taken(self.root, self.agent, "in_form")
        return [step.expanded(named, self.root) for _, named in laid_in]


def main(held: str, words: list[str]) -> int:
    """Runs the lanes a hook's command lays, held on the event, on the event Claude Code hands on
    stdin, for the plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT; what the
    event script exits with. A command not in the form lane:up writes lets the subagent go on,
    telling the user, as no subagent or lane can be told from it."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    try:
        agent, given = hooks_file.parsed(words, held)
    except ValueError as wrong:
        sys.stderr.write(
            f"lane: the hook's command {wrong}, not as lane:up writes it, so this goes on"
            " unchecked; run lane:up again on the plugin to write its hooks anew\n"
        )
        return hook.UNREAD
    found = [Laid(root, agent, *g) for g in given]
    return hook.run(agent.split(":")[0], found, sys.stdin, sys.stderr, agent)
