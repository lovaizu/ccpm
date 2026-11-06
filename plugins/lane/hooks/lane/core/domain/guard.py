"""The guard: decides, of each event of a subagent with lanes laid or named by the routes, and of
each event of the main conversation within a run of the skill the routes start from, what it is
told, from the event's input alone, as Claude Code documents it, and from the calls kept; and,
where it cannot decide, the error that says what is wrong and who must fix it.

At PreToolUse, a call goes through, is stopped with the sentences it breaks, or, a held command, is
put to the person with its sentence. A subagent with lanes runs a command only where a run_only,
hold or test_after lane names it, whole, or its result command does: a call of Bash is judged by
those lanes of the subagent together, as lane does not know which step the subagent is on. A read
is judged by its read_only lanes together, and a write by its write_only lanes together, each going
through where there is none; a write of an edit_only lane's output, once it is there, goes through
only by Edit; a write of an in_form lane's output is held to its form. Any other
tool goes through. A result command is let through only once the lanes checked at the end hold.

A take `{<name>}` is the start's value of the name, read at the values port from the texts the
subagent was given: the prompt of the Agent call that started it, kept under the ID of the start as
the call comes back, and each message sent to it after. A call the subagent makes before its start
has come back waits for it a short time, within the hook's; a value given as null lets the lane's
call or end through on that start. A subagent whose file no longer sets `background: true` is an
error at each of its events, as only a start in the background comes back with its ID before the
subagent's calls.

At PostToolUse, a subagent's call is kept, with the result where it is a result command. At
SubagentStart, the start is kept and the subagent given its part whole where its entry names one.
At SubagentStop, a subagent giving a result is kept going once where it gave none; any other end is
kept, so a start in the background counts once its subagent has ended.

The main conversation is held only while a run of the skill lasts, from the command's expansion or
the Skill call that begins it until a route ends it, with neither a `to` nor `waits`, or a new call
of the skill, while the run waits for the user, ends it and begins another. Within it, a
start not due, or a message resuming a start that ended with no result, is stopped with the start
due; each start coming back is kept and told to wait; each prompt handed to the main conversation,
a subagent's task-notification among them, is told the next start, or, where a route waits, to
put the subagent's point to the user and resume it with their answer; and the end of a turn is
kept going once while a start is due and no start of the run still runs, and let end while the
user is to answer. A dependency's skill the routes name is
one move, from its Skill call to the run of the dependency's result script, during which nothing
of the main conversation is checked."""

from __future__ import annotations

import os
import time
from typing import Any, Callable, NamedTuple

import called
import lanes
import ports
import routes
import rules
import schema
import step
from lanes import edit_only, follow_routes, in_form, read_only, run_only, write_only
from lanes.done import Done

# Each tool a lane judges, with the action its call is and the field of its input the lane judges.
WATCHED = {
    "Bash": ("run", "command"),
    "Write": ("write", "file_path"),
    "Edit": ("write", "file_path"),
    "NotebookEdit": ("write", "notebook_path"),
    "Read": ("read", "file_path"),
    "Grep": ("read", "path"),
}
# The lanes that name the commands a subagent may run, each with the place they lie in.
RUNS = {"run_only": "commands", "hold": "commands", "test_after": "test", "result": "commands"}
# What a subagent is told, after its run lanes' sentences, of the commands it may run.
MAY_RUN = "The commands you may run, each word for word: {listed}."
DEPENDENCY_FOLDER = (
    "Each `${dependency:<name>}` is the folder the plugin of the name is installed in, as its skill"
    " gives the command."
)
LAY_AGAIN = rules.LAY_AGAIN
ADAPTER = (
    "the maker of {plugin} must fix its adapter {adapter}, and lay it again with `lay.py write`"
)
GIVE = "whoever starts {name} must give it `{value}` in its prompt or a message, as JSON"
PART = "the maker of {plugin} must put its part {part} back, or lay its lanes again"
BACKGROUND = "the maker of {plugin} must set `background: true` in the frontmatter of {file} again"
CLAUDE_CODE = (
    "Claude Code must be updated with `claude update`, and where this goes on, it must be reported"
    " at https://github.com/lovaizu/ccpm/issues"
)
START = (
    f"whoever starts {{name}} must start it with the Agent tool, and where they did, {CLAUDE_CODE}"
)
# The seconds a run's call waits for the Agent call that started the run to come back with its ID,
# and the seconds between looks: a start in the background comes back as the run starts, and its
# first call comes seconds later, as Claude Code 2.1.317's hooks showed.
WAIT = 3.0
STEP = 0.05
UNJOINED = (
    "the Agent call starting it gave back no ID of its run within {wait:g} seconds, so what it was"
    " given is not known"
)
# What the user is told as the main conversation, kept going once with a start due, is let end its
# turn: the start left, and the step that must be fixed, the skill's own or that of the subagent
# that ended with no result.
LEFT = (
    "lane let the run of {lead} end with `{plugin}:{name}` still due{why}: the maker of {plugin}"
    " must fix {at}"
)
LEFT_DEPENDENCY = (
    "lane let the run of {lead} end with `{name}` still due, as {name} ended with no result the"
    " routes take: the maker of {dependency} must have {own} give {results}"
)
STARTS_IT = "step {step} of {lead} in {file}, which starts it."
GIVES_IT = "step {step} of {name} in {file}, which gives its result."
ORDER = (
    "the maker of {plugin} must order the results of {name} in the `precedence` of its routes, and"
    " lay them again with `lay.py write`"
)
LANES_FAULT = "it must be reported at https://github.com/lovaizu/ccpm/issues, as lane's own fault"
# What an Agent call starting a subagent gives back, as Claude Code documents it: the status of a
# subagent ended in the foreground or launched in the background, and the ID of its run, which
# names its calls kept.
BACK = {
    "type": "object",
    "required": ["status", "agentId"],
    "properties": {
        "status": {"enum": ["completed", "async_launched"]},
        "agentId": {"type": "string", "pattern": f"^{called.ID.pattern}$"},
    },
}


