"""The guard: decides, of each event of a subagent with lanes laid or named by the routes, what it
is told, from the event's input alone, as Claude Code documents it, and from the calls kept; and,
where it cannot decide, the error that says what is wrong and who must fix it.

At PreToolUse, a call goes through or is stopped with the sentences it breaks. A subagent with
lanes runs a command only where a lane names it, whole, or its result command does: a call of Bash
is judged by the run lanes of the subagent together, as lane does not know which step the subagent
is on. A write is judged by its write lanes together, and goes through where it has none. Any other
tool goes through. The orchestrator makes no call but the start due while one is due, and starts
none while a subagent it started runs in the background.

At PostToolUse, the call is kept, with the result where it is a result command; the orchestrator is
told the next start as each of its starts comes back, or, at PostToolUseFailure, the start still
due. At SubagentStart, the run's start is kept, and the orchestrator told the next start. At
SubagentStop, the orchestrator is kept going while a start is due, and a subagent giving a result
is kept going once where it gave none; any other end is kept, so a start in the background counts
once its subagent has ended."""

from __future__ import annotations

from typing import Any, Callable, NamedTuple

import called
import lanes
import routes
import rules
import schema
import step
from lanes import follow_routes, run_only

# Each tool a lane judges, with the action its call is and the field of its input the lane judges.
WATCHED = {
    "Bash": ("run", "command"),
    "Write": ("write", "file_path"),
    "Edit": ("write", "file_path"),
    "NotebookEdit": ("write", "notebook_path"),
}
# What a subagent is told, after its run lanes' sentences, of the commands it may run.
MAY_RUN = "The commands you may run, each word for word: {listed}."
RUN_NONE = "You may run no command."
# What a subagent is told to do where lane cannot check a lane, given who must fix it: a role asks
# the main conversation for what lies outside its work and goes on with the rest, as
# dev/architecture.md's Asking for what lies outside the work says.
ASK = "Ask the main conversation for the fix: {fix}. Go on with the rest of your work meanwhile."
LAY_AGAIN = (
    "the maker of {plugin} must lay its lanes again with `lay.py write`, so they match its steps"
)
CLAUDE_CODE = (
    "Claude Code must be updated with `claude update`, and where this goes on, it must be reported"
    " at https://github.com/lovaizu/ccpm/issues"
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
    """What the guard says of an event: a break, told the subagent; or an error, told the subagent
    and the user alike, as only the user can have it fixed."""

    text: str
    error: bool = False


class Cannot(Exception):
    """Where lane cannot check an event: the error it says."""

    def __init__(self, said: Said) -> None:
        super().__init__(said.text)
        self.said = said


class Subagent(NamedTuple):
    """The subagent an event is of, as the guard checks it: the plugin's folder and name, the
    subagent's name, the session and the ID of its run, its lanes with the sentences laid from the
    routes, and the routes where they name it."""

    root: str
    plugin: str
    name: str
    session: str
    agent: str
    laid: list[rules.Laid]
    routes: dict[str, Any] | None

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
            )
        except ValueError as why:
            raise Cannot(cannot(f"the lanes of {self.name}", str(why), LANES_FAULT)) from None

    def keep(self, entry: dict[str, Any]) -> None:
        """Keeps the entry under the subagent's run."""
        called.keep(self.session, self.agent, entry)

    def told(self, due: routes.Next) -> Said:
        """The next start, as the orchestrator is told it."""
        return Said(routes.line(due, self.plugin))

    def commands(self, lane: str) -> list[str]:
        """The commands of the subagent's lanes of the kind, as it reads them in its steps."""
        return [c for g in self.laid if g.lane == lane for c in run_only.named(g.takes, self.root)]


def cannot(on: str, wrong: str, fix: str) -> Said:
    """The error where lane cannot check what `on` names, such as `the lanes of <subagent>` or
    `<lane> on step <n> of <subagent>`, in the form docs/lanes.md gives."""
    return Said(f"lane cannot check {on}: {wrong}. {ASK.format(fix=fix)}", True)


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
    hooks/lanes.json cannot be read, or the event is not as Claude Code hands it, as `wrong`
    says."""
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
    if wrong:
        raise Cannot(unshaped(name, wrong))
    found = list(laid or [])
    if routed is not None and routed["orchestrator"] == name:
        found.append(rules.Laid(routed["step"], "follow_routes", []))
    ons = routes.ons(routed, name) if routed else []
    if ons:
        # The last step's number, or none that a step has, where its file has no step.
        last = step.last(step.lines_of(root, name)) or 0
        found.append(rules.Laid(last, "result", [routes.command(name, on) for on in ons]))
    session, agent = event["session_id"], event["agent_id"]
    return Subagent(root, plugin, name, session, agent, found, routed)


def held(lane: rules.Laid, s: Subagent) -> None:
    """Stops with Cannot where the lane's step no longer says its sentence."""
    said = lanes.sentence(lane.lane, lane.takes)
    if not step.holds(s.root, s.name, lane.step, said):
        on = f"{lane.lane} on step {lane.step} of {s.name}"
        gone = f"step {lane.step} no longer says: {said}".rstrip(".")
        raise Cannot(cannot(on, gone, LAY_AGAIN.format(plugin=s.plugin)))


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


