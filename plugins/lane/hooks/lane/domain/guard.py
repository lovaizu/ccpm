"""What the guard does on each hook event: which line it adds to the run record, which check it asks
of the lane types or the adapter, and what it answers, by Lane's rules that only the main
conversation starts the roles, that a Run moves only on a Result from result.py, that what no hook
shows comes only from Lane's scripts, and that the guard checks only within a Run."""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from adapters import AdapterFailed, NoWork, Running, kept_results, start_text, step_items
from answers import (
    cant_check,
    due,
    ended_unheld,
    gave,
    item_refused,
    no_steps,
    picked_up,
    stopped,
    text_failed,
)
from events import Answer, Event
from form import Lane, LanesFile, Move, OutOfForm, read_lanes
from lanes import (
    check_call,
    check_end,
    check_mark,
    check_start,
    ends_by_result,
    keeps_steps,
    needs_items,
    read_kept,
)
from lanes.kind import Broken, CantCheck, Held, Kept, Marking, Verdict
from manifest import plugin_name
from marks import items_left, may_mark, since_step_began, step_due
from place import (
    AgentPosted,
    EndAsked,
    ItemAsked,
    ItemPosted,
    Notification,
    Placed,
    Prompt,
    ReadPosted,
    ResultPosted,
    SkillCall,
    StartCall,
    StepAsked,
    StepPosted,
    ToolCall,
    place,
)
from run_record import (
    Called,
    Ended,
    Gave,
    Line,
    Marked,
    Prompted,
    Read,
    Report,
    Started,
    TextFailed,
    TextGiven,
    Tied,
    add,
    lines,
    record_path,
)
from runs import Due, Left, OffRoutes, Result, Run, pick_up, stand

# What lets an event through and says nothing.
PASS = Answer(False, "")


