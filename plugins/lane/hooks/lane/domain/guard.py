"""What the guard does on each hook event: which line it adds to the run record, which check it asks
of the lane types or the adapter, and what it answers, by Lane's rules that only the main
conversation starts the roles, that a Run moves only on a Result from result.py, and that the guard
checks only within a Run."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from adapters import AdapterFailed, NoWork, Running, start_text
from answers import cant_check, due, ended_unheld, gave, stopped, text_failed
from events import Answer, Event
from form import Lane, LanesFile, Move, OutOfForm, read_lanes
from lanes import check_call, check_end, check_start
from lanes.kind import Broken, CantCheck, Held, Kept, Verdict
from manifest import plugin_name
from place import (
    AgentPosted,
    EndAsked,
    Notification,
    Placed,
    PrintPosted,
    Prompt,
    ResultPosted,
    SkillCall,
    StartCall,
    ToolCall,
    place,
)
from run_record import (
    Called,
    Ended,
    Gave,
    Line,
    Prompted,
    Shown,
    Started,
    SteppedAside,
    Tied,
    add,
    lines,
    record_path,
)
from runs import Due, Left, Run, stand

# What lets an event through and says nothing.
PASS = Answer(False, "")


def handle(event: Event, root: str) -> Answer:
    """The guard's answer to one hook event of the plugin.

    Takes: the event, and the plugin's folder, whose hooks/lanes.json holds the Lanes, the Routes,
    and the adapters.
    Gives, and adds to the run record, by what the event is:
    - a skill's call (S1, S3, S5, S7): adds the call of a new Run, by a person or an AI, or picks
      the Run up from the record or the Kept results, and answers the first start due or where the
      run picks up; for another plugin's skill that a move names, adds it so that the Run stands
      aside;
    - a prompt typed (S2, S5): adds it to each Run of the conversation, so that the moves of a
      Route after a typed command are due, and answers those moves;
    - a start or resume (S5, S6): checks it by `lanes.check_start` with the Lanes of the role that
      makes it, and adds the Start where it's due, lets a resume, or a subagent's start of no
      role, through with no Start added, and stops any other with the moves due, or a subagent's
      start of a role with the sentence of the Lane on its last Step;
    - the PostToolUse of a start (S5): adds the tie of the Start to its agent_id;
    - the PostToolUse of result.py that gave 0 (S2, S5, S6): adds the Result, for the subagent's
      Start where it has an agent_id;
    - the PostToolUse of lay.py print (S1): adds what it showed, with the Proposal's ID;
    - any other call (S2, S5, S6): checks it by each Lane of each Run that holds it, and lets it
      through or stops it with the Lane's sentence and what the role may do;
    - a subagent's end (S6): checks it by each Lane of the role, and stops it with a broken Lane's
      sentence, that of the Lane on its last Step where it gave no Result since its Start;
    - a subagent's end reaching the main conversation (S5): adds the end, and answers the Result and
      the moves of its Route, or, ended with no Result, its start due again;
    - the main conversation's end of its turn (S2, S5): stops it with the moves due where a move is
      due and no subagent of the Run runs, unless a move waits for the person; else checks it by
      each Lane of each Run's skill, a Run that its skill's Result ended in that turn among them;
    - each start due, wherever the guard names the moves due (S5): asks the adapter of a start's
      text for it, where lanes.json names one, and where it gives that no work waits for the
      start, leaves the start out of the moves due, with why in its place in the answer; a start
      of that role then stops with the moves due, and the main conversation's end stops for none
      of it;
    - an event outside every Run: lets it through and adds nothing.
    Changes: the run record, by the lines above, and whatever an adapter or a command of the
    plugin's changes.
    Refuses: nothing; where lanes.json, the run record, an adapter, or a Lane can't be read or
    run, it stops the event with why and who must fix it, except an adapter that fails at the
    skill's call, whose start it gives with why while it lets the call run, and one that fails as a
    subagent's end reaches the main conversation, whose why and who it gives in place of the
    moves.
    Carries: each `CC->>G` arrow of S1 to S7, each `G-->>` answer, and S5 `G->>G: leaves that
    start out of the moves due, with why in its place`.
    """
    name = plugin_name(root)
    try:
        lanes = read_lanes(os.path.join(root, "hooks", "lanes.json"))
    except (OutOfForm, FileNotFoundError) as e:
        who = f"The developer of {name} must lay it again by `/lane:up {name}`"
        return _cant(event, name, CantCheck(f"hooks/lanes.json can't be read: {e}", who))
    plugin = Plugin(name, root, lanes, event.session_id, record_path(name, event.session_id))
    conversation = stand(event.session_id, lines(plugin.record), lanes.proposal.routes, name)
    placed = place(event, conversation, lanes, root)
    try:
        if isinstance(placed.what, SkillCall):
            return _called(plugin, placed, placed.what, event.cwd)
        return _answered(plugin, placed, event.cwd) if placed.runs else PASS
    except AdapterFailed as e:
        cant = CantCheck(str(e), f"The developer of {name} must fix its adapter")
        return _cant(event, name, cant)


def _cant(event: Event, name: str, cant: CantCheck) -> Answer:
    """The event stopped with why the guard can't check it and who must fix it; a prompt, which
    also brings a subagent's end to the main conversation, let through with them, as one stopped
    would be lost to it."""
    return Answer(event.name != "UserPromptSubmit", _stop(name, cant).words)


def _answered(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """The answer to an event within a Run, by what the event is."""
    what = placed.what
    if isinstance(what, Notification):
        return _notified(plugin, placed, cwd)
    if isinstance(what, StartCall):
        return _started(plugin, placed, what, cwd)
    if isinstance(what, EndAsked) and placed.start is None:
        return _turn_ended(plugin, placed, cwd)
    if isinstance(what, (ToolCall, EndAsked)):
        return _checked(plugin, placed, cwd)
    if isinstance(what, Prompt):
        return _prompted(plugin, placed, cwd)
    _record(plugin, placed)
    return PASS


@dataclass(frozen=True)
class Plugin:
    """The plugin whose guard answers: its name, its folder, its lanes.json, the conversation's
    session_id, and the conversation's run record."""

    name: str
    root: str
    lanes: LanesFile
    session_id: str
    record: str


