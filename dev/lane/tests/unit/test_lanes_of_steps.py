"""The unit cases of the lane types that hold a role's Steps, reads_whole, reads_none, keeps_steps,
and keeps_items, through each type's `faults`, `sentence`, `allows`, `check_start`, `check_mark`,
and `check_end`, reads_whole's `named` and keeps_steps' `last_step`, and of how lanes/ joins them,
through `needs_items`, `check_mark`, `read_kept`, `check_call`, and `check_end`: each type's values
and refusals, each class of Call it stops or doesn't judge, each Mark it keeps or breaks, the lines
a file holds at the edge of a Read, and each end held to a Step unmarked; and the Mark of every
other lane type, which none of them checks."""

from __future__ import annotations

import dataclasses
import os
from typing import Any

import lane_data as d
import pytest
from lanes import (
    check_call,
    check_end,
    check_mark,
    ends_by_result,
    ends_checked,
    keeps_items,
    keeps_steps,
    needs_items,
    read_kept,
    reads_none,
    reads_whole,
    routes,
    run_only,
    sentence,
    write_only,
)
from lanes.kind import Broken, CantCheck, Held, Kept, Marking
from place import EndAsked, StartCall

TYPES = {
    "reads_whole": reads_whole.TYPE,
    "reads_none": reads_none.TYPE,
    "keeps_steps": keeps_steps.TYPE,
    "keeps_items": keeps_items.TYPE,
}
OTHERS = {
    "routes": routes.TYPE,
    "ends_by_result": ends_by_result.TYPE,
    "run_only": run_only.TYPE,
    "write_only": write_only.TYPE,
    "ends_checked": ends_checked.TYPE,
}
TALLY = "/home/you/tally/tally.py"


def held(
    reports: tuple[Any, ...] = (),
    values: dict[str, str] | None = None,
    cwd: str = d.REPO,
    main: bool = False,
) -> Held:
    """writer's Start with its Marks and Reads and its run values, in write's Run, its calls made
    in the folder; or, where `main`, the main conversation with the Marks and Reads on the Run."""
    start = dataclasses.replace(d.start("writer"), values=values or {}, reports=reports)
    if main:
        run = d.run(due=(), reports=reports)
        return Held(run, None, d.ROOT, d.ROUTES_OF_WRITE, cwd)
    return Held(d.run(starts=(start,), due=()), start, d.ROOT, d.ROUTES_OF_WRITE, cwd)