def handle(event: Event, root: str) -> Answer:
    """The guard's answer to one hook event of the plugin.

    Takes: the event, and the plugin's folder, whose hooks/lanes.json holds the Lanes, the Routes,
    and the adapters.
    Gives, and adds to the run record, by what the event is:
    - a skill's call (S4, S6): adds the call of a new Run, or picks the Run up from the record,
      where it holds one of the skill going, or from the Kept results, and answers the first start
      due or where the run picks up;
    - a prompt typed (S4): adds it to each Run of the conversation, so that the moves of a
      Route after a typed command are due, and answers those moves;
    - a start or resume (S4, S5): checks it by `lanes.check_start` with the Lanes of the role that
      makes it, and adds the Start where it's due, lets a resume, or a subagent's start of no
      role, through with no Start added, and stops any other with the moves due, or a subagent's
      start of a role with the sentence of the Lane on its last Step;
    - the PostToolUse of a start (S4): adds the tie of the Start to its agent_id, and answers the
      moves due where a start stays due beside it, as the adapter gives a text other than that of
      each Start of its role that runs;
    - the PostToolUse of each call of the main conversation after an adapter of a start's text
      failed at the skill's call (S4): asks it again, and once it answers, adds that it did and
      answers the moves due, each start with its text; says nothing while it still fails;
    - the PostToolUse of result.py that gave 0 (S4, S5): adds the Result, for the subagent's
      Start where it has an agent_id;
    - a run of step.py (S4's Note, S5), by the Start whose subagent runs it, or by the main
      conversation for the skill of a Run: stops it with the Step due where `marks.may_mark`
      doesn't take Step n for that Start's Marks and Reads, or the Run's, with the last Step that
      `lanes.keeps_steps.last_step` gives, and where the role it names isn't the Start's role or
      the Run's skill, or has no Lane of keeps_steps, as no Step of it is due then; else asks the
      adapter of a step's items for the Step's Items, with the role, Step n, and the Start's run
      values, where `lanes.needs_items` gives True; checks the Mark by `lanes.check_mark` with the
      Lanes of the role and the Reads and Marks that `marks.since_step_began` gives; and stops it
      with why and who must fix it where the adapter fails, with the Lane's sentence and what the
      Step lacks where a Lane is broken, or lets it through;
    - a run of item.py (S4's Note, S5), by a Start or the main conversation as a run of step.py
      is: asks the adapter of a step's items for the Items of the Step that `marks.step_due`
      gives, with the role and the Start's run values; stops it with why and who must fix it where
      the adapter fails, and with the Items that `marks.items_left` gives where the ID isn't one
      of the Step's Items, where no Step is due, or where lanes.json names no adapter of a step's
      items, as the Step then keeps no checklist; else lets it through;
    - the PostToolUse of step.py or item.py that gave 0 (S4's Note, S5): adds the Mark, an Item's
      with the Step that `marks.step_due` gives as it's marked, for the subagent's Start where it
      has an agent_id, else for the skill's Run;
    - the PostToolUse of a Read of a path that `lanes.read_kept` gives (S4's Note, S5): adds the
      Read, with the lines it read, for the subagent's Start where it has an agent_id, else for the
      skill's Run;
    - any other call (S4, S5): checks it by each Lane of each Run that holds it, and lets it
      through or stops it with the Lane's sentence and what the role may do;
    - a subagent's end (S5): checks it by each Lane of the role, and stops it with a broken Lane's
      sentence, that of the Lane on its last Step where it gave no Result since its Start, and that
      of keeps_steps with the Step due where a Step is unmarked in the latest pass;
    - a subagent's end reaching the main conversation (S4): adds the end, and answers the Result and
      the moves of its Route, or, ended with no Result, its start due again;
    - the main conversation's end of its turn (S4): stops it with the moves due where a move is
      due with its text and no subagent of the Run runs, unless a move waits for the person, a Run
      whose adapter of a start's text fails having none; else checks it by each Lane of each Run's
      skill, a Run that its skill's Result ended in that turn among them;
    - each start due, wherever the guard names the moves due (S4): asks the adapter of a start's
      text for it, where lanes.json names one, and where it gives that no work waits for the
      start, leaves the start out of the moves due, with why in its place in the answer; a start
      of that role then stops with the moves due, and the main conversation's end stops for none
      of it; a start whose text is that of a Start of its role that runs isn't due;
    - an event outside every Run: lets it through and adds nothing.
    Changes: the run record, by the lines above, and whatever an adapter or a command of the
    plugin's changes.
    Refuses: nothing; where lanes.json, the run record, an adapter, or a Lane can't be read or
    run, or the Kept results leave the Routes, it stops the event with why and who must fix it,
    except an adapter of a start's text that fails at the skill's call, a new Run's or one picked
    up, whose start it gives with why while it lets the call run, adding that it failed, one that
    fails at the main conversation's end, which then holds no move due, and one that fails as a
    subagent's end reaches the main conversation, whose why and who it gives in place of the
    moves.
    Carries: each `CC->>G` arrow of S4 to S6, each `G-->>` answer, S5 `G->>A: asks for the Step's
    Items, with the role, Step n, and the Start's run values` and `G->>A: asks for the Items of the
    Step due, with the role and the Start's run values`, and S4 `G->>G: leaves that start out of
    the moves due, with why in its place` and `G->>G: gives that start with why, and lets the call
    run`, with the Notes after it and after the tie of a Start.
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
    if isinstance(what, EndAsked) and placed.start is None:
        return _turn_ended(plugin, placed, cwd)
    if isinstance(what, (ToolCall, EndAsked)):
        return _checked(plugin, placed, cwd)
    handlers: dict[type, Callable[[Plugin, Placed, str], Answer]] = {
        Notification: _notified,
        StartCall: _started,
        Prompt: _prompted,
        StepAsked: _step_asked,
        ItemAsked: _item_asked,
    }
    return handlers.get(type(what), _posted)(plugin, placed, cwd)


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
    """A skill's call, where the skill is the plugin's and a Route goes after its start: the moves
    due of the latest Run of the skill that the record holds going, as after /compact; else the Run
    picked up from the Kept results, where lanes.json names an adapter of the plugin's records; else
    the call of a new Run with the first moves due; stopped with why and who must fix it where the
    Kept results leave the Routes."""
    routes = plugin.lanes.proposal.routes
    first = [r for r in routes if r.skill == what.skill and r.after.kind == "first"]
    if what.plugin != plugin.name or not first:
        return PASS
    going = [r for r in placed.runs if r.skill == what.skill]
    if going:
        return Answer(False, due(plugin.name, _told(plugin, going[-1], cwd)))
    records = plugin.lanes.proposal.adapters.records
    picked: tuple[Result, ...] = ()
    if records:
        kept = kept_results(os.path.join(plugin.root, records), what.words, cwd)
        try:
            picked = pick_up(routes, what.skill, kept)
        except OffRoutes as e:
            who = f"The developer of {plugin.name} must fix its adapter of records"
            return _stop(plugin.name, CantCheck(str(e), who))
    if picked:
        return _picked_up(plugin, what, picked, cwd)
    return _begun(plugin, what, cwd)


def _picked_up(plugin: Plugin, what: SkillCall, picked: tuple[Result, ...], cwd: str) -> Answer:
    """The call of a new Run with the Results it picks up from the Kept results, and where it picks
    up with the moves due, as `_at_call` gives them; the Run holds the words typed now, as any call
    does."""
    run_id = uuid.uuid4().hex[:8]
    add(plugin.record, Called(run_id, what.skill, what.words))
    for result in picked:
        add(plugin.record, Gave(run_id, result.role, result.result, None))
    return _at_call(plugin, run_id, cwd, lambda told: picked_up(plugin.name, picked, told))


def _begun(plugin: Plugin, what: SkillCall, cwd: str) -> Answer:
    """The call of a new Run, with the first moves due, as `_at_call` gives them."""
    run_id = uuid.uuid4().hex[:8]
    add(plugin.record, Called(run_id, what.skill, what.words))
    return _at_call(plugin, run_id, cwd, lambda told: due(plugin.name, told))


def _at_call(
    plugin: Plugin, run_id: str, cwd: str, said: Callable[[tuple[Due | Left, ...]], str]
) -> Answer:
    """The call let run, with what `said` makes of the Run's moves due; where the adapter of a
    start's text fails, what it makes of none, and each start with why, adding that it failed, as
    the skill's own steps may make what the adapter reads."""
    run = _now(plugin, run_id)
    try:
        return Answer(False, said(_told(plugin, run, cwd)))
    except AdapterFailed as e:
        add(plugin.record, TextFailed(run_id))
        failed = text_failed(plugin.name, run.due, str(e))
        return Answer(False, "\n".join(x for x in (said(()), failed) if x))


