"""Decides what the guard does on each moment of a conversation: which of the Runs of the plugin's
skills that go on side by side the moment goes to, whether it lies in a Run and of a role whose
Lanes name it, which facts of it the run record keeps, when a Run starts and ends, whether each
call, start, and end passes, and what the main conversation or the role reads, from the laid set
and the run record alone. The run record keeps no text of a start before a Start takes it, so the
guard asks the adapter for that text again at each moment that needs it, such as the start's
call."""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass

from domain import adapter, results, said
from domain.adapter import StartText
from domain.event import (
    BEGUN,
    CALL,
    COMMAND,
    ENDS,
    RAN,
    REACHED,
    START,
    TURN_ENDS,
    TYPED,
    Call,
    Event,
)
from domain.fault import Fault
from domain.laid_set import START as MOVE_START
from domain.laid_set import LaidSet, Lane, lanes_of
from domain.lanes import End, Where, check_call, check_end
from domain.routes import due, may_end_turn, no_more, opens_start, stand
from domain.run_record import (
    ENDED,
    LAID,
    PERSON,
    PROMPTED,
    SHOWN,
    TURN_ENDED,
    Called,
    Line,
    Noted,
    Result,
    Run,
    Start,
    Tied,
    add,
    load,
)


@dataclass(frozen=True)
class Decision:
    """What the guard gives on a moment: `stop` whether it stops the call, the end, or the prompt,
    `said` what the one stopped reads, and `context` what the main conversation reads beside the
    moment, such as the start due."""

    stop: bool = False
    said: str = ""
    context: str = ""


LET_THROUGH = Decision()

# The text of a start where the plugin has no adapter of a start's text.
_CARRY_OUT = "Carry out your steps"


@dataclass(frozen=True)
class _At:
    """The moment as the guard of the plugin in `root` meets it, with the run records in `temp`
    and the lines of the conversation's record so far."""

    event: Event
    laid_set: LaidSet
    root: str
    temp: str
    lines: tuple[Line, ...]

    def runs(self) -> tuple[Run, ...]:
        return stand(self.lines, self.laid_set, self.event.session)

    def keep(self, line: Line) -> _At:
        add(line, self.temp, self.laid_set.plugin, self.event.session)
        return _At(self.event, self.laid_set, self.root, self.temp, (*self.lines, line))

    def name(self, role: str) -> str:
        """The role's name within the plugin, "" for a role of no Start of this plugin."""
        plugin, _, name = role.partition(":")
        return name if plugin == self.laid_set.plugin and name else ""


def decide(event: Event, laid_set: LaidSet, plugin_root: str, temp: str) -> Decision:
    """What the guard of the plugin in the folder, holding its laid set, gives on the moment, with
    the run records in the folder `temp`. It works out each Run of the conversation from the lines
    of its run record, as `routes.stand` does, and adds to the record, before it answers, each fact
    of the moment that no later payload gives again: a skill's call, a Start let through with its
    skill, its tie to a subagent, a Result that a run of result.py gave, a subagent's end, a command
    typed that a Route waits for or goes after, and each line that a Lane's command printed. It
    stops what it can't check, with why and who must fix it, and never raises."""
    try:
        lines = load(temp, laid_set.plugin, event.session)
        return _MOMENTS.get(event.moment, _let)(_At(event, laid_set, plugin_root, temp, lines))
    except Fault as fault:
        return Decision(stop=True, said=said.cant_check(laid_set.plugin, fault.why, fault.who))


def _let(at: _At) -> Decision:
    return LET_THROUGH


def _typed(at: _At) -> Decision:
    event, laid_set = at.event, at.laid_set
    skill = at.name(event.command)
    if skill in laid_set.skills:
        at = at.keep(Called(skill, PERSON))
        run = at.runs()[-1]
        return Decision(context=_moves(at, [run], at_call=True)) if run.moves else LET_THROUGH
    going = [run for run in at.runs() if not run.ended]
    if laid_set.proposes and going and not event.command:
        at.keep(Noted(PROMPTED))
    return LET_THROUGH


def _call(at: _At) -> Decision:
    event, call = at.event, at.event.call
    runs = at.runs()
    if call is None or not in_run(event, at.laid_set, runs):
        return LET_THROUGH
    if starts_from_main(event):
        return _start(at, runs, call) if call.kind == START and at.name(call.role) else LET_THROUGH
    _, start = _held(runs, event.agent)
    lanes = lanes_of(at.laid_set, start.role)
    where = Where(event.cwd, event.root)
    lane, verdict = check_call(lanes, call, start.values, where, at.root)
    if lane is None:
        return LET_THROUGH
    return _stopped(at, lane, verdict.may, verdict.printed)