def _called(plugin: Plugin, placed: Placed, what: SkillCall, cwd: str) -> Answer:
    """A skill's call: the call of a new Run, where the skill is the plugin's and a Route goes after
    its start, with the first moves due; or each Run set aside whose move due calls the skill of
    another plugin."""
    routes = plugin.lanes.proposal.routes
    first = [r for r in routes if r.skill == what.skill and r.after.kind == "first"]
    if what.plugin != plugin.name:
        skill = f"{what.plugin}:{what.skill}"
        for run in [r for r in placed.runs if Move("call", skill=skill) in r.due]:
            add(plugin.record, SteppedAside(run.id, skill))
        return PASS
    if not first:
        return PASS
    run_id = uuid.uuid4().hex[:8]
    add(plugin.record, Called(run_id, what.skill, what.by, what.words))
    run = _now(plugin, run_id)
    try:
        return Answer(False, due(plugin.name, _told(plugin, run, cwd)))
    except AdapterFailed as e:
        return Answer(False, text_failed(plugin.name, run.due, str(e)))


def _now(plugin: Plugin, run_id: str) -> Run:
    """The Run as it stands now, from the run record as it is."""
    routes = plugin.lanes.proposal.routes
    conversation = stand(plugin.session_id, lines(plugin.record), routes, plugin.name)
    (run,) = [r for r in conversation.runs if r.id == run_id]
    return run


def _record(plugin: Plugin, placed: Placed) -> None:
    """Adds the line that a prompt, a start's tie, a Result, or a Proposal shown makes."""
    what = placed.what
    for run in placed.runs:
        line: Line | None = None
        if isinstance(what, Prompt):
            line = Prompted(run.id, what.text)
        elif isinstance(what, AgentPosted):
            if any(s.tool_use_id == what.tool_use_id for s in run.starts):
                line = Tied(run.id, what.tool_use_id, what.agent_id)
        elif isinstance(what, ResultPosted):
            if placed.start is not None or what.role == run.skill:
                line = Gave(run.id, what.role, what.result, placed.agent_id)
        elif isinstance(what, PrintPosted):
            line = Shown(run.id, what.proposal_id, what.words)
        if line is not None:
            add(plugin.record, line)