class Said(NamedTuple):
    """What the guard says of an event: a break, told the subagent; an error, told the subagent
    and the user alike, as only the user can have it fixed; a held command, put to the person
    with it; the subagent's part, given as it is; or a note, told the user alone, as the event
    goes on."""

    text: str
    error: bool = False
    ask: bool = False
    plain: bool = False
    note: bool = False


class Cannot(Exception):
    """Where lane cannot check an event: the error it says."""

    def __init__(self, said: Said) -> None:
        super().__init__(said.text)
        self.said = said


class Subagent(NamedTuple):
    """The subagent an event is of, as the guard checks it: the plugin's folder and name, the
    subagent's name, the session and the ID of its run, its lanes with the sentences laid from the
    routes, the routes where they name it, the results it gives, its values adapter where it names
    one, what was read once for the event, and when the guard began on the event, a time of
    time.monotonic, from which the seconds its adapters are left are counted."""

    root: str
    plugin: str
    name: str
    session: str
    agent: str
    laid: list[rules.Laid]
    routes: dict[str, Any] | None
    ons: list[str]
    adapter: str | None
    memo: dict[str, Any]
    start: float

    def foreign(self) -> bool:
        """Whether the subagent is a dependency's, `<dependency>:<name>`, which the routes name and
        its own plugin's guard holds to its lanes."""
        return ":" in self.name

    def gave(self, command: str, cwd: str) -> str | None:
        """The result the command gives, as one of the subagent's result commands, matched whole:
        word for word as it reads them, or, for a dependency's subagent, by any folder of the
        dependency; None where it is none of them."""
        for on, gives in zip(self.ons, self.commands("result")):
            if command == gives or (
                self.foreign() and run_only.allows(command, [gives], self.root, cwd, {})
            ):
                return on
        return None

    def keep(self, entry: dict[str, Any]) -> None:
        """Keeps the entry under the subagent's run."""
        called.keep(self.session, self.agent, entry)

    def of(self, *kinds: str) -> list[rules.Laid]:
        """The subagent's lanes of the kinds, each checked to be said by its step still."""
        found = [g for g in self.laid if g.lane in kinds]
        for lane in found:
            held(lane, self)
        return found

    def commands(self, lane: str) -> list[str]:
        """The commands of the subagent's lanes of the kind, as it reads them in its steps."""
        # The lane asked for is `result`, a text the code writes as it writes the result lanes,
        # so `is` finds them as `==`.
        found = [g for g in self.laid if g.lane == lane]  # pragma: no mutate
        return [c for g in found for c in run_only.named(g.takes, self.root)]

    def texts(self) -> list[str]:
        """The texts the run was given, as `called.texts` reads them, waiting up to WAIT seconds,
        within the hook's time left, for its start to come back with them; stops with ValueError
        where it has not."""
        for _ in range(int(min(WAIT, ports.left(self.start)) / STEP)):
            found = called.texts(self.session, self.agent)
            if found is not None:
                return found
            time.sleep(STEP)
        found = called.texts(self.session, self.agent)
        if found is None:
            raise ValueError(UNJOINED.format(wait=WAIT))
        return found

    def values(self) -> dict[str, Any]:
        """The run's values, read at the values port from the texts it was given, by lane's reading
        or the subagent's adapter, once for the event; stops with ports.Failed where the adapter
        fails, and ValueError where its start has not come back with its texts."""
        if "values" not in self.memo:
            given = {"texts": self.texts()}
            self.memo["values"] = (
                ports.run(
                    os.path.join(self.root, self.adapter),
                    "values",
                    given,
                    self.root,
                    ports.left(self.start),
                )
                if self.adapter
                else ports.read("values", given)
            )["values"]
        return self.memo["values"]


def cannot(on: str, wrong: str, fix: str) -> Said:
    """The error where lane cannot check what `on` names, such as `the lanes of <subagent>` or
    `<lane> on step <n> of <subagent>`, in the form docs/lanes.md gives."""
    return Said(rules.cannot(on, wrong, fix), True)


def cannot_main(on: str, wrong: str, fix: str) -> Said:
    """The error where lane cannot check what `on` names of a run, such as `the routes of
    <skill>`, in the form docs/lanes.md gives the main conversation."""
    return Said(rules.cannot(on, wrong, fix, main=True), True)


def unshaped(name: str, wrong: str) -> Said:
    """The error where the event of the subagent of the name is not as Claude Code hands it, by the
    point given, which Claude Code must fix."""
    said = f"the hook was handed no event as Claude Code hands it, {wrong}"
    return cannot(f"the lanes of {name}", said, CLAUDE_CODE)