def _now(plugin: Plugin, run_id: str) -> Run:
    """The Run as it stands now, from the run record as it is."""
    routes = plugin.lanes.proposal.routes
    conversation = stand(plugin.session_id, lines(plugin.record), routes, plugin.name)
    (run,) = [r for r in conversation.runs if r.id == run_id]
    return run


def _record(plugin: Plugin, placed: Placed, cwd: str) -> None:
    """Adds, for each Run that holds the event, the line that `_line` gives."""
    for run in placed.runs:
        line = _line(plugin, placed, run, cwd)
        if line is not None:
            add(plugin.record, line)


def _line(plugin: Plugin, placed: Placed, run: Run, cwd: str) -> Line | None:
    """The line of the Run that a prompt, a start's tie, a Result, a Mark, or a Read makes; none
    for a tie of another Run's Start, or another role's Result."""
    what = placed.what
    if isinstance(what, (StepPosted, ItemPosted, ReadPosted)):
        return _reported(plugin, placed, run, cwd)
    if isinstance(what, Prompt):
        return Prompted(run.id, what.text)
    if isinstance(what, AgentPosted):
        tied = any(s.tool_use_id == what.tool_use_id for s in run.starts)
        return Tied(run.id, what.tool_use_id, what.agent_id) if tied else None
    if isinstance(what, ResultPosted):
        ours = placed.start is not None or what.role == run.skill
        return Gave(run.id, what.role, what.result, placed.agent_id) if ours else None
    return None


