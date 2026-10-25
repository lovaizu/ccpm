"""The guard: the lanes laid in the subagent a hook's command names, read from the plugin's
hooks/lanes.json, run on the event Claude Code hands the command's script, each telling the
subagent its sentence where a call drifts from it, and each call of the subagent kept as it comes
back, as called.py says. A thing a lane takes written
`{<name>}` is given for each run, and put in before the lane's check, as started.py reads it."""

from __future__ import annotations

import os
import sys
from typing import Any, NamedTuple

import call
import called
import hook
import hooks_file
import started
import step
from lanes import LANES, alone, held_on, sentence


class Seen(NamedTuple):
    """What an event shows, read once for every lane checked on it: the entries of its subagent's
    record with its calls kept that the record does not hold yet, None where the record is not
    found, and what each lane's check takes, the call, or how the subagent ends."""

    found: list[dict[str, Any]] | None
    acted: call.Call | call.End


class Lanes:
    """The lanes laid in one subagent of the plugin at root, as `<plugin>:<name>`, held on an
    event, checked on it together."""

    def __init__(self, root: str, agent: str, held: str) -> None:
        self.root, self.agent, self.held = root, agent, held

    def check(self, event: dict[str, Any]) -> list[hook.Said]:
        """What each lane held on the event says on it, read from the plugin's hooks/lanes.json,
        its subagent's record and kept calls read once for all of them; where the file cannot be
        read so, the user told what is wrong, as no lane can be told from it."""
        try:
            given = hooks_file.laid_in(self.root, self.agent.split(":")[1])
        except ValueError as wrong:
            unread = f"{wrong}, so this goes on unchecked; run lane:up again on the plugin"
            return [hook.Said(unread, user=True)]
        laid = [(lane, takes) for _, lane, takes in given]
        on = [Laid(self.root, self.agent, g, laid) for g in given if self.held in held_on(g[1])]
        found = called.entries(event)
        ending = event["hook_event_name"] == "SubagentStop"  # pragma: no mutate
        seen = Seen(found, call.ended(event, found) if ending else call.read(event, found))
        return [hook.Said(s) for lane in on for s in lane.check(event, seen)]


class Laid:
    """A lane laid on a step of a subagent of the plugin at root, with every lane laid in the
    subagent, each with what it takes."""

    def __init__(
        self,
        root: str,
        agent: str,
        given: tuple[int, str, list[str]],
        laid: list[tuple[str, list[str]]],
    ) -> None:
        self.root, self.agent = root, agent
        self.plugin, self.name = agent.split(":")
        self.number, self.lane, self.takes = given
        self.laid = laid

    def check(self, event: dict[str, Any], seen: Seen) -> list[str]:
        """The lane's sentence where what the event shows drifts from it, as the subagent reads its
        step, with the point it drifts by on the next line where its check gives one; where the step
        no longer says it, that lane:up must be run again; nothing otherwise."""
        # A lane held as the subagent ends lets it end where what it did is not known, or where,
        # told before, it has answered with words alone, so it is told and never held for good.
        acted = seen.acted
        if isinstance(acted, call.End) and (acted.made is None or acted.answered):
            return []
        said = sentence(self.lane, self.takes)
        if not step.holds(self.root, self.name, self.number, said):
            gone = f"step {self.number} of {self.name} no longer says: {said}"
            again = f"lane:up must be run again on {self.plugin}, so its lanes match its steps"
            return [f"{gone} Stop here and reply that {again}."]
        # A lane taking a thing given for each run lets every call through until the subagent
        # has been given it.
        named = started.names(self.takes)
        run = self.run_values(event["cwd"], seen.found) if named else {}
        if not set(named) <= set(run):
            return []
        lane: Any = LANES[self.lane]
        each = started.resolved(self.takes, run, alone(self.lane))
        # A lane may take more beside what its step names, from the lanes laid in the subagent.
        more = getattr(lane, "beside", None)
        if more is not None:
            each = [[*inputs, *more(self.laid, self.root)] for inputs in each]
        drift = next(filter(None, (lane.drifts(acted, t, self.root) for t in each)), "")
        if not drift:
            return []
        told = [step.expanded(said, self.root), *(started.told(n, run[n]) for n in named)]
        return ["\n".join([*told, *([drift] if isinstance(drift, str) else [])])]

    def run_values(self, cwd: str, found: list[dict[str, Any]] | None) -> dict[str, list[str]]:
        """The run's value of each name the JSON the subagent started from gives, from the entries
        found of its record, made in the folder: its prompt and what each script start_with takes
        in it printed; none where its record is not found."""
        scripts = [s for t in hooks_file.taken(self.root, self.name, "start_with") for s in t]
        texts = started.texts(found, cwd, lambda c: call.runs(c, scripts))
        return {} if texts is None else started.values(texts)


def main(held: str, words: list[str]) -> None:
    """Runs the lanes laid in the subagent a hook's command names, held on the event, on the event
    Claude Code hands on stdin, for the plugin found where Claude Code gives its folder,
    CLAUDE_PLUGIN_ROOT, or, on an event a call is kept on, keeps the call, answering Claude Code on
    stdout. A command not in the form lane:up writes lets the subagent go on, telling the user, as
    no subagent can be told from it."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if len(words) != 1 or not hooks_file.AGENT.fullmatch(words[0]):
        unread = (
            f"lane: the hook's command gives `{' '.join(words)}`, not the subagent alone as"
            " <plugin>:<name>, as lane:up writes it, so this goes on unchecked; run lane:up again"
            " on the plugin to write its hooks anew"
        )
        hook.answered(sys.stdout, hook.answer(held, "", unread))
        return
    agent = words[0]
    check = called.Kept() if held in hooks_file.KEPT else Lanes(root, agent, held)
    hook.run(agent.split(":")[0], [check], sys.stdin, sys.stdout, agent)