def _prompted(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A prompt typed: added to each Run, with the moves due of each Run whose moves it changed,
    as a Route goes after the command typed."""
    _record(plugin, placed)
    said = []
    for run in placed.runs:
        now = _now(plugin, run.id)
        if now.due != run.due:
            said.append(due(plugin.name, _told(plugin, now, cwd)))
    return Answer(False, "\n".join(said))


def _notified(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A subagent's end as it reaches the main conversation: the end added, and the Result it gave
    with the moves of its Route, or, ended with no Result, its start due again."""
    what = placed.what
    assert isinstance(what, Notification) and placed.start is not None
    (run,) = placed.runs
    add(plugin.record, Ended(run.id, what.agent_id, what.killed))
    told = _told(plugin, _now(plugin, run.id), cwd)
    role = placed.start.role
    if not placed.start.results:
        return Answer(False, ended_unheld(plugin.name, role, told))
    return Answer(False, gave(plugin.name, role, placed.start.results[-1], told))


def _started(plugin: Plugin, placed: Placed, asked: StartCall, cwd: str) -> Answer:
    """A start: the Start added in the Run whose Lanes keep it, or stopped by the first Lane that
    breaks it; a resume, or a subagent's start of no role, let through with no Start added."""
    verdicts: list[Verdict] = []
    for run in placed.runs:
        moves = tuple(d for d in _told(plugin, run, cwd) if isinstance(d, Due))
        verdict = check_start(
            _lanes(plugin, placed, run), asked, _held(plugin, placed, run, cwd), moves
        )
        if verdict != Kept():
            verdicts.append(verdict)
            continue
        if placed.start is None and not asked.resume:
            text = next(d for d in moves if (d.move.role, d.text) == (asked.role, asked.text))
            started = Started(
                run.id, asked.role, asked.text, dict(text.values), asked.tool_use_id, False
            )
            add(plugin.record, started)
        return PASS
    return _stop(plugin.name, verdicts[0])


def _turn_ended(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """The main conversation's end of its turn: stopped with the moves due where a Run has a move
    due, none of them waiting for the person, and no subagent of the Run runs; else checked by each
    Lane of each Run's skill."""
    for run in placed.runs:
        told = _told(plugin, run, cwd)
        moves = [d.move.kind for d in told if isinstance(d, Due)]
        running = any(not s.ended for s in run.starts)
        if moves and "wait" not in moves and not running:
            return Answer(True, due(plugin.name, told))
    return _checked(plugin, placed, cwd)


def _checked(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A Call or an end, checked by each Lane of the role in each Run that holds it."""
    for run in placed.runs:
        held = _held(plugin, placed, run, cwd)
        lanes = _lanes(plugin, placed, run)
        if isinstance(placed.what, ToolCall):
            verdict = check_call(lanes, placed.what.call, held)
        else:
            assert isinstance(placed.what, EndAsked)
            verdict = check_end(lanes, placed.what, held)
        if verdict != Kept():
            return _stop(plugin.name, verdict)
    return PASS


def _stop(name: str, verdict: Verdict) -> Answer:
    """The stop of what isn't kept: a broken Lane's sentence and what the role may do, or why the
    guard can't check and who must fix it."""
    if isinstance(verdict, CantCheck):
        return Answer(True, cant_check(name, verdict))
    assert isinstance(verdict, Broken)
    return Answer(True, stopped(name, verdict))


def _lanes(plugin: Plugin, placed: Placed, run: Run) -> tuple[Lane, ...]:
    """The Lanes of the role that makes the event: the Start's, or the Run's skill's."""
    role = placed.start.role if placed.start else run.skill
    return tuple(lane for lane in plugin.lanes.proposal.lanes if lane.role == role)


def _held(plugin: Plugin, placed: Placed, run: Run, cwd: str) -> Held:
    return Held(run, placed.start, plugin.root, plugin.lanes.proposal.routes, cwd)


def _told(plugin: Plugin, run: Run, cwd: str) -> tuple[Due | Left, ...]:
    """The Run's moves due, each start with its text and run values, and each start that the
    adapter gives no work waits for left out, with why in its place; raises AdapterFailed where
    the adapter fails."""
    running = tuple(Running(s.role, s.text, s.values) for s in run.starts if not s.ended)
    adapter = plugin.lanes.proposal.adapters.text
    program = os.path.join(plugin.root, adapter) if adapter else None
    found: list[Due | Left] = []
    for move in run.due:
        if move.kind == "start" and move.role:
            text = start_text(program, move.role, running, run.words, cwd)
            if isinstance(text, NoWork):
                found.append(Left(move, text.why))
            else:
                found.append(Due(move, text.text, text.values))
        else:
            found.append(Due(move, "", {}))
    return tuple(found)
