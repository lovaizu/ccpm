"""The guard: the lanes laid in the subagent a hook's command names, read from the plugin's
hooks/lanes.json, run on the event Claude Code hands the command's script, each telling the
subagent its sentence where a call drifts from it, its calls read from its record with those kept as
they came back, as called.py says. A thing a lane takes written `{<name>}` is given for each run,
and put in before the lane's check, as started.py reads it."""

from __future__ import annotations

import os
from typing import Any, NamedTuple

import call
import called
import hook
import lanes_json
import ports
import schema
import started
import step
from lanes import LANES, alone, given_in, held_on, placed, places, read_whole, sentence, start_with


class Seen(NamedTuple):
    """What an event shows, read once for every lane checked on it: the entries of its subagent's
    record with its calls kept whose results the record does not hold yet, None where the record is
    not found, and what each lane's check takes, the call, or how the subagent ends."""

    found: list[dict[str, Any]] | None
    acted: call.Call | call.End


# Who must fix an error in what the plugin gives a lane, as the subagent replies it.
LAY_AGAIN = (
    "the maker of {plugin} must lay its lanes again with `lay.py write`, so they match its steps"
)
MAKER = "the maker of {plugin} must fix it"
ADAPTER = "the maker of {plugin} must fix the adapter and lay its lanes again with `lay.py write`"
REFUSED = "the maker of {plugin} must fix it and lay its lanes again with `lay.py write`"
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
        read so, an error, as no lane can be checked from it. On a tool call of a subagent whose
        entry has it read its part first, what `read_first` says, where it says anything, in place
        of the lanes."""
        plugin, name = self.agent.split(":")
        try:
            found = lanes_json.subagent(self.root, name)
        except ValueError as wrong:
            return [self.unchecked(str(wrong), LAY_AGAIN.format(plugin=plugin))]
        given, values = lanes_json.lanes_of(found), found.get("adapter")
        # A name the subagent's part uses is read as its entry says it stands for.
        bindings = step.bindings(self.root, name)
        laid = [(lane, step.bound(takes, bindings)) for _, lane, takes, _ in given]
        on = [
            Laid(self.root, self.agent, g, laid, values, bindings)
            for g in given
            if self.held in held_on(g[1])
        ]
        entries = called.entries(event)
        ending = event["hook_event_name"] == "SubagentStop"  # pragma: no mutate
        acted = call.ended(event, entries) if ending else call.read(event, entries)
        if isinstance(acted, call.Call):
            first = self.read_first(acted, entries)
            if first is not None:
                return first
        return [s for lane in on for s in lane.check(event, Seen(entries, acted))]

    def read_first(
        self, acted: call.Call, found: list[dict[str, Any]] | None
    ) -> list[hook.Said] | None:
        """What the subagent is told of the call, where its entry has it read its part whole
        first, read with the entries found of its record, None where it is not found: nothing for a
        read of the part alone, as the entry tells it, its lanes not held on it; the entry's
        sentence naming the part for a call that does anything else before the part is read to its
        end, as start_with and read_whole read what was done before; an error where the part or the
        record is not found; None where the entry names no part or the part is read whole, so the
        lanes are held on the call."""
        plugin, name = self.agent.split(":")
        part = step.part(self.root, name)
        if part is None:
            return None
        file = part.file
        if not os.path.isfile(file):
            where = os.path.relpath(file, self.root)
            wrong = f"its entry names its part `{where}`, which is not there"
            return [self.unchecked(wrong, MAKER.format(plugin=plugin))]
        if found is None:
            return [self.unchecked(NOT_FOUND, hook.CLAUDE_CODE)]
        if acted.tool in call.READ_TOOLS and [p for p, _ in acted.reads] == [file]:
            return []

        def reading(made: call.Call) -> bool:
            return any(p == file for p, _ in made.reads)

        whole = start_with.begun(acted, reading) and not read_whole.left(file, acted.before)
        if reading(acted) or whole:
            return None
        return [hook.Said(step.expanded(part.said, self.root))]

    def unchecked(self, wrong: str, fix: str) -> hook.Said:
        """The error where no lane of the subagent can be checked, told with what is wrong and who
        must fix it."""
        name = self.agent.split(":")[1]
        said = f"lane cannot check the lanes of {name}: {wrong}. {hook.ASK.format(fix=fix)}"
        return hook.Said(said, True)


class Laid:
    """A lane laid on a step of a subagent of the plugin at root, with the adapter of the port it
    reads, None for none, every lane laid in the subagent, each with what it takes read through the
    bindings, the subagent's adapter of the values port, None for none, and the bindings of its
    entry, what each name its part uses stands for."""

    def __init__(
        self,
        root: str,
        agent: str,
        given: tuple[int, str, list[str], str | None],
        laid: list[tuple[str, list[str]]],
        values: str | None,
        bindings: dict[str, str],
    ) -> None:
        self.root, self.agent = root, agent
        self.plugin, self.name = agent.split(":")
        self.number, self.lane, self.takes, self.adapter = given
        # What it takes, as its step names it in its sentence, and read through the bindings as
        # it is checked.
        self.bound = step.bound(self.takes, bindings)
        self.laid, self.values = laid, values
        # The scripts start_with takes in the subagent, which give the run's values with what they
        # print, and which a lane taking one waits on.
        self.scripts = [s for lane, takes in laid if lane == "start_with" for s in takes]

    def check(self, event: dict[str, Any], seen: Seen) -> list[hook.Said]:
        """The lane's sentence where what the event shows drifts from it, as the subagent reads its
        step, with the point it drifts by on the next line where its check gives one; an error where
        what the lane is given is not as its IN says, an adapter it reads by is not as its port
        says, its step no longer says its sentence, or what it takes is refused now as the layer
        refuses it, such as in_form's form gone; nothing otherwise."""
        # Told before as it ends, a subagent that has answered with words alone is let end, so it
        # is told and never held for good.
        acted = seen.acted
        if isinstance(acted, call.End) and acted.answered:
            return []
        said = sentence(self.lane, self.takes)
        if not step.holds(self.root, self.name, self.number, said):
            return [self.error(f"step {self.number} no longer says: {said}", LAY_AGAIN)]
        # What the layer refuses to lay is held again on each run, as the plugin may have changed
        # since, such as in_form's form gone.
        refused = getattr(LANES[self.lane], "refused", None)
        why = refused(self.bound, self.root) if refused is not None else ""
        if why:
            return [self.error(f"it {why}", REFUSED)]
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
        held to its IN, nothing where one is given as null, as `check` says; stops with
        ports.Failed, holding what the adapter did and its path, where an adapter it reads by is not
        as its port says."""
        acted = seen.acted
        run = started.held(named, self.run_values(event["cwd"], seen.found)) if named else {}
        if run is None:
            return []
        texts = started.put(placed(self.lane, self.bound), run)
        given: dict[str, Any] = {"takes": dict(zip(places(self.lane), texts))}
        out = schema.held(given_in(self.lane), {**given, **self.record(seen)})
        if out is not None:
            return [self.error(NOT_FOUND, "") if seen.found is None else self.wrong(out, run)]
        lane: Any = LANES[self.lane]
        # Held to its IN, each place holds its texts, as the check then reads them.
        each = started.resolved(list(given["takes"].values()), alone(self.lane))
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
            return ports.run(os.path.join(self.root, adapter), port, given, self.root)
        except ports.Failed as failed:
            raise ports.Failed(str(failed), adapter) from None

    def record(self, seen: Seen) -> dict[str, Any]:
        """The record the lane's check may rest on, as its IN names it, where it is found."""
        return {} if seen.found is None else {"record": seen.found}

    def started(self, seen: Seen) -> bool:
        """Whether the subagent has run each script start_with takes in it, before the call or the
        end the event shows, or start_with is laid in it on none."""
        acted = seen.acted
        before = acted.made if isinstance(acted, call.End) else acted.before
        return not self.scripts or any(call.runs(c, self.scripts) for c in before)

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
        said = f"lane cannot check {on}: {wrong.rstrip('.')}. {hook.ASK.format(fix=who)}"
        return hook.Said(said, True)

    def run_values(
        self, cwd: str, found: list[dict[str, Any]] | None
    ) -> dict[str, list[str] | None]:
        """The run's value of each name the JSON the subagent started from gives, from the entries
        found of its record, made in the folder: its prompt and what each script start_with takes
        in it printed; none where its record is not found."""
        texts = started.texts(found, cwd, lambda c: call.runs(c, self.scripts))
        return {} if texts is None else self.read("values", {"texts": texts}, self.values)["values"]