def subagent(
    root: str, plugin: str, name: str, event: dict[str, Any], wrong: str
) -> Subagent | None:
    """The subagent of the name as the guard checks it, of the plugin at root of the name given;
    None where no lane is laid in it and no route names it. Stops with Cannot where the plugin's
    hooks/lanes.json cannot be read, the event is not as Claude Code hands it, as `wrong` says, or
    the subagent's file, where it is there, no longer sets `background: true`. The guard begins on
    the event here, so its adapters' seconds are counted from now."""
    start = time.monotonic()
    try:
        given = rules.read(root)
    except ValueError as why:
        # Whether the routes name another plugin's subagent cannot be read, and the plugin's own
        # are told the error.
        if ":" in name:
            return None
        fix = LAY_AGAIN.format(plugin=plugin)
        raise Cannot(cannot(f"the lanes of {name}", str(why), fix)) from None
    laid, routed = rules.of(given, name), rules.routes_of(given)
    if routed is not None and name not in routes.named(routed):
        routed = None
    if laid is None and routed is None:
        return None
    why = routes.refused(routed) if routed is not None else ""
    if why:
        fix = LAY_AGAIN.format(plugin=plugin)
        raise Cannot(cannot(f"the lanes of {name}", f"{rules.FILE} {why}", fix))
    if wrong:
        raise Cannot(unshaped(name, wrong))
    entry = step.agent_file(root, name)
    if entry is not None and not step.background(entry):
        file = os.path.relpath(entry, root)
        said = f"its file {file} no longer sets `background: true`, so lane cannot tell its runs"
        said += " apart"
        fix = BACKGROUND.format(plugin=plugin, file=file)
        raise Cannot(cannot(f"the lanes of {name}", said, fix))
    found = list(laid or [])
    ends = any(lanes.ends(g.lane) for g in found)
    ons = routes.gives(routed, name, ends, rules.results_of(given, name))
    if ons:
        # The last step's number, or none that a step has, where its file has no step.
        last = step.last(step.lines_of(root, name)) or 0
        found.append(rules.Laid(last, "result", [routes.command(name, on) for on in ons]))
    session, agent = called.record(plugin, event["session_id"]), event["agent_id"]
    adapter = rules.adapter_of(given, name)
    return Subagent(root, plugin, name, session, agent, found, routed, ons, adapter, {}, start)


def on(lane: rules.Laid, s: Subagent) -> str:
    """The lane on its step of the subagent, as an error names it."""
    return f"{lane.lane} on step {lane.step} of {s.name}"


def held(lane: rules.Laid, s: Subagent) -> None:
    """Stops with Cannot where the lane is one `lay.py write` would now refuse, as lanes/ checks
    it, or its step no longer says its sentence."""
    # The result command is laid from the routes, which `subagent` holds to their checks.
    why = lanes.refused(lane.lane, lane.takes, s.root) if lane.lane in lanes.LANES else None
    if why and why.said:
        wrong = f"`lay.py write` would now refuse it: {lane.lane} {why.said}".replace(" ,", ",")
        raise Cannot(cannot(on(lane, s), wrong, LAY_AGAIN.format(plugin=s.plugin)))
    said = lanes.sentence(lane.lane, lane.takes)
    if not step.holds(s.root, s.name, lane.step, said):
        gone = f"step {lane.step} no longer says: {said}".rstrip(".")
        raise Cannot(cannot(on(lane, s), gone, LAY_AGAIN.format(plugin=s.plugin)))


def places_of(lane: rules.Laid, s: Subagent) -> dict[str, list[str]] | None:
    """What the lane takes on the subagent's run, in its places: each `{<name>}` the run's value of
    the name, its empty texts left out, in the place the take is in, and a command holding a value
    as a part as it is, its value read by `parts_of`; None where a value is given as null, which
    lets the lane's call or end through. Stops with Cannot where a value cannot be read, is not
    given or is given empty."""
    if parts_of(lane, s) is None:
        return None
    found: dict[str, list[str]] = {}
    for place, takes in lanes.placed(lane.lane, lane.takes).items():
        found[place] = []
        for take in takes:
            texts = value_of(take, lane, s) if rules.GIVEN.fullmatch(take) else [take]
            if texts is None:
                return None
            found[place] += texts
    # A value adds texts only to a place its take is in, and `held` holds the takes laid to the
    # lane's IN, so what the lane is given stays in it.
    return found


def parts_of(lane: rules.Laid, s: Subagent) -> dict[str, list[str]] | None:
    """The run's values the lane's commands hold as parts, by their names, each its texts, the
    empty left out; None where one is given as null. Stops with Cannot as `value_of` does."""
    found: dict[str, list[str]] = {}
    for place, takes in lanes.placed(lane.lane, lane.takes).items():
        holding = (lane.lane, place) in run_only.COMMANDS
        for take in takes if holding else []:
            # A take that is a value whole is read by places_of.
            for name in [] if rules.GIVEN.fullmatch(take) else run_only.values_in(take):
                texts = value_of(f"{{{name}}}", lane, s)
                if texts is None:
                    return None
                found[name] = texts
    return found


