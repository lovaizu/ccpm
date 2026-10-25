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
import ports
import schema
import started
import step
from lanes import LANES, alone, given_in, held_on, placed, places, sentence


class Seen(NamedTuple):
    """What an event shows, read once for every lane checked on it: the entries of its subagent's
    record with its calls kept that the record does not hold yet, None where the record is not
    found, and what each lane's check takes, the call, or how the subagent ends."""

    found: list[dict[str, Any]] | None
    acted: call.Call | call.End


# Who must fix an error in what the plugin gives a lane, as the subagent replies it.
LANE_UP = "lane:up must be run again on {plugin}, so its lanes match its steps"
MAKER = "the maker of {plugin} must fix it"
ADAPTER = "the maker of {plugin} must fix the adapter and run lane:up again"
# What a lane resting on its subagent's record meets where the record is not there.
NOT_FOUND = "its record is not found where Claude Code keeps it"


class Lanes:
    """The lanes laid in one subagent of the plugin at root, as `<plugin>:<name>`, held on an
    event, checked on it together."""

    def __init__(self, root: str, agent: str, held: str) -> None:
        self.root, self.agent, self.held = root, agent, held

    def check(self, event: dict[str, Any]) -> list[hook.Said]:
        """What each lane held on the event says on it, read from the plugin's hooks/lanes.json,
        its subagent's record and kept calls read once for all of them; where the file cannot be
        read so, an error, as no lane can be checked from it."""
        plugin, name = self.agent.split(":")
        try:
            given = hooks_file.laid_in(self.root, name)
            values = hooks_file.subagent(self.root, name).get("adapter")
        except ValueError as wrong:
            fix = LANE_UP.format(plugin=plugin)
            unread = (
                f"lane cannot check the lanes of {name}: {wrong}. Stop here and reply that {fix}."
            )
            return [hook.Said(unread, True)]
        laid = [(lane, takes) for _, lane, takes, _ in given]
        on = [
            Laid(self.root, self.agent, g, laid, values)
            for g in given
            if self.held in held_on(g[1])
        ]
        found = called.entries(event)
        ending = event["hook_event_name"] == "SubagentStop"  # pragma: no mutate
        seen = Seen(found, call.ended(event, found) if ending else call.read(event, found))
        return [s for lane in on for s in lane.check(event, seen)]


