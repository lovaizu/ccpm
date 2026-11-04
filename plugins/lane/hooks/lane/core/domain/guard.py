"""The guard: decides, of each event of a subagent with lanes laid or named by the routes, what it
is told, from the event's input alone, as Claude Code documents it, and from the calls kept; and,
where it cannot decide, the error that says what is wrong and who must fix it.

At PreToolUse, a call goes through, is stopped with the sentences it breaks, or, a held command, is
put to the person with its sentence. A subagent with lanes runs a command only where a run_only,
hold or test_after lane names it, whole, or its result command does: a call of Bash is judged by
those lanes of the subagent together, as lane does not know which step the subagent is on. A read
is judged by its read_only lanes together, and a write by its write_only lanes together, each going
through where there is none; a write of an in_form lane's output is held to its form. Any other
tool goes through. A result command is let through only once the lanes checked at the end hold.
The orchestrator makes no call but the start due while one is due, and starts none while a
subagent it started runs in the background, but more runs of it where the routes fan it out. It
sends no message to a run that ended with no result, as the run started again takes its place.

A take `{<name>}` is the run's value of the name, read at the values port from the texts the run
was given: the prompt of the Agent call that started it, kept under the ID of the run as the call
comes back, and each message sent to it after. A call the run makes before its start has come back
waits for it a short time, within the hook's; a value given as null lets the lane's call or end
through on that run. A subagent whose file no longer sets `background: true` is an error at each of
its events, as only a start in the background comes back with the run's ID before the run's
calls.

At PostToolUse, the call is kept, with the result where it is a result command; the orchestrator is
told the next start as each of its starts comes back, kept with how it is joined to the starts
before it, as a further run of a subagent the routes fan out or a run started again, or, at
PostToolUseFailure, the start still due. At SubagentStart, the run's start is kept, the subagent
given its part whole where its entry names one, and the orchestrator told the next start. At
SubagentStop, the orchestrator is kept going while a start is due, and a subagent giving a result
is kept going once where it gave none; any other end is kept, so a start in the background counts
once its subagent has ended."""

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
from lanes import follow_routes, in_form, read_only, run_only, write_only
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
RUN_NONE = "You may run no command."
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
# What the operator is told as the orchestrator, kept going once with a start due, is let end: the
# start left, and the step that must be fixed, the orchestrator's own or that of the subagent that
# ended with no result.
LEFT = (
    "lane let {lead} end with `{plugin}:{name}` still due{why}: the maker of {plugin} must fix {at}"
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

    def orchestrator(self) -> bool:
        """Whether the subagent is the routes' orchestrator."""
        return self.routes is not None and self.routes["orchestrator"] == self.name

    def giving(self) -> list[str]:
        """The subagents the orchestrator's routes start, each giving a result."""
        return routes.giving(self.routes) if self.routes else []

    def due(self) -> routes.Next:
        """The orchestrator's next start, from its starts kept and the results of their runs."""
        assert self.routes is not None
        try:
            started = called.starts(self.session, self.agent, self.giving(), self.plugin)
            return routes.next_start(
                self.routes,
                started,
                lambda a: called.result(self.session, a),
                lambda a: called.ended(self.session, a),
                lambda a: called.left_without_result(self.session, a),
            )
        except routes.Unordered as why:
            fix = ORDER.format(plugin=self.plugin, name=why.name)
            raise Cannot(cannot(f"the lanes of {self.name}", str(why), fix)) from None
        except ValueError as why:
            raise Cannot(cannot(f"the lanes of {self.name}", str(why), LANES_FAULT)) from None

    def ended_with_none(self) -> list[str]:
        """The IDs of the orchestrator's runs that ended with no result, after each was kept going
        once, each of a subagent that gives one."""
        started = called.starts(self.session, self.agent, self.giving(), self.plugin)
        return [
            r.agent
            for r in started
            if called.ended(self.session, r.agent) and called.result(self.session, r.agent) is None
        ]

    def keep(self, entry: dict[str, Any]) -> None:
        """Keeps the entry under the subagent's run."""
        called.keep(self.session, self.agent, entry)

    def told(self, due: routes.Next) -> Said:
        """The next start, as the orchestrator is told it."""
        return Said(routes.line(due, self.plugin))

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
    if routed is not None and routed["orchestrator"] == name:
        found.append(rules.Laid(routed["step"], "follow_routes", []))
    ons = rules.gives(routed, name, [g.lane for g in found])
    if ons:
        # The last step's number, or none that a step has, where its file has no step.
        last = step.last(step.lines_of(root, name)) or 0
        found.append(rules.Laid(last, "result", [routes.command(name, on) for on in ons]))
    session, agent = event["session_id"], event["agent_id"]
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
    for lane in s.of("follow_routes"):
        due = s.due()
        allowed = follow_routes.allows(tool, given, due, s.plugin)
        if not allowed or follow_routes.resumes(tool, given, s.ended_with_none()):
            return [Said(follow_routes.WORDING), s.told(due)]
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
    path is none of their outputs nor under one, a lane's value null letting it through; and each
    in_form lane's sentence, with the point, where the call writes its output out of its form."""
    cwd, judging = event["cwd"], s.of("write_only")
    if judging:
        allowed = [places_of(g, s) for g in judging]
        if not any(p is None or write_only.allows(path, p["output"], s.root, cwd) for p in allowed):
            return [sentences(judging)]
    told = []
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
    sentence; nothing where the command is one its lanes name, or a lane's value is null, but a
    result command with what is missing of the lanes checked at the end; the sentences of its
    run_only and hold lanes, and the commands it may run, each value put in, otherwise."""
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
    if command.strip() in s.commands("result"):
        return ended(s, cwd)
    takes = list(dict.fromkeys(c for _, each in named for c in each))
    if run_only.allows(command, takes, s.root, cwd, values):
        return []
    told = [lanes.sentence(g.lane, g.takes) for g in judging if g.lane in ("run_only", "hold")]
    listed = ", ".join(f"`{c}`" for c in run_only.put(takes, s.root, values))
    told.append(MAY_RUN.format(listed=listed) if takes else RUN_NONE)
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
    """What the subagent's PostToolUse event is told: the call is kept, and the result where it is
    a result command of the subagent's; the orchestrator is told the next start as its start comes
    back, or, where it did not come back as Claude Code gives it, the error and the start still
    due."""
    tool, given, back = event["tool_name"], event["tool_input"], event["tool_response"]
    name = follow_routes.started(tool, given, s.giving(), s.plugin) if s.orchestrator() else None
    if name:
        before = s.due()
        # A next start is `end`, `start` or `wait`, `end` the first of them in order.
        if before.kind == "end":  # pragma: no mutate
            s.keep(called.call(tool, given))
            return []
        out = schema.held(BACK, back)
        if out is not None:
            s.keep(called.call(tool, given))
            return [unshaped(s.name, f"$.tool_response{out.told()[1:]}"), s.told(before)]
        s.keep(called.call(tool, given, back, joined(before, name)))
        return [s.told(s.due())]
    s.keep(called.call(tool, given))
    command = str(given.get("command", "")).strip() if tool == "Bash" else None
    for on_, gives in zip(s.ons, s.commands("result")):
        if command == gives:
            s.keep(called.gave(on_))
    return []


def joined(before: routes.Next, name: str) -> str:
    """How the orchestrator's start of the subagent of the name, made with the next start `before`,
    is joined to the starts before it: as a further run, where runs of it go and more may start; as
    a run started again, where it is due again; or not."""
    if before.name != name:
        return ""
    if before.more:
        return routes.MORE
    return routes.AGAIN if before.again else ""


def failure_told(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's PostToolUseFailure event is told: the orchestrator, the start still due
    where its start failed; nothing else, and nothing kept, as a call that failed gives no
    result."""
    if s.orchestrator() and follow_routes.started(
        event["tool_name"], event["tool_input"], s.giving(), s.plugin
    ):
        due = s.due()
        # A next start is `end`, `start` or `wait`, `end` the first of them in order.
        if due.kind == "end":  # pragma: no mutate
            return []
        return [s.told(due)]
    return []


def start_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's SubagentStart event is told: its run's start is kept; it is given its
    part whole, the plugin's folder put in, where its entry names one, or an error where the part
    is not there; and the orchestrator is told the next start."""
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
    return told + ([s.told(s.due())] if s.orchestrator() else [])


def end_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's SubagentStop event is told: the orchestrator is kept going once with the
    sentence and the start while one is due, and let end after, the operator told what is left and
    the step to fix, as only the plugin's maker can mend a run that stops so; a subagent giving a
    result, kept going once with the sentence of its last step, as it reads it, where it gave none;
    any other end is kept."""
    told = []
    if s.orchestrator():
        due = s.due()
        if not follow_routes.ends(due):
            if not event["stop_hook_active"]:
                return [Said(follow_routes.WORDING), s.told(due)]
            told.append(left(s, due))
    ending = [g for g in s.laid if g.lane == "result"]
    if ending and not event["stop_hook_active"] and called.result(s.session, s.agent) is None:
        # A subagent has one result lane, on its last step.
        commands = run_only.named(ending[0].takes, s.root)  # pragma: no mutate
        return [Said(lanes.sentence("result", commands))]
    s.keep(called.END)
    return told


def left(s: Subagent, due: routes.Next) -> Said:
    """The note telling the operator that the orchestrator was let end with the start due left,
    and which step of the plugin must be fixed: the last of the subagent due, where it ended with
    no result, or the orchestrator's step the routes lie on otherwise."""
    assert s.routes is not None
    if due.again:
        lines = step.lines_of(s.root, due.name)
        file = os.path.relpath(str(step.steps_file(s.root, due.name)), s.root)
        at = GIVES_IT.format(step=step.last(lines), name=due.name, file=file)
        why = f", as {due.name} ended with no result"
    else:
        file = os.path.relpath(str(step.steps_file(s.root, s.name)), s.root)
        at = STARTS_IT.format(step=s.routes["step"], lead=s.name, file=file)
        why = ""
    text = LEFT.format(lead=s.name, plugin=s.plugin, name=due.name, why=why, at=at)
    return Said(text, note=True)


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
failed = guarded(failure_told)
started = guarded(start_kept)
stopping = guarded(end_kept)
