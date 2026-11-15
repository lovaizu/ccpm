"""What the guard does on each hook event: which line it adds to the run record, which check it asks
of the lane types or the adapter, and what it answers, by Lane's rules that only the main
conversation starts the roles, that a Run moves only on a Result from result.py, and that the guard
checks only within a Run."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from adapters import NoWork, Running, start_text
from answers import due, gave, stopped
from events import Answer, Event
from form import Lane, LanesFile, read_lanes
from lanes import check_call, check_end, check_start
from lanes.kind import Broken, Held, Kept, Verdict
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
      Route after a typed command are due;
    - a start or resume (S5, S6): checks it by `lanes.check_start` with the Lanes of the role that
      makes it, and adds the Start where it's due, lets a resume that the Routes open none for
      through, and stops any other with the moves due, or a subagent's start of a role with the
      sentence of the Lane on its last Step;
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
      due and no subagent of the Run runs, unless the move waits for the person; else checks it by
      each Lane of each Run's skill;
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
    skill's call, whose start it gives with why while it lets the call run.
    Carries: each `CC->>G` arrow of S1 to S7, each `G-->>` answer, and S5 `G->>G: leaves that
    start out of the moves due, with why in its place`.
    """
    lanes = read_lanes(os.path.join(root, "hooks", "lanes.json"))
    name = plugin_name(root)
    plugin = Plugin(name, root, lanes, event.session_id, record_path(name, event.session_id))
    conversation = stand(event.session_id, lines(plugin.record), lanes.proposal.routes)
    placed = place(event, conversation, lanes, root)
    if isinstance(placed.what, SkillCall):
        return _called(plugin, placed.what, event.cwd)
    return _answered(plugin, placed, event.cwd) if placed.runs else PASS


def _answered(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """The answer to an event within a Run, by what the event is."""
    what = placed.what
    if isinstance(what, Notification):
        return _notified(plugin, placed, cwd)
    if isinstance(what, StartCall):
        return _started(plugin, placed, what, cwd)
    if isinstance(what, (ToolCall, EndAsked)):
        return _checked(plugin, placed)
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


def _called(plugin: Plugin, what: SkillCall, cwd: str) -> Answer:
    """A skill's call: the call of a new Run, where the skill is the plugin's and a Route goes after
    its start, with the first moves due."""
    routes = plugin.lanes.proposal.routes
    first = [r for r in routes if r.skill == what.skill and r.after.kind == "first"]
    if what.plugin != plugin.name or not first:
        return PASS
    run_id = uuid.uuid4().hex[:8]
    add(plugin.record, Called(run_id, what.skill, what.by, what.words))
    conversation = stand(plugin.session_id, lines(plugin.record), routes)
    (run,) = [r for r in conversation.runs if r.id == run_id]
    return Answer(False, due(plugin.name, _told(plugin, run, cwd)))


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


def _notified(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A subagent's end as it reaches the main conversation: the end added, and the Result it gave
    with the moves of its Route."""
    what = placed.what
    assert isinstance(what, Notification) and placed.start is not None
    (run,) = placed.runs
    add(plugin.record, Ended(run.id, what.agent_id, what.killed))
    if not placed.start.results:
        return PASS
    result = placed.start.results[-1]
    return Answer(False, gave(plugin.name, placed.start.role, result, _told(plugin, run, cwd)))


def _started(plugin: Plugin, placed: Placed, asked: StartCall, cwd: str) -> Answer:
    """A start: the Start added in the Run whose Lanes keep it, or stopped by the first Lane that
    breaks it."""
    verdicts: list[Verdict] = []
    for run in placed.runs:
        moves = tuple(d for d in _told(plugin, run, cwd) if isinstance(d, Due))
        verdict = check_start(_lanes(plugin, placed, run), asked, _held(plugin, placed, run), moves)
        if verdict == Kept():
            text = next((d for d in moves if d.text == asked.text), None)
            values = dict(text.values) if text else {}
            started = Started(
                run.id, asked.role, asked.text, values, asked.tool_use_id, asked.resume
            )
            add(plugin.record, started)
            return PASS
        verdicts.append(verdict)
    return _stop(plugin, verdicts[0])


def _checked(plugin: Plugin, placed: Placed) -> Answer:
    """A Call or an end, checked by each Lane of the role in each Run that holds it."""
    for run in placed.runs:
        held = _held(plugin, placed, run)
        lanes = _lanes(plugin, placed, run)
        if isinstance(placed.what, ToolCall):
            verdict = check_call(lanes, placed.what.call, held)
        else:
            assert isinstance(placed.what, EndAsked)
            verdict = check_end(lanes, placed.what, held)
        if verdict != Kept():
            return _stop(plugin, verdict)
    return PASS


def _stop(plugin: Plugin, verdict: Verdict) -> Answer:
    assert isinstance(verdict, Broken)
    return Answer(True, stopped(plugin.name, verdict))


def _lanes(plugin: Plugin, placed: Placed, run: Run) -> tuple[Lane, ...]:
    """The Lanes of the role that makes the event: the Start's, or the Run's skill's."""
    role = placed.start.role if placed.start else run.skill
    return tuple(lane for lane in plugin.lanes.proposal.lanes if lane.role == role)


def _held(plugin: Plugin, placed: Placed, run: Run) -> Held:
    return Held(run, placed.start, plugin.root, plugin.lanes.proposal.routes)


def _told(plugin: Plugin, run: Run, cwd: str) -> tuple[Due | Left, ...]:
    """The Run's moves due, each start with its text and run values, and each start that the
    adapter gives no work waits for left out, with why in its place."""
    running = tuple(Running(s.role, s.text, s.values) for s in run.starts if not s.ended)
    adapter = plugin.lanes.proposal.adapters.text
    program = os.path.join(plugin.root, adapter) if adapter else None
    found: list[Due | Left] = []
    for move in run.due:
        if move.kind == "start" and move.role:
            text = start_text(program, move.role, running, run.words, cwd)
            if isinstance(text, NoWork):
                raise NotImplementedError("guard.handle, of none")
            found.append(Due(move, text.text, text.values))
        else:
            found.append(Due(move, "", {}))
    return tuple(found)