class Laid:
    """A lane laid on a step of a subagent of the plugin at root, with the adapter of the port it
    reads, None for none, every lane laid in the subagent, each with what it takes, and the
    subagent's adapter of the values port, None for none."""

    def __init__(
        self,
        root: str,
        agent: str,
        given: tuple[int, str, list[str], str | None],
        laid: list[tuple[str, list[str]]],
        values: str | None,
    ) -> None:
        self.root, self.agent = root, agent
        self.plugin, self.name = agent.split(":")
        self.number, self.lane, self.takes, self.adapter = given
        self.laid, self.values = laid, values

    def check(self, event: dict[str, Any], seen: Seen) -> list[hook.Said]:
        """The lane's sentence where what the event shows drifts from it, as the subagent reads its
        step, with the point it drifts by on the next line where its check gives one; an error where
        what the lane is given is not as its IN says, an adapter it reads by is not as its port
        says, or its step no longer says its sentence; nothing otherwise."""
        # Told before as it ends, a subagent that has answered with words alone is let end, so it
        # is told and never held for good.
        acted = seen.acted
        if isinstance(acted, call.End) and acted.answered:
            return []
        said = sentence(self.lane, self.takes)
        if not step.holds(self.root, self.name, self.number, said):
            return [self.error(f"step {self.number} no longer says: {said}", LANE_UP)]
        named = started.names(self.takes)
        # The run's values are read from the record, given by its prompt and by the script
        # start_with runs first, so a lane taking one is held once that script has run, start_with
        # holding the subagent until.
        if named and seen.found is None:
            return [self.error(NOT_FOUND, "")]
        if named and not self.started(seen):
            return []
        # What an adapter does that is not as its port says is an error, as each lane meets it.
        try:
            return self.checked(event, seen, said, named)
        except ports.Failed as failed:
            return [self.error(f"the adapter {failed.args[1]} {failed.args[0]}", ADAPTER)]

    def checked(
        self, event: dict[str, Any], seen: Seen, said: str, named: list[str]
    ) -> list[hook.Said]:
        """The lane's sentence where what the event shows drifts from it, the run's values read and
        held to its IN, as `check` says; stops with ports.Failed, holding what the adapter did and
        its path, where an adapter it reads by is not as its port says."""
        acted = seen.acted
        run = self.run_values(event["cwd"], seen.found) if named else {}
        texts = started.put(placed(self.lane, self.takes), run)
        given = {"takes": dict(zip(places(self.lane), texts))}
        out = schema.held(given_in(self.lane), {**given, **self.record(seen)})
        if out is not None:
            return [self.error(NOT_FOUND, "") if seen.found is None else self.wrong(out, run)]
        lane: Any = LANES[self.lane]
        each = started.resolved([t or [] for t in texts], alone(self.lane))
        # A lane may take more beside what its step names, from the lanes laid in the subagent.
        more = getattr(lane, "beside", None)
        if more is not None:
            each = [[*inputs, *more(self.laid, self.root)] for inputs in each]
        port = getattr(lane, "PORT", None)
        read = [] if port is None else [lambda given: self.read(port, given, self.adapter)]
        drift = next(filter(None, (lane.drifts(acted, t, self.root, *read) for t in each)), "")
        if not drift:
            return []
        told = [step.expanded(said, self.root), *(started.told(n, run[n]) for n in named)]
        return [hook.Said("\n".join([*told, *([drift] if isinstance(drift, str) else [])]))]

    def read(self, port: str, given: dict[str, Any], adapter: str | None) -> dict[str, Any]:
        """What the port gives back, given its JSON, by the plugin's adapter of the path, or by
        lane's reading where none is named; stops with ports.Failed, holding what the adapter did
        and its path, where it is not as its port says."""
        if adapter is None:
            return ports.read(port, given)
        try:
            return ports.run(os.path.join(self.root, adapter), port, given)
        except ports.Failed as failed:
            raise ports.Failed(str(failed), adapter) from None

    def record(self, seen: Seen) -> dict[str, Any]:
        """The record the lane's check may rest on, as its IN names it, where it is found."""
        return {} if seen.found is None else {"record": seen.found}

    def started(self, seen: Seen) -> bool:
        """Whether the subagent has run each script start_with takes in it, before the call or the
        end the event shows, or start_with is laid in it on none."""
        scripts = [s for t in hooks_file.taken(self.root, self.name, "start_with") for s in t]
        acted = seen.acted
        before = (acted.made if isinstance(acted, call.End) else acted.before) or []
        return not scripts or any(call.runs(c, scripts) for c in before)

    def wrong(self, out: schema.Out, run: dict[str, list[str]]) -> hook.Said:
        """The error of what the lane is given out of its IN by the point, its record found: a take
        given for each run, in the place of its sentence the point names, not given, or given
        empty, which the plugin's maker must fix."""
        takes = placed(self.lane, self.takes)[places(self.lane).index(out.path[1])]
        name = next(n for n in started.names(takes) if not run.get(n))
        how = "not given" if name not in run else "given empty"
        return self.error(f"`{{{name}}}` is {how} in what {self.name} started from", MAKER)

    def error(self, wrong: str, fix: str) -> hook.Said:
        """The error the lane meets, told with what is wrong and who must fix it, "" for Claude
        Code."""
        who = fix.format(plugin=self.plugin) if fix else hook.CLAUDE_CODE
        on = f"{self.lane} on step {self.number} of {self.name}"
        said = f"lane cannot check {on}: {wrong.rstrip('.')}. Stop here and reply that {who}."
        return hook.Said(said, True)

    def run_values(self, cwd: str, found: list[dict[str, Any]] | None) -> dict[str, list[str]]:
        """The run's value of each name the JSON the subagent started from gives, from the entries
        found of its record, made in the folder: its prompt and what each script start_with takes
        in it printed; none where its record is not found."""
        scripts = [s for t in hooks_file.taken(self.root, self.name, "start_with") for s in t]
        texts = started.texts(found, cwd, lambda c: call.runs(c, scripts))
        return {} if texts is None else self.read("values", {"texts": texts}, self.values)["values"]


def main(held: str, words: list[str]) -> None:
    """Runs the lanes laid in the subagent a hook's command names, held on the event, on the event
    Claude Code hands on stdin, for the plugin found where Claude Code gives its folder,
    CLAUDE_PLUGIN_ROOT, or, on an event a call is kept on, keeps the call, answering Claude Code on
    stdout. A command not in the form lane:up writes is an error, as no subagent can be told from
    it."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    agent = " ".join(words)
    if not hooks_file.AGENT.fullmatch(agent):
        unread = (
            f"lane: lane cannot check the lanes of this hook: its command gives"
            f" `{agent}`, not the subagent alone as <plugin>:<name>, as lane:up writes"
            " it. Stop here and reply that lane:up must be run again on the plugin, to write its"
            " hooks anew."
        )
        hook.failed(held, unread, sys.stdin, sys.stdout)
        return
    check = called.Kept() if held in hooks_file.KEPT else Lanes(root, agent, held)
    hook.run(agent.split(":")[0], held, [check], sys.stdin, sys.stdout, agent)