def _stopped(at: _At, lane: Lane, may: Sequence[str], printed: str) -> Decision:
    sentence = lane.sentence.replace("${CLAUDE_PLUGIN_ROOT}", at.root)
    return Decision(stop=True, said=said.stop(at.laid_set.plugin, sentence, may, printed))


def _start(at: _At, runs: Sequence[Run], call: Call) -> Decision:
    role = at.name(call.role)
    run = run_of(at.event, at.laid_set, runs)
    if run is not None:
        given = _given(at, run)[role]
        if isinstance(given, Fault):
            raise given
        if opens_start(run, role, call.text, given.text):
            number = 1 + sum(isinstance(line, Start) for line in at.lines)
            at.keep(Start(number, role, call.text, given.values, skill=run.skill))
            return LET_THROUGH
    going = [each for each in runs if not each.ended]
    return Decision(stop=True, said=_moves(at, going))


def _given(at: _At, run: Run) -> dict[str, StartText | Fault]:
    """The text and the run values of each start due in the Run, Lane's own text or the adapter's,
    or the Fault of the adapter where it can't give them."""
    roles = [move.role for move in due(run.moves, "") if move.kind == MOVE_START]
    if not at.laid_set.text_adapter:
        return {role: StartText(_CARRY_OUT) for role in roles}
    program = os.path.join(at.root, "hooks", "adapters", at.laid_set.text_adapter)
    running = [start for start in run.starts if start.running]
    found: dict[str, StartText | Fault] = {}
    for role in roles:
        try:
            found[role] = adapter.start_text(program, role, running, at.event.cwd)
        except Fault as fault:
            found[role] = fault
    return found


def _texts(at: _At, run: Run) -> said.Texts:
    """The text of each start due in the Run, or the Fault of the adapter that can't give it."""
    return {
        role: given if isinstance(given, Fault) else given.text
        for role, given in _given(at, run).items()
    }


def _moves(at: _At, runs: Sequence[Run], at_call: bool = False) -> str:
    """The moves due in each of the Runs, a line for each, `at_call` at the skill's call."""
    plugin = at.laid_set.plugin
    return "\n".join(
        said.moves(plugin, due(run.moves, ""), _texts(at, run), at_call) for run in runs
    )


def _ran(at: _At) -> Decision:
    event = at.event
    runs = at.runs()
    given = results.given(event, at.laid_set, runs)
    if given is not None:
        at.keep(Result(given.role, given.result, given.agent))
    elif at.laid_set.proposes and not event.failed and any(not run.ended for run in runs):
        _laid_or_shown(at)
    return LET_THROUGH


def _laid_or_shown(at: _At) -> None:
    """Keeps what Lane's own `lay.py print` showed, or that `lay.py write` laid, in up's Run."""
    call = at.event.call
    words = call.command.split() if call and call.kind == COMMAND and not at.event.agent else []
    script = os.path.realpath(os.path.join(at.root, "scripts", "lay.py"))
    if len(words) < 3 or words[0] != "python3" or os.path.realpath(words[1]) != script:
        return
    if words[2] == "print":
        at.keep(Noted(SHOWN, text=at.event.printed))
    elif words[2] == "write":
        at.keep(Noted(LAID))


def _begun(at: _At) -> Decision:
    role = at.name(at.event.role)
    for run in at.runs():
        untied = [s for s in run.starts if s.role == role and not s.agent]
        if role and not run.ended and untied:
            at.keep(Tied(untied[0].number, at.event.agent))
            break
    return LET_THROUGH


def _reached(at: _At) -> Decision:
    event = at.event
    run = run_of(event, at.laid_set, at.runs())
    if run is None:
        return LET_THROUGH
    at = at.keep(Noted(ENDED, event.agent, event.status))
    given = result_since(run, event.agent)
    if given is None:
        return LET_THROUGH
    moves, texts = due(run.moves, ""), _texts(at, run)
    return Decision(context=said.gave(at.laid_set.plugin, given.role, given.result, moves, texts))