def value_of(take: str, lane: rules.Laid, s: Subagent) -> list[str] | None:
    """The run's value of the take `{<name>}`, its empty texts left out; None where it is given as
    null. Stops with Cannot where the values cannot be read, or the value is not given or is given
    empty."""
    try:
        values = s.values()
    except ports.Failed as why:
        fix = ADAPTER.format(plugin=s.plugin, adapter=s.adapter)
        raise Cannot(cannot(on(lane, s), f"the adapter {s.adapter} {why}", fix)) from None
    except ValueError as why:
        raise Cannot(cannot(on(lane, s), str(why), START.format(name=s.name))) from None
    name = take[1:-1]
    fix = GIVE.format(name=s.name, value=name)
    if name not in values:
        raise Cannot(cannot(on(lane, s), f"`{take}` was given no value", fix))
    if values[name] is None:
        return None
    texts = [t for t in values[name] if t]
    if not texts:
        raise Cannot(cannot(on(lane, s), f"`{take}` was given empty", fix))
    return texts


def forms_of(lane: rules.Laid, s: Subagent, places: dict[str, list[str]]) -> list[str]:
    """The forms the in_form lane names, as the subagent reads them; stops with Cannot where one is
    a form `lay.py write` would now refuse."""
    for named in places["form"]:
        why = in_form.refused(named, s.root)
        if why:
            raise Cannot(cannot(on(lane, s), why, LAY_AGAIN.format(plugin=s.plugin)))
    return run_only.named(places["form"], s.root)


Check = Callable[[Subagent, dict[str, Any]], "list[Said]"]


def guarded(check: Check) -> Callable[[str, str, str, dict[str, Any], str], list[Said]]:
    """The check run on the event of the subagent of the name, of the plugin at root of the name
    given, `wrong` saying where the event is not as Claude Code hands it: nothing said where the
    subagent has no lanes and no routes, and the error where lane cannot check it."""

    def run(root: str, plugin: str, name: str, event: dict[str, Any], wrong: str) -> list[Said]:
        try:
            found = subagent(root, plugin, name, event, wrong)
            return [] if found is None else check(found, event)
        except Cannot as stop:
            return [stop.said]

    run.__doc__ = check.__doc__
    return run


def sentences(found: list[rules.Laid]) -> Said:
    """The break of the lanes, told by their sentences, a line each."""
    return Said("\n".join(lanes.sentence(g.lane, g.takes) for g in found))