def tool_checked(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's PreToolUse event is told: nothing where the call goes through; the
    sentences it breaks; or an error where its tool's field is not as Claude Code gives it, or a
    step no longer says the sentence of a lane that judges the call."""
    tool, given = event["tool_name"], event["tool_input"]
    for lane in [g for g in s.laid if g.lane == "follow_routes"]:
        held(lane, s)
        due = s.due()
        if not follow_routes.allows(tool, given, due, s.plugin):
            return [Said(follow_routes.WORDING), s.told(due)]
    if tool not in WATCHED:
        return []
    action, field = WATCHED[tool]
    out = schema.held({"type": "string"}, given.get(field))
    if out is not None:
        raise Cannot(unshaped(s.name, f"$.tool_input.{field}{out.told()[1:]}"))
    writing = action == "write"  # pragma: no mutate
    judging = [g for g in s.laid if lanes.action(g.lane) == action]
    if writing and not judging:
        return []
    ending = [] if writing else [g for g in s.laid if g.lane == "result"]
    for lane in judging + ending:
        held(lane, s)
    value = given[field]
    if writing:
        if any(lanes.LANES[g.lane].allows(value, g.takes, s.root, event["cwd"]) for g in judging):
            return []
        return [Said("\n".join(lanes.sentence(g.lane, g.takes) for g in judging))]
    commands = list(dict.fromkeys(s.commands("run_only") + s.commands("result")))
    if value.strip() in commands:
        return []
    told = [lanes.sentence(g.lane, g.takes) for g in judging]
    listed = ", ".join(f"`{c}`" for c in commands)
    told.append(MAY_RUN.format(listed=listed) if commands else RUN_NONE)
    return [Said("\n".join(told))]


def call_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's PostToolUse event is told: the call is kept, and the result where it is
    a result command of the subagent's; the orchestrator is told the next start as its start comes
    back, or, where it did not come back as Claude Code gives it, the error and the start still
    due."""
    tool, given, back = event["tool_name"], event["tool_input"], event["tool_response"]
    if s.orchestrator() and follow_routes.started(tool, given, s.giving(), s.plugin):
        before = s.due()
        if before.kind == "end":
            s.keep(called.call(tool, given))
            return []
        out = schema.held(BACK, back)
        if out is not None:
            s.keep(called.call(tool, given))
            return [unshaped(s.name, f"$.tool_response{out.told()[1:]}"), s.told(before)]
        s.keep(called.call(tool, given, back))
        return [s.told(s.due())]
    s.keep(called.call(tool, given))
    command = str(given.get("command", "")).strip() if tool == "Bash" else None
    ons = routes.ons(s.routes, s.name) if s.routes else []
    for on, gives in zip(ons, s.commands("result")):
        if command == gives:
            s.keep(called.gave(on))
    return []


def failure_told(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's PostToolUseFailure event is told: the orchestrator, the start still due
    where its start failed; nothing else, and nothing kept, as a call that failed gives no
    result."""
    if s.orchestrator() and follow_routes.started(
        event["tool_name"], event["tool_input"], s.giving(), s.plugin
    ):
        due = s.due()
        return [] if due.kind == "end" else [s.told(due)]
    return []


def start_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's SubagentStart event is told: its run's start is kept, and the
    orchestrator told the next start."""
    s.keep(called.START)
    return [s.told(s.due())] if s.orchestrator() else []


def end_kept(s: Subagent, event: dict[str, Any]) -> list[Said]:
    """What the subagent's SubagentStop event is told: the orchestrator is kept going with the
    sentence and the start while one is due; a subagent giving a result, kept going once with the
    sentence of its last step, as it reads it, where it gave none; any other end is kept."""
    if s.orchestrator():
        due = s.due()
        if not follow_routes.ends(due):
            return [Said(follow_routes.WORDING), s.told(due)]
    ending = [g for g in s.laid if g.lane == "result"]
    if ending and not event["stop_hook_active"] and called.result(s.session, s.agent) is None:
        commands = run_only.named(ending[0].takes, s.root)
        return [Said(lanes.sentence("result", commands))]
    s.keep(called.END)
    return []


check = guarded(tool_checked)
came_back = guarded(call_kept)
failed = guarded(failure_told)
started = guarded(start_kept)
stopping = guarded(end_kept)