def _ends(at: _At) -> Decision:
    event = at.event
    runs = at.runs()
    if not in_run(event, at.laid_set, runs):
        return LET_THROUGH
    run, start = _held(runs, event.agent)
    given = result_since(run, event.agent)
    end = End(start.role, event.message, start.values, given.result if given else "")
    lane, verdict = check_end(lanes_of(at.laid_set, start.role), end, Where(event.cwd, event.root))
    if lane is None:
        return LET_THROUGH
    return _stopped(at, lane, verdict.may, verdict.printed)


def _turn_ends(at: _At) -> Decision:
    if at.laid_set.proposes:
        return LET_THROUGH
    runs = [run for run in at.runs() if not run.aside and (not run.ended or run.ending)]
    held = [run for run in runs if not run.ended and not may_end_turn(run)]
    if held:
        return Decision(stop=True, said=_moves(at, held))
    for run in runs:
        stopped = _skills_end(at, run)
        if stopped is not None:
            return stopped
    if any(run.ending for run in runs):
        at.keep(Noted(TURN_ENDED))
    return LET_THROUGH


def _skills_end(at: _At, run: Run) -> Decision | None:
    """The stop of the main conversation's turn by the first Lane of the Run's skill that its end
    breaks, None where it keeps each, the skill's result due once the moves start no more."""
    given = next((r.result for r in reversed(run.results) if not r.agent), "")
    end = End(run.skill, at.event.message, result=given, due=run.ended or no_more(run.moves))
    where = Where(at.event.cwd, at.event.root)
    lane, verdict = check_end(lanes_of(at.laid_set, run.skill), end, where)
    return None if lane is None else _stopped(at, lane, verdict.may, verdict.printed)


def _held(runs: Sequence[Run], agent: str) -> tuple[Run, Start]:
    """The Run that goes on and its last Start that tie the subagent, as `in_run` found them."""
    return next(
        (run, start)
        for run in reversed(runs)
        if not run.ended
        for start in reversed(run.starts)
        if start.agent == agent
    )


def _start_of(run: Run, agent: str) -> Start | None:
    """The last Start of the Run that ties the subagent, None where none does."""
    return next((start for start in reversed(run.starts) if start.agent == agent), None)


_MOMENTS = {
    TYPED: _typed,
    CALL: _call,
    RAN: _ran,
    BEGUN: _begun,
    REACHED: _reached,
    ENDS: _ends,
    TURN_ENDS: _turn_ends,
}


def in_run(event: Event, laid_set: LaidSet, runs: Sequence[Run]) -> bool:
    """Whether the guard checks the moment, given the conversation's Runs: it lies between the call
    of a skill of the plugin and the end of that skill's Run, and comes from the main conversation
    while such a Run goes on and stands aside from no other plugin's run, or from a subagent that a
    Start of such a Run ties, as the principle The guard checks only the run says."""
    going = [run for run in runs if not run.ended and run.session == event.session]
    if starts_from_main(event):
        return any(not run.aside for run in going)
    return any(_start_of(run, event.agent) for run in going)


def run_of(event: Event, laid_set: LaidSet, runs: Sequence[Run]) -> Run | None:
    """The Run among the conversation's that the moment goes to: a subagent's, the Run of the Start
    that its `agent_id` ties; a skill's call, typed or by the Skill tool, the Run of that skill; a
    run of result.py by the main conversation, the Run of the skill that its command names; a start
    of the main conversation, the Run whose moves open it, the one that began first where the moves
    of two open it; and None where none such goes on, as for a subagent that no Start ties."""
    if event.agent:
        return next((run for run in reversed(runs) if _start_of(run, event.agent)), None)
    call = event.call
    if event.moment == TYPED and event.command:
        skill = event.command.partition(":")[2]
        return next((run for run in reversed(runs) if run.skill == skill), None)
    if call is not None and call.kind == START:
        role = call.role.partition(":")[2]
        return next((run for run in runs if not run.ended and _opens(run, role)), None)
    return None


def _opens(run: Run, role: str) -> bool:
    return any(move.kind == MOVE_START and move.role == role for move in due(run.moves, ""))


def result_since(run: Run, agent: str) -> Result | None:
    """The Result that the subagent gave by result.py since its last Start or resume, as the Run
    records it, or None where it gave none; never what the subagent wrote in its reply."""
    start = _start_of(run, agent)
    if start is None:
        return None
    since = [r for r in run.results if r.agent == agent and r.start == start.number]
    return since[-1] if since else None


def starts_from_main(event: Event) -> bool:
    """Whether a start of a role, or a call of the plugin's skill, comes from the main conversation,
    the only one that starts the roles in a Run."""
    return not event.agent