def tool_checked(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's PreToolUse event is told: nothing where the call goes through; the
    sentences it breaks; a held command's sentence, put to the person; or an error where its tool's
    field is not as Claude Code gives it, or lane cannot check a lane that judges the call."""
    tool, given = event["tool_name"], event["tool_input"]
    if s.foreign():
        return []
    if tool not in WATCHED:
        return []
    action, field = WATCHED[tool]
    # Grep given no path searches the folder the call is made in.
    value = given.get(field, "." if tool == "Grep" else None)
    out = schema.held({"type": "string"}, value)
    if out is not None:
        raise Cannot(unshaped(s.name, f"$.tool_input.{field}{out.told()[1:]}"))
    checks = {"read": read_checked, "write": write_checked, "run": run_checked}
    return checks[action](s, event, value)


def read_checked(s: Subagent, event: dict[str, Any], path: str) -> list[Said]:
    """What a read of the path is told: nothing where the subagent has no read_only lane, a lane's
    value is null, or the path is one of the inputs, the forms of its in_form lanes or its own
    part, or lies under one; the read_only lanes' sentences otherwise."""
    judging = s.of("read_only")
    if not judging:
        return []
    inputs: list[str] = []
    for lane in judging:
        places = places_of(lane, s)
        if places is None:
            return []
        inputs += places["input"]
    for lane in s.of("in_form"):
        places = places_of(lane, s)
        inputs += forms_of(lane, s, places) if places else []
    # The subagent's own part it was given whole as it started, so reading it again breaks no rule.
    inputs += [p for p in [step.part(s.root, s.name)] if p]
    return [] if read_only.allows(path, inputs, s.root, event["cwd"]) else [sentences(judging)]


def write_checked(s: Subagent, event: dict[str, Any], path: str) -> list[Said]:
    """What a write of the path is told: write_only's sentences where it has such lanes and the
    path is none of their outputs nor under one, a lane's value null letting it through; each
    edit_only lane's sentence where the call changes its output, once it is there, by other than
    Edit; and each in_form lane's sentence, with the point, where the call writes its output out of
    its form."""
    cwd, judging = event["cwd"], s.of("write_only")
    if judging:
        allowed = [places_of(g, s) for g in judging]
        if not any(p is None or write_only.allows(path, p["output"], s.root, cwd) for p in allowed):
            return [sentences(judging)]
    told = []
    for lane in s.of("edit_only"):
        places = places_of(lane, s)
        tool = event["tool_name"]
        if places and not edit_only.allows(tool, path, places["output"], s.root, cwd):
            told.append(sentences([lane]))
    for lane in s.of("in_form"):
        places = places_of(lane, s)
        if places is None:
            continue
        forms_of(lane, s, places)
        point = in_form.out_of(event["tool_name"], event["tool_input"], places, s.root, cwd)
        if point:
            told.append(Said(f"{lanes.sentence(lane.lane, lane.takes)}\n{point}"))
    return told


def run_checked(s: Subagent, event: dict[str, Any], command: str) -> list[Said]:
    """What a run of the command is told: a held command put to the person with its hold lane's
    sentence; a result command, what is missing of the lanes checked at the end; where the
    subagent has no run_only lane, nothing, but for a run of its result script on a result it may
    not give, told the sentence of its last step and the commands it gives its results by;
    otherwise nothing where the command is one its lanes name, or a lane's value is null, and the
    sentences of its run_only and hold lanes, and the commands it may run, each value put in, where
    it is not."""
    judging = s.of(*RUNS)
    named: list[tuple[rules.Laid, list[str]]] = []
    values: dict[str, list[str]] = {}
    for lane in judging:
        places = places_of(lane, s)
        if places is None:
            return []
        named.append((lane, places[RUNS[lane.lane]]))
        values.update(parts_of(lane, s) or {})
    cwd = event["cwd"]
    for lane, takes in named:
        # Of the lanes judging a command, hold is the first in order.
        holding = lane.lane == "hold"  # pragma: no mutate
        if holding and run_only.allows(command, takes, s.root, cwd, values):
            return [sentences([lane])._replace(ask=True)]
    results = s.commands("result")
    if command.strip() in results:
        return ended(s, cwd)
    if not any(g.lane == "run_only" for g in judging):
        # A result command ends in its result, so one of another result has the same words first.
        if command.strip().rsplit(" ", 1)[0] not in {c.rsplit(" ", 1)[0] for c in results}:
            return []
        listed = ", ".join(f"`{c}`" for c in results)
        return [Said(f"{lanes.sentence('result', results)}\n{MAY_RUN.format(listed=listed)}")]
    takes = list(dict.fromkeys(c for _, each in named for c in each))
    if run_only.allows(command, takes, s.root, cwd, values):
        return []
    told = [lanes.sentence(g.lane, g.takes) for g in judging if g.lane in ("run_only", "hold")]
    listed = ", ".join(f"`{c}`" for c in run_only.put(takes, s.root, values))
    told.append(MAY_RUN.format(listed=listed))
    if any(run_only.DEPENDENCY.search(t) for t in takes):
        told.append(DEPENDENCY_FOLDER)
    return [Said("\n".join(told))]


def ended(s: Subagent, cwd: str) -> list[Said]:
    """What the subagent's result command is told: each lane checked at the end, and each in_form
    lane, whose work is missing, by its sentence, with what is missing on the next line; nothing
    where none is."""
    told = []
    run = called.calls(s.session, s.agent, True)
    checks = {**lanes.END, "in_form": in_form.missing}
    for lane in [g for g in s.laid if g.lane in checks]:
        held(lane, s)
        places = places_of(lane, s)
        if places is None:
            continue
        if lane.lane == "in_form":
            forms_of(lane, s, places)
        items, values = items_of(lane, s), parts_of(lane, s) or {}
        done = Done(s.root, cwd, called.calls(s.session, s.agent), run, items, values)
        try:
            missing = checks[lane.lane](places, done)
        except ports.Failed as why:
            fix = ADAPTER.format(plugin=s.plugin, adapter=lane.adapter)
            raise Cannot(cannot(on(lane, s), f"the adapter {lane.adapter} {why}", fix)) from None
        if missing:
            told.append(Said(f"{lanes.sentence(lane.lane, lane.takes)}\n{missing}"))
    return told


def items_of(lane: rules.Laid, s: Subagent) -> Callable[[str, str], list[str]]:
    """How the lane reads the items of an input, given its path and text: by its adapter where it
    names one, by lane's reading otherwise."""

    def read(path: str, text: str) -> list[str]:
        given = {"input": path, "text": text}
        if lane.adapter is None:
            return ports.read("items", given)["items"]
        adapter = os.path.join(s.root, lane.adapter)
        return ports.run(adapter, "items", given, s.root, ports.left(s.start))["items"]

    return read


def call_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's PostToolUse event is told: nothing; the call is kept, and the result
    where it is a result command of the subagent's."""
    tool, given = event["tool_name"], event["tool_input"]
    if not s.foreign():
        s.keep(called.call(tool, given))
    command = str(given.get("command", "")).strip() if tool == "Bash" else ""
    on_ = s.gave(command, event["cwd"]) if command else None
    if on_ is not None:
        s.keep(called.gave(on_))
    return []


def joined(before: routes.Next, name: str) -> str:
    """How the run's start of the subagent of the name, made with the next start `before`,
    is joined to the starts before it: as a further run, where runs of it go and more may start; as
    a run started again, where it is due again; or not."""
    if before.name != name:
        return ""
    if before.more:
        return routes.MORE
    return routes.AGAIN if before.again else ""


def start_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's SubagentStart event is told: its start is kept; it is given its part
    whole, the plugin's folder put in, where its entry names one, or an error where the part is not
    there."""
    s.keep(called.START)
    told = []
    part = step.part(s.root, s.name)
    if part is not None:
        shown = os.path.relpath(part, s.root)
        try:
            with open(part, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            fix = PART.format(plugin=s.plugin, part=shown)
            raise Cannot(cannot(f"the lanes of {s.name}", f"its part {shown} is not there", fix))
        told.append(Said(text.replace(step.ROOT, s.root), plain=True))
    return told


def end_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's SubagentStop event is told: a subagent giving a result, kept going once
    with the sentence of its last step, as it reads it, where it gave none; any other end is
    kept."""
    ending = [g for g in s.laid if g.lane == "result"]
    if ending and not event["stop_hook_active"] and called.result(s.session, s.agent) is None:
        # A subagent has one result lane, on its last step.
        commands = run_only.named(ending[0].takes, s.root)  # pragma: no mutate
        told_ = [lanes.sentence("result", commands)]
        if s.foreign():
            told_.append(DEPENDENCY_FOLDER)
        return [Said("\n".join(told_))]
    s.keep(called.END)
    return []


def left(m: Main, due: routes.Next) -> Said:
    """The note telling the user that the run was let end with the start due left, and which step
    of the plugin must be fixed: the last of the subagent due, where it ended with no result, or
    the skill's step the routes lie on otherwise; for a dependency's subagent due again, that its
    maker must have it give a result the routes take, or the plugin's maker must route the one it
    gives."""
    lead = m.skill()
    if due.again and ":" in due.name:
        dependency, own = due.name.split(":")
        results = lanes.listed(routes.ons(m.routes, due.name))
        text = LEFT_DEPENDENCY.format(
            lead=lead, name=due.name, dependency=dependency, own=own, results=results
        )
        return Said(
            text + f", or the maker of {m.plugin} must route the result it gives.", note=True
        )
    if due.again:
        lines = step.lines_of(m.root, due.name)
        file = os.path.relpath(str(step.steps_file(m.root, due.name)), m.root)
        at = GIVES_IT.format(step=step.last(lines), name=due.name, file=file)
        why = f", as {due.name} ended with no result"
    else:
        file = os.path.relpath(str(step.steps_file(m.root, lead, skill=True)), m.root)
        at = STARTS_IT.format(step=m.routes["step"], lead=lead, file=file)
        why = ""
    text = LEFT.format(lead=lead, plugin=m.plugin, name=due.name, why=why, at=at)
    return Said(text, note=True)


class Main(NamedTuple):
    """The main conversation as the guard holds it to the routes: the plugin's folder and name, the
    session as the plugin's guard keeps its record, and the routes laid."""

    root: str
    plugin: str
    session: str
    routes: dict[str, Any]

    def skill(self) -> str:
        """The skill the routes start from."""
        return str(self.routes["orchestrator"])

    def giving(self) -> list[str]:
        """The subagents and dependencies' skills the routes start, each giving a result."""
        return routes.giving(self.routes)

    def starts(self) -> list[routes.Start]:
        """The starts of the run, as they came back."""
        return called.starts(self.session, called.RUN, self.giving(), self.plugin)

    def due(self) -> routes.Next:
        """The run's next start, from its starts kept and the result each gave."""
        try:
            return routes.next_start(
                self.routes,
                self.starts(),
                lambda a: called.result(self.session, a),
                lambda a: called.ended(self.session, a),
                lambda a: called.left_without_result(self.session, a),
            )
        except routes.Unordered as why:
            fix = ORDER.format(plugin=self.plugin, name=why.name)
            raise Cannot(cannot_main(f"the routes of {self.skill()}", str(why), fix)) from None
        except ValueError as why:
            raise Cannot(
                cannot_main(f"the routes of {self.skill()}", str(why), LANES_FAULT)
            ) from None

    def begun(self) -> bool:
        """Whether a run of the skill has begun and was not let end; stops with Cannot where its
        record cannot be read."""
        try:
            return called.begun(self.session)
        except ValueError as why:
            raise Cannot(
                cannot_main(f"the routes of {self.skill()}", str(why), LANES_FAULT)
            ) from None

    def on(self) -> bool:
        """Whether a run of the skill is on: begun, and a start still due or waited for."""
        return self.begun() and self.due().kind != "end"

    def moving(self) -> routes.Start | None:
        """The move of a dependency's skill begun in the run and not ended with a result, during
        which the dependency's guard holds the main conversation; None where none is."""
        last = self.starts()[-1:]
        if last and last[0].status == SKILL and not called.ended(self.session, last[0].agent):
            return last[0]
        return None

    def told(self) -> list[Said]:
        """The next start, as the main conversation is told it: the line of the start due, the
        wait or the end, the end told once for the results that led to it."""
        due = self.due()
        line = routes.line(due, self.plugin)
        # A next start is `end`, `reply`, `start` or `wait`, `end` the first of them in order.
        if due.kind == "end":  # pragma: no mutate
            seen = sum(len(called.kept(self.session, s.agent)) for s in self.starts())
            if called.told(self.session, line, seen):
                return []
            called.keep(self.session, called.RUN, called.said(line, seen))
        return [Said(line)]

    def ended_with_none(self) -> list[str]:
        """The IDs of the run's starts that ended with no result, after each was kept going once."""
        return [
            r.agent
            for r in self.starts()
            if called.ended(self.session, r.agent) and called.result(self.session, r.agent) is None
        ]


# How a dependency's skill begun in the run is kept, in place of the status of a subagent's start.
SKILL = "skill"


def main(root: str, plugin: str, event: dict[str, Any], wrong: str) -> Main | None:
    """The main conversation of the plugin at root of the name given, as the guard holds it; None
    where no routes are laid, so the main conversation is never held, or where the event holds no
    session, as no run can be told. Stops with Cannot where hooks/lanes.json cannot be read, its
    routes cannot be followed, or the event is not as Claude Code hands it, as `wrong` says, each
    only while a run is on, as outside a run nothing of the main conversation is touched."""
    given = event.get("session_id")
    if not isinstance(given, str) or not called.ID.fullmatch(given):
        return None
    session = called.record(plugin, given)
    try:
        laid = rules.read(root)
    except ValueError as why:
        if not Main(root, plugin, session, {"orchestrator": ""}).begun():
            return None
        fix = LAY_AGAIN.format(plugin=plugin)
        raise Cannot(cannot_main("the routes of the run", str(why), fix)) from None
    routed = rules.routes_of(laid)
    if routed is None:
        return None
    m = Main(root, plugin, session, routed)
    why = routes.refused(routed)
    if why and m.begun():
        fix = LAY_AGAIN.format(plugin=plugin)
        raise Cannot(cannot_main(f"the routes of {m.skill()}", f"{rules.FILE} {why}", fix))
    if why:
        return None
    if wrong and m.on():
        said = f"the hook was handed no event as Claude Code hands it, {wrong}"
        raise Cannot(cannot_main(f"the routes of {m.skill()}", said, CLAUDE_CODE))
    return None if wrong else m


MainCheck = Callable[[Main, dict[str, Any]], "list[Said]"]


def held_main(check: MainCheck) -> Callable[[str, str, dict[str, Any], str], list[Said]]:
    """The check run on the event of the main conversation of the plugin at root of the name
    given, `wrong` saying where the event is not as Claude Code hands it: nothing said where no
    routes are laid, and the error where lane cannot check it."""

    def run(root: str, plugin: str, event: dict[str, Any], wrong: str) -> list[Said]:
        try:
            found = main(root, plugin, event, wrong)
            return [] if found is None else check(found, event)
        except Cannot as stop:
            return [stop.said]

    run.__doc__ = check.__doc__
    return run


def begin(m: Main) -> list[Said]:
    """What the main conversation is told as the skill the routes name is called: nothing where a
    run is on already and does not wait for the user; the first start, a run begun, where the
    skill's step still says the routes' sentence, a run that waits for the user ended first, as a
    new call of the skill is the user's, and the run would otherwise wait with no way to be let go;
    an error otherwise, no run begun, as its step was not laid by `lay.py write`."""
    if m.on() and m.due().kind != "reply":
        return []
    said = lanes.sentence("follow_routes", [])
    if not step.holds(m.root, m.skill(), m.routes["step"], said, skill=True):
        gone = f"step {m.routes['step']} no longer says: {said}".rstrip(".")
        fix = LAY_AGAIN.format(plugin=m.plugin)
        raise Cannot(
            cannot_main(f"follow_routes on step {m.routes['step']} of {m.skill()}", gone, fix)
        )
    called.keep(m.session, called.RUN, called.START)
    return m.told()


def expanded(m: Main, event: dict[str, Any]) -> list[Said]:
    """What the main conversation's UserPromptExpansion is told: the first start, where the
    command typed is the skill's, as `begin` says; nothing otherwise."""
    if event["command_name"] != f"{m.plugin}:{m.skill()}":
        return []
    return begin(m)


def prompted(m: Main, event: dict[str, Any]) -> list[Said]:
    """What the main conversation's UserPromptSubmit is told, a task-notification of a subagent's
    end among them, and the user's answer to a subagent's point: the next start, or the point to
    put to the user, while a run is on and no dependency's skill moves; nothing otherwise."""
    if not m.begun() or m.moving() is not None:
        return []
    return m.told()


def starting(m: Main, tool: str, given: dict[str, Any]) -> bool:
    """Whether the main conversation's call is a start of the run: an Agent call of a subagent of
    the plugin or of one the routes name, or a Skill call of a dependency's skill they name."""
    if follow_routes.started(tool, given, m.giving(), m.plugin):
        return True
    kind = given.get("subagent_type")
    # No tool Claude Code names sorts before Agent.
    agent = tool == follow_routes.AGENT  # pragma: no mutate
    return agent and isinstance(kind, str) and kind.startswith(f"{m.plugin}:")


def start_checked(m: Main, event: dict[str, Any]) -> list[Said]:
    """What the main conversation's PreToolUse event is told while a run is on and no dependency's
    skill moves: a start not due, or a message resuming a start that ended with no result, stopped
    with the sentence and the start due; any other call goes through."""
    tool, given = event["tool_name"], event["tool_input"]
    if not m.on() or m.moving() is not None:
        return []
    due = m.due()
    if starting(m, tool, given):
        if follow_routes.allows(tool, given, due, m.plugin):
            return []
    elif not follow_routes.resumes(tool, given, m.ended_with_none()):
        return []
    return [Said(follow_routes.WORDING), Said(routes.line(due, m.plugin))]


def main_kept(m: Main, event: dict[str, Any]) -> list[Said]:
    """What the main conversation's PostToolUse event is told: the first start, as the Skill call of
    the skill the routes name comes back; while a run is on, the wait, as a start comes back kept
    under the ID it gives, or the error and the start still due where it did not come back as
    Claude Code gives it; a dependency's skill begun, kept with nothing told, and the next start as
    the run of its result script comes back; nothing otherwise."""
    tool, given, back = event["tool_name"], event["tool_input"], event["tool_response"]
    named = back.get("commandName") if isinstance(back, dict) else None
    if tool == follow_routes.SKILL and named == f"{m.plugin}:{m.skill()}":
        return begin(m)
    if not m.on():
        return []
    move = m.moving()
    if move is not None:
        return moved(m, move, event)
    name = follow_routes.started(tool, given, m.giving(), m.plugin)
    if name is None:
        return []
    before = m.due()
    if tool == "Skill":
        use = event.get("tool_use_id")
        if not isinstance(use, str) or not called.ID.fullmatch(use):
            said = "the hook was handed no event as Claude Code hands it, $.tool_use_id: no ID"
            return [cannot_main(f"the routes of {m.skill()}", said, CLAUDE_CODE)]
        made = {"status": SKILL, "agentId": use}
        called.keep(m.session, called.RUN, called.call(tool, given, made))
        return []
    out = schema.held(BACK, back)
    if out is not None:
        said = (
            f"the hook was handed no event as Claude Code hands it, $.tool_response{out.told()[1:]}"
        )
        error = cannot_main(f"the routes of {m.skill()}", said, CLAUDE_CODE)
        return [error, Said(routes.line(before, m.plugin))]
    called.keep(m.session, called.RUN, called.call(tool, given, back, joined(before, name)))
    return m.told()


def moved(m: Main, move: routes.Start, event: dict[str, Any]) -> list[Said]:
    """What the main conversation's PostToolUse is told while a dependency's skill moves: the next
    start, as a run of the dependency's result script with a result a route from the skill is on
    comes back, the result kept; nothing otherwise, as the dependency's guard holds the
    conversation meanwhile."""
    if event["tool_name"] != "Bash":
        return []
    command = str(event["tool_input"].get("command", "")).strip()
    for on in routes.ons(m.routes, move.name):
        gives = routes.command(move.name, on)
        if run_only.allows(command, [gives], m.root, event["cwd"], {}):
            called.keep(m.session, move.agent, called.gave(on))
            called.keep(m.session, move.agent, called.END)
            return m.told()
    return []


def turn_ended(m: Main, event: dict[str, Any]) -> list[Said]:
    """What the main conversation's Stop event is told while a run is on and no dependency's skill
    moves: where a start is due and no start of the run still runs, kept going once with the
    sentence and the start due, and let end after, the run ended and the user told what is left
    and the step to fix, as a hold with no end would need a person to break it; nothing
    otherwise, as while the user is to answer a subagent's point, whose route waits."""
    if not m.on() or m.moving() is not None:
        return []
    due = m.due()
    if due.kind != "start":
        return []
    if not event["stop_hook_active"]:
        return [Said(follow_routes.WORDING), Said(routes.line(due, m.plugin))]
    called.keep(m.session, called.RUN, called.END)
    return [left(m, due)]


# The guard's check of each event of the main conversation.
MAIN = {
    "UserPromptExpansion": held_main(expanded),
    "UserPromptSubmit": held_main(prompted),
    "PreToolUse": held_main(start_checked),
    "PostToolUse": held_main(main_kept),
    "Stop": held_main(turn_ended),
}


def handed(plugin: str, event: dict[str, Any], held_: str) -> None:
    """Keeps, of a call made by anyone in the session, what a run of a subagent of the plugin is
    given: an Agent call starting one, as it comes back, its prompt under the ID of the run it
    gives back, so runs of one subagent at once are each given their own; a SendMessage call's
    message, as it is made, under the run of the ID it is sent to, where that run's calls are
    kept. Anything not in the fields Claude Code documents is left, as a run whose prompt is not
    kept is told so by the lane that needs its value."""
    tool, given = event.get("tool_name"), event.get("tool_input")
    session, use = event.get("session_id"), event.get("tool_use_id")
    if not isinstance(given, dict) or not isinstance(session, str) or not isinstance(use, str):
        return
    session = called.record(plugin, session)
    # Only the Agent tool, before which no tool of Claude Code's sorts, starts a run.
    starting = tool == "Agent"  # pragma: no mutate
    # Of the events of a call, PostToolUse, PostToolUseFailure and PreToolUse, a call comes back at
    # PostToolUse, the first of them in order, and is made at PreToolUse, the last.
    returned = held_ == "PostToolUse"  # pragma: no mutate
    made = held_ == "PreToolUse"  # pragma: no mutate
    try:
        if starting and returned:
            kind, prompt = given.get("subagent_type"), given.get("prompt")
            back = event.get("tool_response")
            agent = back.get("agentId") if isinstance(back, dict) else None
            ours = isinstance(kind, str) and kind.startswith(f"{plugin}:")
            if ours and isinstance(prompt, str) and isinstance(agent, str):
                called.keep(session, agent, called.given(prompt))
        elif tool == "SendMessage" and made:
            to, text = given.get("to"), given.get("message")
            sent = isinstance(to, str) and isinstance(text, str) and called.ID.fullmatch(to)
            if sent and os.path.exists(called.file(session, str(to), False)):
                called.keep(session, str(to), called.message(str(text)))
    except ValueError:
        return


check = guarded(tool_checked)
came_back = guarded(call_kept)
started = guarded(start_kept)
stopping = guarded(end_kept)