def _reported(plugin: Plugin, placed: Placed, run: Run, cwd: str) -> Line | None:
    """The Mark or the Read that the PostToolUse of a run of step.py or item.py, or of a Read,
    adds: a Step's Mark of the role that ran it; an Item's, with the Step due as it's marked; a
    Read of a path that a Lane of reads_whole names; none for another role's or path's."""
    what = placed.what
    role = _role(placed, run)
    if isinstance(what, ReadPosted):
        path = read_kept(_lanes(plugin, placed, run), what.call, _held(plugin, placed, run, cwd))
        return Read(run.id, role, path, what.first, what.last, placed.agent_id) if path else None
    assert isinstance(what, (StepPosted, ItemPosted))
    if isinstance(what, StepPosted):
        return Marked(run.id, role, what.step, None, placed.agent_id) if what.role == role else None
    lane = _kept_steps(plugin, placed, run, what.role)
    step = step_due(_reports(placed, run), lane.step) if lane else None
    return Marked(run.id, role, step, what.item, placed.agent_id) if step else None


def _step_asked(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A run of step.py: stopped with the Step due where no Step of the role it names is due or
    Step n isn't; else checked by the Lanes on Step n, with the Step's Items where a Lane of
    keeps_items lies on it."""
    what = placed.what
    assert isinstance(what, StepAsked)
    run = _marking_run(placed, what.role)
    held = _held(plugin, placed, run, cwd)
    role = _role(placed, run)
    lane = _kept_steps(plugin, placed, run, what.role)
    if lane is None:
        return Answer(True, no_steps(plugin.name, what.role, role))
    reports = _reports(placed, run)
    if not may_mark(reports, what.step, lane.step):
        return _stop(plugin.name, keeps_steps.broken(lane, held, step_due(reports, lane.step)))
    lanes = _lanes(plugin, placed, run)
    items = _items(plugin, role, what.step, held) if needs_items(lanes, what.step) else None
    verdict = check_mark(lanes, Marking(what.step, since_step_began(reports), items), held)
    return PASS if verdict == Kept() else _stop(plugin.name, verdict)


def _item_asked(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A run of item.py: let through where the ID is one of the Items of the Step due; else
    stopped with the Items left."""
    what = placed.what
    assert isinstance(what, ItemAsked)
    run = _marking_run(placed, what.role)
    held = _held(plugin, placed, run, cwd)
    role = _role(placed, run)
    lane = _kept_steps(plugin, placed, run, what.role)
    reports = _reports(placed, run)
    step = step_due(reports, lane.step) if lane else None
    items = _items(plugin, role, step, held) if step else ()
    if what.item in items:
        return PASS
    return Answer(True, item_refused(plugin.name, what.item, step, items_left(reports, items)))


def _marking_run(placed: Placed, named: str) -> Run:
    """The Run that a run of step.py or item.py lies on: the subagent's; for the main conversation,
    the Run of the skill it names, or else the first, whose skill then isn't the role named."""
    return next((r for r in placed.runs if placed.start or r.skill == named), placed.runs[0])


def _kept_steps(plugin: Plugin, placed: Placed, run: Run, named: str) -> Lane | None:
    """The Lane of keeps_steps on the last Step of the role that runs Lane's script, where the
    script names that role; None where it names another, or the role keeps no Steps."""
    role = _role(placed, run)
    last = keeps_steps.last_step(plugin.lanes.proposal.lanes, role) if named == role else None
    kept = [x for x in _lanes(plugin, placed, run) if x.type == "keeps_steps" and x.step == last]
    return kept[0] if kept else None


def _role(placed: Placed, run: Run) -> str:
    """The role that makes the event: its Start's, or the Run's skill for the main conversation."""
    return placed.start.role if placed.start else run.skill


def _reports(placed: Placed, run: Run) -> tuple[Report, ...]:
    """The Marks and Reads of the role that makes the event: its Start's, or the skill's Run's."""
    return placed.start.reports if placed.start else run.reports


def _items(plugin: Plugin, role: str, step: int, held: Held) -> tuple[str, ...]:
    """The Items of the role's Step that the adapter of a step's items gives, with the Start's run
    values, run in the hook event's cwd; none where lanes.json names no such adapter, as the Step
    then keeps no checklist. Raises AdapterFailed where the adapter fails."""
    adapter = plugin.lanes.proposal.adapters.items
    if adapter is None:
        return ()
    values = held.start.values if held.start else {}
    return step_items(os.path.join(plugin.root, adapter), role, step, values, held.cwd)


def _posted(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """The PostToolUse of a call: its line added; and, for the main conversation's, each start due
    with its text once the adapter that failed at the skill's call answers, and the moves due after
    a Start tied, where a start stays due beside it with another text."""
    _record(plugin, placed, cwd)
    if placed.start is not None:
        return PASS
    said = [_asked_again(plugin, run, cwd) for run in placed.runs if run.awaiting]
    what = placed.what
    if isinstance(what, AgentPosted):
        said += [_beside(plugin, run, cwd) for run in placed.runs if _tied(run, what)]
    return Answer(False, "\n".join(x for x in said if x))


def _asked_again(plugin: Plugin, run: Run, cwd: str) -> str:
    """The moves due, once the adapter that failed at the skill's call answers, with that it has
    answered added; nothing while it still fails."""
    try:
        told = _told(plugin, run, cwd)
    except AdapterFailed:
        return ""
    add(plugin.record, TextGiven(run.id))
    return due(plugin.name, told)


def _tied(run: Run, what: AgentPosted) -> bool:
    """Whether the Agent call whose PostToolUse it is made a Start of the Run."""
    return any(s.tool_use_id == what.tool_use_id for s in run.starts)


def _beside(plugin: Plugin, run: Run, cwd: str) -> str:
    """The moves due after a Start, where a start stays due beside it with another text; nothing
    where none does."""
    told = _told(plugin, run, cwd)
    starts = [d for d in told if isinstance(d, Due) and d.move.kind == "start"]
    return due(plugin.name, told) if starts else ""


def _prompted(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A prompt typed: added to each Run, with the moves due of each Run whose moves it changed,
    as a Route goes after the command typed."""
    _record(plugin, placed, cwd)
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
    if not placed.start.results and not placed.start.due:
        return Answer(False, due(plugin.name, told))
    if not placed.start.results:
        return Answer(False, ended_unheld(plugin.name, role, told))
    return Answer(False, gave(plugin.name, role, placed.start.results[-1], told))


def _started(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """A start: the Start added in the Run whose Lanes keep it, or stopped by the first Lane that
    breaks it; a resume let through, with a Start marked resumed where a Route makes it due; a
    resume that no move due opens, or a subagent's start of no role, let through with no Start
    added. A resume lies only on the Run that holds its subagent's Start, and on none where that
    Run has ended."""
    asked = placed.what
    assert isinstance(asked, StartCall)
    runs = placed.runs
    if asked.resume:
        runs = tuple(r for r in runs if any(s.agent_id == asked.agent_id for s in r.starts))
    verdicts: list[Verdict] = []
    for run in runs:
        moves = tuple(d for d in _told(plugin, run, cwd) if isinstance(d, Due))
        verdict = check_start(
            _lanes(plugin, placed, run), asked, _held(plugin, placed, run, cwd), moves
        )
        if verdict != Kept():
            verdicts.append(verdict)
            continue
        if placed.start is None:
            _add_start(plugin, run, asked, moves)
        return PASS
    return _stop(plugin.name, verdicts[0]) if verdicts else PASS


def _add_start(plugin: Plugin, run: Run, asked: StartCall, moves: tuple[Due, ...]) -> None:
    """Adds the main conversation's Start that the Routes keep: a start due, with the run values
    of its text; or a resume due, with the run values of the Start it resumes, tied at once to the
    subagent it resumes, as no later payload ties a SendMessage to it; or a resume that no move due
    opens, so that its subagent runs again, marked as made due by no Route. A start of a subagent
    not the plugin's adds nothing."""
    if not asked.resume:
        due = next((d for d in moves if (d.move.role, d.text) == (asked.role, asked.text)), None)
        if due is None:
            return
        started = Started(
            run.id, asked.role, asked.text, dict(due.values), asked.tool_use_id, False
        )
        add(plugin.record, started)
        return
    (before, *_) = [s for s in reversed(run.starts) if s.agent_id == asked.agent_id]
    opened = Move("resume", role=asked.role) in run.due
    values = dict(before.values)
    resumed = Started(run.id, asked.role, asked.text, values, asked.tool_use_id, True, opened)
    add(plugin.record, resumed)
    add(plugin.record, Tied(run.id, asked.tool_use_id, asked.agent_id))


def _turn_ended(plugin: Plugin, placed: Placed, cwd: str) -> Answer:
    """The main conversation's end of its turn: stopped with the moves due where a Run has a move
    due, none of them waiting for the person, and no subagent of the Run runs, a stop where only the
    move to start no more is due giving the sentence of the Lane on the skill's last Step, which
    names its result script; else checked by each Lane of each Run's skill. A Run whose adapter of
    a start's text fails has no move due with its text, so that the main conversation may ask the
    person what the adapter waits for, such as after it failed at the skill's call."""
    for run in placed.runs:
        try:
            told = _told(plugin, run, cwd)
        except AdapterFailed:
            continue
        moves = [d.move.kind for d in told if isinstance(d, Due)]
        running = any(not s.ended for s in run.starts)
        if moves and "wait" not in moves and not running:
            ends = [x for x in _lanes(plugin, placed, run) if x.type == "ends_by_result"]
            if set(moves) == {"no_more"} and ends:
                said = ends_by_result.TYPE.sentence(ends[0], plugin.lanes.proposal.routes)
                broken = Broken(ends[0], said.replace("${CLAUDE_PLUGIN_ROOT}", plugin.root), "")
                return Answer(True, stopped(plugin.name, broken))
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
    role = _role(placed, run)
    return tuple(lane for lane in plugin.lanes.proposal.lanes if lane.role == role)


def _held(plugin: Plugin, placed: Placed, run: Run, cwd: str) -> Held:
    return Held(run, placed.start, plugin.root, plugin.lanes.proposal.routes, cwd)


def _told(plugin: Plugin, run: Run, cwd: str) -> tuple[Due | Left, ...]:
    """The Run's moves due, each start with its text and run values, and each start that the
    adapter gives no work waits for left out, with why in its place; a start whose text is that of
    a Start of its role that runs isn't due, so that a start stays due beside those that run only
    with another text; raises AdapterFailed where the adapter fails."""
    running = tuple(Running(s.role, s.text, s.values) for s in run.starts if not s.ended)
    adapter = plugin.lanes.proposal.adapters.text
    program = os.path.join(plugin.root, adapter) if adapter else None
    found: list[Due | Left] = []
    for move in run.due:
        if move.kind != "start" or not move.role:
            found.append(Due(move, "", {}))
            continue
        text = start_text(program, move.role, running, run.words, cwd)
        if isinstance(text, NoWork):
            found.append(Left(move, text.why))
        elif all((r.role, r.text) != (move.role, text.text) for r in running):
            found.append(Due(move, text.text, text.values))
    return tuple(found)