def worktree(
    tmp_path: Any,
    changelog: str = "# Changelog\n\n## 0.1.0\n\n- Counts lines.\n- Reads standard input.\n",
) -> str:
    """A worktree whose top holds .git and CHANGELOG.md, with the text given; gives its top."""
    top = str(tmp_path)
    os.makedirs(os.path.join(top, ".git"))
    with open(os.path.join(top, "CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write(changelog)
    return top


def faults(lane: Any) -> tuple[str, ...]:
    return TYPES[lane.type].faults(lane, d.LAST[lane.role], d.ROUTES_OF_WRITE)


def start_call(role: str) -> StartCall:
    return StartCall(
        role=role, ours=True, text="Carry out your steps", resume=False, tool_use_id="t1"
    )


@pytest.mark.supports("test_a_proposal_of_the_lane_types_of_steps_shows_each_steps_sentence")
@pytest.mark.parametrize(
    "lane, said",
    [
        (lambda: d.READS_WHOLE, "Read `CHANGELOG.md` whole."),
        (
            lambda: dataclasses.replace(
                d.READS_WHOLE, args={"paths": ["CHANGELOG.md", "REVIEW.md"]}
            ),
            "Read `CHANGELOG.md` and `REVIEW.md` whole.",
        ),
        (lambda: d.READS_NONE, "Never read `tally.py`."),
        (
            lambda: dataclasses.replace(d.READS_NONE, args={"paths": ["tally.py", "REVIEW.md"]}),
            "Never read `tally.py` or `REVIEW.md`.",
        ),
        (
            lambda: d.KEEPS_ITEMS,
            (
                "As each item of this step's checklist is done, run"
                f" `{d.ITEM} writer <id>` as a command of its own, with the item's ID."
            ),
        ),
        (
            lambda: d.KEEPS_STEPS,
            (
                f"As each step ends, run `{d.STEP} writer <n>` as a command of its own, with the"
                " step's number."
            ),
        ),
    ],
    ids=[
        "reads_whole",
        "reads_whole of two paths",
        "reads_none",
        "reads_none of two paths",
        "keeps_items",
        "keeps_steps",
    ],
)
def test_a_lane_of_steps_reads_as_its_type_gives_it(lane: Any, said: str) -> None:
    """Given: one of writer's Lanes that hold its Steps.
    When: sentence gives the Lane's sentence.
    Then: it reads as its type's info gives it, two paths of reads_whole joined by `and`, of
    reads_none by `or`, and the scripts named by `${CLAUDE_PLUGIN_ROOT}` with writer's name."""
    given = lane()
    assert sentence(given, d.LAST[given.role], d.ROUTES_OF_WRITE) == said


@pytest.mark.supports("test_a_lane_that_only_keeps_steps_bounds_goes_back_to_up")
@pytest.mark.parametrize(
    "lane",
    [
        lambda: d.lane("writer", "agents/writer.md", 1, "reads_whole"),
        lambda: d.lane("writer", "agents/writer.md", 1, "reads_whole", paths=[]),
        lambda: d.lane("writer", "agents/writer.md", 1, "reads_whole", paths="CHANGELOG.md"),
        lambda: d.lane("writer", "agents/writer.md", 2, "reads_none"),
        lambda: d.lane("writer", "agents/writer.md", 2, "reads_none", paths=[]),
        lambda: d.lane("writer", "agents/writer.md", 2, "reads_none", paths=[1]),
        lambda: dataclasses.replace(d.KEEPS_STEPS, step=3),
        lambda: dataclasses.replace(d.KEEPS_STEPS, step=1),
    ],
    ids=[
        "reads_whole without paths",
        "reads_whole of no path",
        "reads_whole of a string",
        "reads_none without paths",
        "reads_none of no path",
        "reads_none of a number",
        "keeps_steps on the Step before the last",
        "keeps_steps on the first Step",
    ],
)
def test_a_lane_of_steps_that_cant_stand_has_a_fault(lane: Any) -> None:
    """Given: a Lane of reads_whole or reads_none without its paths, with none, or with a value of
    another type, or keeps_steps on a Step of writer other than its last, Step 4.
    When: its type finds its faults.
    Then: it finds one."""
    assert faults(lane())


@pytest.mark.supports("test_a_proposal_of_the_lane_types_of_steps_shows_each_steps_sentence")
@pytest.mark.parametrize(
    "lane",
    [lambda: d.READS_WHOLE, lambda: d.READS_NONE, lambda: d.KEEPS_ITEMS, lambda: d.KEEPS_STEPS],
    ids=["reads_whole", "reads_none", "keeps_items", "keeps_steps on the last Step"],
)
def test_a_lane_of_steps_with_its_values_on_a_step_it_suits_has_no_fault(lane: Any) -> None:
    """Given: one of writer's Lanes that hold its Steps, with its values, keeps_steps on writer's
    last Step.
    When: its type finds its faults.
    Then: it finds none."""
    assert faults(lane()) == ()


@pytest.mark.supports("test_a_call_that_reaches_a_path_never_to_read_is_stopped")
@pytest.mark.parametrize(
    "call, allowed",
    [
        (d.tool("Read", file_path=TALLY), False),
        (d.tool("Read", file_path=TALLY, offset=1, limit=1), False),
        (d.tool("Grep", path=TALLY, pattern="sum"), False),
        (d.tool("Grep", path=d.REPO, pattern="sum"), False),
        (d.tool("Glob", path=d.REPO, pattern="tally.py"), False),
        (d.tool("Glob", path=d.REPO, pattern="*.md"), None),
        (d.bash("cat tally.py"), False),
        (d.tool("Read", file_path="/home/you/tally/CHANGELOG.md"), None),
        (d.tool("Read", file_path="/home/you/tally/docs/tally.py"), None),
        (d.bash("git log --oneline"), None),
        (d.write(TALLY), None),
    ],
    ids=[
        "a Read of its path",
        "a Read of part of its path",
        "a Grep of its path",
        "a Grep of the folder that holds it",
        "a Glob that names its path",
        "a Glob of its folder by another pattern",
        "a Bash command that names it",
        "a Read of another path",
        "a Read of its name elsewhere",
        "a Bash command that names it not",
        "a Write of its path",
    ],
)
def test_reads_none_stops_each_read_that_reaches_its_path(call: Any, allowed: Any) -> None:
    """Given: writer's reads_none Lane for `tally.py`, in the worktree whose top is tally.
    When: the type judges a Call.
    Then: it stops a Read or a Grep of tally's tally.py, a Grep of tally, which reads its
    contents, a Glob that names it, and a Bash command that names it, and doesn't judge any other
    Call, a Glob by another pattern among them, so that a Lane of its type that names another path
    never outweighs it."""
    assert TYPES["reads_none"].allows(d.READS_NONE, call, held()) is allowed


@pytest.mark.supports("test_a_call_that_reaches_a_path_never_to_read_is_stopped")
@pytest.mark.parametrize(
    "values, path, allowed",
    [
        ({"deliverable": "plan"}, "/home/you/tally/plan.md", False),
        ({"deliverable": "plan"}, "/home/you/tally/spec.md", None),
    ],
    ids=["its value", "another value"],
)
def test_reads_none_fills_in_the_starts_run_values(
    values: dict[str, str], path: str, allowed: Any
) -> None:
    """Given: writer's reads_none Lane for `{deliverable}.md`, and writer's Start with the value
    deliverable `plan`.
    When: the type judges a Read.
    Then: it stops a Read of plan.md, and doesn't judge one of spec.md."""
    lane = dataclasses.replace(d.READS_NONE, args={"paths": ["{deliverable}.md"]})
    given = TYPES["reads_none"].allows(lane, d.tool("Read", file_path=path), held(values=values))
    assert given is allowed


@pytest.mark.supports("test_a_call_that_reaches_a_path_never_to_read_is_stopped")
@pytest.mark.parametrize(
    "lanes, kept",
    [
        (lambda: (d.READS_NONE,), False),
        (
            lambda: (
                d.READS_NONE,
                dataclasses.replace(d.READS_NONE, args={"paths": ["REVIEW.md"]}),
            ),
            False,
        ),
        (lambda: (d.READS_NONE, d.write_only()), False),
        (lambda: (dataclasses.replace(d.READS_NONE, args={"paths": ["REVIEW.md"]}),), True),
    ],
    ids=[
        "its Lane alone",
        "beside a Lane of its type that names another path",
        "beside a Lane of another type",
        "a Lane of another path alone",
    ],
)
def test_a_read_of_a_path_never_to_read_is_broken_by_its_lane(lanes: Any, kept: bool) -> None:
    """Given: writer's Lanes of reads_none, for tally.py or for REVIEW.md, alone or beside another.
    When: check_call checks a Read of tally.py.
    Then: it breaks it with the sentence of the Lane that names tally.py, which no Lane that names
    another path outweighs, and keeps it where no Lane names it."""
    verdict = check_call(lanes(), d.tool("Read", file_path=TALLY), held())
    if kept:
        assert verdict == Kept()
    else:
        assert isinstance(verdict, Broken) and verdict.sentence == "Never read `tally.py`."


@pytest.mark.supports("test_lanes_scripts_go_beside_a_lane_that_runs_only_some_commands")
@pytest.mark.parametrize(
    "name",
    ["reads_whole", "keeps_steps", "keeps_items"],
    ids=["reads_whole", "keeps_steps", "keeps_items"],
)
@pytest.mark.parametrize(
    "call",
    [d.bash("git status"), d.tool("Read", file_path="/home/you/tally/CHANGELOG.md")],
    ids=["a Bash command", "a Read of its path"],
)
def test_a_lane_that_holds_a_mark_or_an_end_judges_no_call(name: str, call: Any) -> None:
    """Given: writer's Lane of reads_whole, keeps_steps, or keeps_items.
    When: the type judges a Call.
    Then: it judges none, as it holds a Step's Mark or the role's end."""
    lane = {
        "reads_whole": d.READS_WHOLE,
        "keeps_steps": d.KEEPS_STEPS,
        "keeps_items": d.KEEPS_ITEMS,
    }
    assert TYPES[name].allows(lane[name], call, held()) is None


@pytest.mark.supports("test_each_subagent_of_a_role_is_held_to_its_own_marks")
@pytest.mark.parametrize("name", list(TYPES))
def test_a_lane_of_steps_keeps_every_start(name: str) -> None:
    """Given: a Lane of a type that holds a role's Steps.
    When: the type checks writer's start of reviewer.
    Then: it keeps it, as the Lane on writer's last Step checks a subagent's start."""
    lane = {"reads_whole": d.READS_WHOLE, "reads_none": d.READS_NONE}
    given = lane.get(name, d.KEEPS_ITEMS if name == "keeps_items" else d.KEEPS_STEPS)
    assert TYPES[name].check_start(given, start_call("reviewer"), held(), ()) == Kept()


@pytest.mark.supports("test_an_end_with_a_step_unmarked_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "lane",
    [lambda: d.READS_WHOLE, lambda: d.READS_NONE, lambda: d.KEEPS_ITEMS],
    ids=["reads_whole", "reads_none", "keeps_items"],
)
def test_a_lane_on_a_step_keeps_every_end(lane: Any) -> None:
    """Given: writer's Lane of reads_whole, reads_none, or keeps_items, and writer's Start with no
    Mark.
    When: the type checks writer's end.
    Then: it keeps it, as keeps_steps holds the end until each Step is marked."""
    given = lane()
    assert TYPES[given.type].check_end(given, EndAsked("Done."), held()) == Kept()


@pytest.mark.supports("test_a_step_with_no_lane_on_it_is_marked_on_its_turn_alone")
@pytest.mark.parametrize(
    "lane",
    [
        lambda: d.ROUTES,
        lambda: d.WRITER_END,
        lambda: d.run_only(),
        lambda: d.write_only(),
        lambda: d.lane("writer", "agents/writer.md", 4, "ends_checked", command="false"),
        lambda: d.READS_NONE,
        lambda: d.KEEPS_STEPS,
    ],
    ids=[
        "routes",
        "ends_by_result",
        "run_only",
        "write_only",
        "ends_checked",
        "reads_none",
        "keeps_steps",
    ],
)
def test_a_type_that_checks_no_mark_keeps_every_mark(lane: Any) -> None:
    """Given: a Lane of a type that checks no Mark, keeps_steps among them, as the guard takes a
    Mark only of the Step due before it asks the Lanes.
    When: the type checks a Mark of its Step with nothing since the Step began.
    Then: it keeps it."""
    given = lane()
    types = {**OTHERS, **TYPES}
    marking = Marking(given.step, (), None)
    assert types[given.type].check_mark(given, marking, held()) == Kept()


@pytest.mark.supports("test_a_file_read_in_part_leaves_its_step_unmarked")
@pytest.mark.parametrize(
    "since, verdict",
    [
        ((d.read(1, 7),), Kept),
        ((d.read(1, 3), d.read(4, 7)), Kept),
        ((d.read(4, 7), d.read(1, 3)), Kept),
        ((d.read(1, 6),), Broken),
        ((d.read(2, 7),), Broken),
        ((d.read(1, 3), d.read(5, 7)), Broken),
        ((d.read(1, 7, path="REVIEW.md"),), Broken),
        ((), Broken),
    ],
    ids=[
        "each line, the empty one after the last newline among them",
        "each line, in two Reads",
        "each line, in two Reads out of order",
        "each line but the last",
        "each line but the first",
        "a line between two Reads left",
        "another path read",
        "no Read",
    ],
)
def test_reads_whole_keeps_a_mark_only_once_each_line_is_read(
    tmp_path: Any, since: Any, verdict: type
) -> None:
    """Given: writer's reads_whole Lane for `CHANGELOG.md`, which holds 7 lines as Read counts
    them, the empty line after its last newline among them, in the worktree of writer's calls.
    When: the type checks the Mark of writer's step 1 with the Reads since the Step began.
    Then: it keeps the Mark where the Reads cover each line, and breaks it where they don't, with
    its sentence and the path not read whole."""
    top = worktree(tmp_path)
    given = TYPES["reads_whole"].check_mark(
        d.READS_WHOLE, Marking(1, since, None), held(cwd=os.path.join(top))
    )
    assert isinstance(given, verdict)
    if isinstance(given, Broken):
        assert given.sentence == "Read `CHANGELOG.md` whole." and "CHANGELOG.md" in given.may


@pytest.mark.supports("test_a_step_marked_before_its_file_is_read_whole_goes_back_to_the_step")
def test_reads_whole_reads_its_path_from_the_top_of_the_worktree_with_the_run_values(
    tmp_path: Any,
) -> None:
    """Given: writer's reads_whole Lane for `{deliverable}.md`, writer's Start with deliverable
    `CHANGELOG`, and its calls made in a folder below the top of the worktree.
    When: the type checks the Mark of writer's step 1 after a Read of each line of CHANGELOG.md, as
    the Lane names it with the value filled in.
    Then: it keeps the Mark."""
    top = worktree(tmp_path)
    below = os.path.join(top, "docs")
    os.makedirs(below)
    lane = dataclasses.replace(d.READS_WHOLE, args={"paths": ["{deliverable}.md"]})
    marking = Marking(1, (d.read(1, 7),), None)
    given = held(values={"deliverable": "CHANGELOG"}, cwd=below)
    assert TYPES["reads_whole"].check_mark(lane, marking, given) == Kept()


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_reads_whole_cant_check_a_path_that_isnt_there(tmp_path: Any) -> None:
    """Given: writer's reads_whole Lane for `NOTES.md`, which the worktree doesn't hold.
    When: the type checks the Mark of writer's step 1.
    Then: it can't check, naming NOTES.md, with the plugin's developer to fix it."""
    top = worktree(tmp_path)
    lane = dataclasses.replace(d.READS_WHOLE, args={"paths": ["NOTES.md"]})
    given = TYPES["reads_whole"].check_mark(lane, Marking(1, (), None), held(cwd=top))
    assert isinstance(given, CantCheck) and "NOTES.md" in given.why


@pytest.mark.supports("test_only_a_read_of_a_path_reads_whole_names_is_kept")
@pytest.mark.parametrize(
    "call, path",
    [
        (d.tool("Read", file_path="/home/you/tally/CHANGELOG.md"), "CHANGELOG.md"),
        (d.tool("Read", file_path="/home/you/tally/README.md"), None),
        (d.tool("Read", file_path="/home/you/tally/docs/CHANGELOG.md"), None),
        (d.tool("Grep", path="/home/you/tally/CHANGELOG.md", pattern="0.1.0"), None),
    ],
    ids=["a Read of its path", "a Read of another", "a Read of its name elsewhere", "a Grep"],
)
def test_reads_whole_names_the_path_a_read_reads(call: Any, path: str | None) -> None:
    """Given: writer's reads_whole Lane for `CHANGELOG.md`, in the worktree whose top is tally.
    When: named gives the path that a Call reads.
    Then: it gives `CHANGELOG.md` for a Read of tally's CHANGELOG.md, and None for any other."""
    assert reads_whole.named(d.READS_WHOLE, call, held()) == path


@pytest.mark.supports("test_only_a_read_of_a_path_reads_whole_names_is_kept")
@pytest.mark.parametrize(
    "lanes, call, path",
    [
        (
            lambda: (d.run_only(), d.READS_WHOLE),
            d.tool("Read", file_path="/home/you/tally/CHANGELOG.md"),
            "CHANGELOG.md",
        ),
        (lambda: (d.READS_WHOLE,), d.tool("Read", file_path="/home/you/tally/README.md"), None),
        (lambda: (d.READS_WHOLE,), d.bash("cat CHANGELOG.md"), None),
        (lambda: (d.run_only(),), d.tool("Read", file_path="/home/you/tally/CHANGELOG.md"), None),
    ],
    ids=["a Read its Lane names", "a Read of another path", "no Read", "no Lane of reads_whole"],
)
def test_a_read_is_kept_only_where_a_lane_of_reads_whole_names_its_path(
    lanes: Any, call: Any, path: str | None
) -> None:
    """Given: writer's Lanes, with or without its reads_whole Lane for `CHANGELOG.md`.
    When: read_kept gives the path of a Call's PostToolUse to keep.
    Then: it gives `CHANGELOG.md` for a Read of it where the Lane names it, and None otherwise."""
    assert read_kept(lanes(), call, held()) == path


@pytest.mark.supports("test_a_step_with_an_item_left_goes_back_to_the_step")
@pytest.mark.parametrize(
    "since, verdict",
    [
        ((d.marked(3, "dated"), d.marked(3, "linked")), Kept),
        ((d.marked(3, "dated"),), Broken),
        ((), Broken),
    ],
    ids=["each Item marked", "one Item left", "no Item marked"],
)
def test_keeps_items_keeps_a_mark_only_once_each_item_is_marked(since: Any, verdict: type) -> None:
    """Given: writer's keeps_items Lane on its step 3, whose Items the adapter gives as `dated` and
    `linked`.
    When: the type checks the Mark of step 3 with the Marks since the Step began.
    Then: it keeps the Mark where each Item is marked, and breaks it with its sentence and each
    Item left where one isn't."""
    marking = Marking(3, since, ("dated", "linked"))
    given = TYPES["keeps_items"].check_mark(d.KEEPS_ITEMS, marking, held())
    assert isinstance(given, verdict)
    if isinstance(given, Broken):
        assert given.sentence == (
            "As each item of this step's checklist is done, run"
            f" `python3 {d.ROOT}/hooks/lane/item.py writer <id>` as a command of its own, with the"
            " item's ID."
        )
        assert "linked" in given.may


@pytest.mark.supports("test_a_step_with_an_item_left_goes_back_to_the_step")
def test_keeps_items_keeps_a_mark_of_a_step_with_no_items_this_run() -> None:
    """Given: writer's keeps_items Lane on its step 3, whose Items the adapter gives as none this
    run.
    When: the type checks the Mark of step 3 with nothing since the Step began.
    Then: it keeps it."""
    marking = Marking(3, (), ())
    assert TYPES["keeps_items"].check_mark(d.KEEPS_ITEMS, marking, held()) == Kept()


@pytest.mark.supports("test_an_end_with_a_step_unmarked_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "given, due",
    [
        (lambda: held(), 1),
        (lambda: held((d.marked(1), d.marked(2))), 3),
        (lambda: held(tuple(d.marked(n) for n in range(1, 5))), None),
        (lambda: held((*(d.marked(n) for n in range(1, 5)), d.marked(1))), 2),
    ],
    ids=["no Step marked", "two Steps marked", "each Step marked", "a new pass begun"],
)
def test_keeps_steps_holds_the_end_until_each_step_is_marked(given: Any, due: int | None) -> None:
    """Given: writer's keeps_steps Lane on its step 4, its last, and writer's Start with its Marks.
    When: the type checks the end.
    Then: it keeps the end where the latest pass marked each Step, and breaks it with its sentence
    and the Step due where it didn't."""
    verdict = TYPES["keeps_steps"].check_end(d.KEEPS_STEPS, EndAsked("Done."), given())
    if due is None:
        assert verdict == Kept()
    else:
        assert isinstance(verdict, Broken) and verdict.sentence == (
            f"As each step ends, run `python3 {d.ROOT}/hooks/lane/step.py writer <n>` as a command"
            " of its own, with the step's number."
        )
        assert str(due) in verdict.may


@pytest.mark.supports("test_the_skills_turn_end_with_its_step_unmarked_goes_while_it_waits")
def test_keeps_steps_lets_the_main_conversations_turn_end() -> None:
    """Given: writer's keeps_steps Lane on its step 4, and the main conversation, no Step marked on
    the Run.
    When: the type checks the main conversation's end of its turn.
    Then: it keeps the end, as a Step may wait on a subagent."""
    verdict = TYPES["keeps_steps"].check_end(d.KEEPS_STEPS, EndAsked("Done."), held(main=True))
    assert verdict == Kept()


@pytest.mark.supports("test_an_end_held_to_the_plugins_command_goes_once_it_gives_0")
def test_keeps_steps_checks_an_end_before_the_plugins_command() -> None:
    """Given: writer's Lanes of ends_checked, whose command gives 1, and of keeps_steps, in that
    order, on its step 4, and writer's Start with no Step marked.
    When: check_end checks writer's end.
    Then: it breaks it with keeps_steps' sentence, so that the plugin's command runs only once each
    Step holds."""
    checked = d.lane("writer", "agents/writer.md", 4, "ends_checked", command="false")
    verdict = check_end((checked, d.KEEPS_STEPS), EndAsked("Done."), held())
    assert isinstance(verdict, Broken) and verdict.lane == d.KEEPS_STEPS


@pytest.mark.supports("test_lanes_scripts_go_beside_a_lane_that_runs_only_some_commands")
def test_a_stop_of_run_only_names_the_scripts_that_mark_steps_and_items() -> None:
    """Given: writer's Lanes of run_only for `git log --oneline`, keeps_items on its step 3, and
    keeps_steps on its step 4.
    When: check_call checks writer's `rm REVIEW.md`.
    Then: it breaks it with run_only's sentence, and the commands it may run name step.py and
    item.py beside `git log --oneline`."""
    items = d.lane("writer", "agents/writer.md", 3, "keeps_items")
    lanes = (d.run_only("git log --oneline"), items, d.KEEPS_STEPS)
    verdict = check_call(lanes, d.bash("rm REVIEW.md"), held())
    assert isinstance(verdict, Broken)
    assert f"python3 {d.ROOT}/hooks/lane/step.py writer <n>" in verdict.may
    assert f"python3 {d.ROOT}/hooks/lane/item.py writer <id>" in verdict.may


SKILLS_STEPS = d.lane("write", "skills/write/SKILL.md", 1, "keeps_steps")


def skills_marked(*steps: int) -> Any:
    """write's Run, with the main conversation's Marks of the Steps on it."""
    marks = tuple(dataclasses.replace(d.marked(n, agent=None), role="write") for n in steps)
    return d.run(due=(), reports=marks)


@pytest.mark.supports("test_the_skills_result_with_its_step_unmarked_is_refused")
@pytest.mark.parametrize(
    "lanes, run, due",
    [
        (lambda: (d.ROUTES, SKILLS_STEPS), lambda: skills_marked(), 1),
        (lambda: (d.ROUTES, SKILLS_STEPS), lambda: skills_marked(1), None),
        (lambda: (d.ROUTES, d.KEEPS_STEPS, SKILLS_STEPS), lambda: skills_marked(), 1),
        (lambda: (d.ROUTES, d.KEEPS_STEPS), lambda: skills_marked(), None),
    ],
    ids=[
        "its Step unmarked",
        "each Step marked",
        "a role's Lane of keeps_steps before it",
        "no Lane of keeps_steps on the skill",
    ],
)
def test_keeps_steps_holds_the_skills_result_until_each_step_is_marked(
    lanes: Any, run: Any, due: int | None
) -> None:
    """Given: the Lanes of lanes.json, with or without keeps_steps on write's step 1, its last, and
    write's Run with the main conversation's Marks.
    When: keeps_steps checks write's Result.
    Then: it keeps it where write has no Lane of keeps_steps or its latest pass marked each Step,
    and breaks it with write's sentence and the Step due where it didn't."""
    verdict = keeps_steps.at_result(lanes(), run(), d.ROOT, d.ROUTES_OF_WRITE)
    if due is None:
        assert verdict == Kept()
    else:
        assert verdict == Broken(
            SKILLS_STEPS,
            f"As each step ends, run `python3 {d.ROOT}/hooks/lane/step.py write <n>` as a command"
            " of its own, with the step's number.",
            f"Step {due} is due.",
        )


@pytest.mark.supports("test_a_step_marked_out_of_order_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "lanes, role, last",
    [
        (lambda: (d.run_only(), d.KEEPS_STEPS, d.WRITER_END), "writer", 4),
        (lambda: (d.run_only(), d.KEEPS_STEPS), "reviewer", None),
        (lambda: (d.run_only(), d.WRITER_END), "writer", None),
    ],
    ids=["a role with keeps_steps", "another role", "a role with none"],
)
def test_the_last_step_is_where_keeps_steps_lies(lanes: Any, role: str, last: int | None) -> None:
    """Given: the Lanes of lanes.json, with or without writer's keeps_steps Lane on its step 4.
    When: last_step gives the role's last Step.
    Then: it gives 4 for writer with the Lane, and None for a role without one."""
    assert keeps_steps.last_step(lanes(), role) == last


@pytest.mark.supports(
    "test_the_adapter_of_a_steps_items_is_handed_the_role_the_step_and_the_run_values"
)
@pytest.mark.parametrize(
    "lanes, step, needs",
    [
        (lambda: (d.KEEPS_ITEMS, d.KEEPS_STEPS), 3, True),
        (lambda: (d.KEEPS_ITEMS, d.KEEPS_STEPS), 2, False),
        (lambda: (d.READS_WHOLE, d.KEEPS_STEPS), 1, False),
    ],
    ids=["its Step", "another Step", "no Lane of keeps_items"],
)
def test_a_mark_needs_items_only_where_keeps_items_lies_on_its_step(
    lanes: Any, step: int, needs: bool
) -> None:
    """Given: writer's Lanes, with or without its keeps_items Lane on step 3.
    When: needs_items judges a Mark of the Step.
    Then: it gives True only for step 3 with the Lane."""
    assert needs_items(lanes(), step) is needs


@pytest.mark.supports("test_a_step_with_no_lane_on_it_is_marked_on_its_turn_alone")
@pytest.mark.parametrize(
    "marking, verdict",
    [
        (Marking(2, (), None), Kept),
        (Marking(1, (), None), Broken),
        (Marking(1, (d.read(1, 7),), None), Kept),
        (Marking(3, (d.marked(3, "dated"),), ("dated", "linked")), Broken),
        (Marking(3, (d.marked(3, "dated"), d.marked(3, "linked")), ("dated", "linked")), Kept),
    ],
    ids=[
        "a Step with no Lane on it",
        "Step 1, not read",
        "Step 1, read whole",
        "Step 3, an Item left",
        "Step 3, each Item marked",
    ],
)
def test_a_mark_is_checked_by_the_lanes_on_its_step_alone(
    tmp_path: Any, marking: Marking, verdict: type
) -> None:
    """Given: writer's Lanes of reads_whole on its step 1, keeps_items on its step 3, and
    keeps_steps on its step 4, in the worktree that holds CHANGELOG.md of 7 lines.
    When: check_mark checks a Mark of a Step.
    Then: it keeps a Mark of a Step that no Lane lies on, and of one whose Lanes keep it, and
    breaks one whose Lane finds what the Step lacks."""
    top = worktree(tmp_path)
    lanes = (d.READS_WHOLE, d.run_only(), d.KEEPS_ITEMS, d.KEEPS_STEPS, d.WRITER_END)
    assert isinstance(check_mark(lanes, marking, held(cwd=top)), verdict)


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_a_mark_whose_lane_cant_check_gives_why(tmp_path: Any) -> None:
    """Given: writer's reads_whole Lane on its step 1 for NOTES.md, which the worktree doesn't
    hold.
    When: check_mark checks the Mark of step 1.
    Then: it can't check, naming NOTES.md."""
    top = worktree(tmp_path)
    lane = dataclasses.replace(d.READS_WHOLE, args={"paths": ["NOTES.md"]})
    verdict = check_mark((lane, d.KEEPS_STEPS), Marking(1, (), None), held(cwd=top))
    assert isinstance(verdict, CantCheck) and "NOTES.md" in verdict.why
