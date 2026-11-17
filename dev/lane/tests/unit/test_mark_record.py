"""The unit cases of how a Mark and a Read reach the run record and come back: place.py's `place`
of a run of step.py or item.py and its PostToolUse, and of a Read's PostToolUse with the lines it
read; run_record.py's Marked and Read lines kept as added; and runs.py's `stand`, which puts each
Mark and Read on the Start whose agent_id it gives, or on the skill's Run."""

from __future__ import annotations

import dataclasses
import tempfile
from typing import Any

import lane_data as d
import pytest
from place import ItemAsked, ItemPosted, ReadPosted, StepAsked, StepPosted, ToolCall, place
from run_record import Called, Marked, Read, Started, Tied, add, lines, record_path
from runs import stand

WRITER = d.start("writer", agent_id="a01")
RUN = d.run(starts=(WRITER,), due=())
STEP = f"python3 {d.ROOT}/hooks/lane/step.py"
ITEM = f"python3 {d.ROOT}/hooks/lane/item.py"


def placed(name: str, *runs: Any, **fields: Any) -> Any:
    """The event placed in a conversation of the Runs, with the walkthrough's lanes.json."""
    return place(d.event(name, **fields), d.conversation(*runs), d.lanes_file(), d.ROOT)


def bash(command: str, **fields: Any) -> dict[str, Any]:
    """The fields of a Bash call of the command, a01's where `fields` names it."""
    return dict({"tool_name": "Bash", "tool_input": {"command": command}}, **fields)


@pytest.mark.supports("test_a_step_marked_out_of_order_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "command, what",
    [
        (f"{STEP} writer 2", StepAsked("writer", 2)),
        (f"{ITEM} writer dated", ItemAsked("writer", "dated")),
    ],
    ids=["step.py", "item.py"],
)
def test_a_subagents_run_of_lanes_scripts_is_a_mark_asked_on_its_start(
    command: str, what: Any
) -> None:
    """Given: write's Run with writer's Start tied to a01.
    When: place reads a01's PreToolUse of a run of step.py or item.py.
    Then: it is a StepAsked or an ItemAsked, with the role and the Step or Item, from writer's
    Start, on write's Run."""
    got = placed("PreToolUse", RUN, agent_id="a01", **bash(command))
    assert (got.what, got.runs, got.start) == (what, (RUN,), WRITER)


@pytest.mark.supports("test_a_step_marked_in_its_turn_is_added_for_the_subagents_start")
@pytest.mark.parametrize(
    "command, what",
    [
        (f"{STEP} writer 2", StepPosted("writer", 2)),
        (f"{ITEM} writer dated", ItemPosted("writer", "dated")),
    ],
    ids=["step.py", "item.py"],
)
def test_the_post_tool_use_of_lanes_scripts_is_a_mark_posted(command: str, what: Any) -> None:
    """Given: write's Run with writer's Start tied to a01.
    When: place reads the PostToolUse of a01's run of step.py or item.py.
    Then: it is a StepPosted or an ItemPosted, from writer's Start, with a01."""
    given = bash(command, agent_id="a01", tool_response={"stdout": "", "stderr": ""})
    got = placed("PostToolUse", RUN, **given)
    assert (got.what, got.start, got.agent_id) == (what, WRITER, "a01")


@pytest.mark.supports("test_the_skills_mark_lies_on_its_run_with_no_agent_id")
def test_the_main_conversations_run_of_step_py_lies_on_its_run() -> None:
    """Given: write's Run.
    When: place reads the main conversation's PreToolUse of step.py write 1.
    Then: it is a StepAsked of write's Step 1, from no Start, on write's Run."""
    got = placed("PreToolUse", RUN, **bash(f"{STEP} write 1"))
    assert (got.what, got.runs, got.start) == (StepAsked("write", 1), (RUN,), None)


@pytest.mark.supports("test_lanes_scripts_go_beside_a_lane_that_runs_only_some_commands")
def test_a_run_of_step_py_chained_with_another_command_is_a_call() -> None:
    """Given: write's Run with writer's Start tied to a01.
    When: place reads a01's PreToolUse of step.py writer 1 followed by `rm CHANGELOG.md`.
    Then: it is a ToolCall, which the Lanes check, as no single run of step.py."""
    got = placed("PreToolUse", RUN, agent_id="a01", **bash(f"{STEP} writer 1; rm CHANGELOG.md"))
    assert isinstance(got.what, ToolCall)


def read_response(first: int, count: int, total: int) -> dict[str, Any]:
    """A Read's `tool_response`, as Claude Code's states give it."""
    file = {"filePath": "/home/you/tally/CHANGELOG.md", "content": "", "numLines": count}
    return {"type": "text", "file": dict(file, startLine=first, totalLines=total)}


@pytest.mark.supports("test_a_file_read_in_part_leaves_its_step_unmarked")
@pytest.mark.parametrize(
    "response, lines_read",
    [
        (read_response(1, 2501, 2501), (1, 2501)),
        (read_response(10, 5, 2501), (10, 14)),
        (read_response(7, 1, 7), (7, 7)),
    ],
    ids=["whole", "with offset 10 and limit 5", "its last line alone"],
)
def test_the_post_tool_use_of_a_read_gives_the_lines_it_read(
    response: dict[str, Any], lines_read: tuple[int, int]
) -> None:
    """Given: write's Run with writer's Start tied to a01.
    When: place reads the PostToolUse of a01's Read of CHANGELOG.md.
    Then: it is a ReadPosted of the Call, from `startLine` to `startLine` plus `numLines` less
    one."""
    path = "/home/you/tally/CHANGELOG.md"
    got = placed(
        "PostToolUse",
        RUN,
        agent_id="a01",
        tool_name="Read",
        tool_input={"file_path": path},
        tool_response=response,
    )
    assert isinstance(got.what, ReadPosted) and got.what.call.input == {"file_path": path}
    assert (got.what.first, got.what.last, got.start) == (*lines_read, WRITER)


@pytest.mark.supports("test_marks_go_on_after_compact")
@pytest.mark.parametrize(
    "line",
    [
        Marked("r1", "writer", 2, None, "a01"),
        Marked("r1", "writer", 3, "dated", "a01"),
        Marked("r1", "write", 1, None, None),
        Read("r1", "writer", "CHANGELOG.md", 1, 7, "a01"),
        Read("r1", "write", "plan.md", 10, 14, None),
    ],
    ids=["a Step's Mark", "an Item's Mark", "the skill's Mark", "a Read", "the skill's Read"],
)
def test_a_mark_and_a_read_are_kept_as_added(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, line: Any
) -> None:
    """Given: an empty run record.
    When: add adds a Mark or a Read, and lines reads the record.
    Then: it gives the line as added."""
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setattr(tempfile, "tempdir", None)
    path = record_path("changelog", d.SESSION)
    add(path, line)
    assert lines(path) == (line,)


CALLED = Called("r1", "write", "")
STARTED = Started("r1", "writer", "Carry out your steps", {}, "toolu_w", False)
TIED = Tied("r1", "toolu_w", "a01")


@pytest.mark.supports("test_a_step_marked_in_its_turn_is_added_for_the_subagents_start")
def test_a_subagents_marks_and_reads_lie_on_its_start_in_the_order_added() -> None:
    """Given: the lines of write's Run with writer's Start tied to a01.
    When: stand reads a01's Read, its Mark of Step 1, and its Mark of the Item `dated`.
    Then: writer's Start holds each, in the order added, and the Run holds none."""
    reports = (
        Read("r1", "writer", "CHANGELOG.md", 1, 7, "a01"),
        Marked("r1", "writer", 1, None, "a01"),
        Marked("r1", "writer", 2, "dated", "a01"),
    )
    (run,) = stand(d.SESSION, (CALLED, STARTED, TIED, *reports), d.ROUTES_OF_WRITE).runs
    (start,) = run.starts
    assert (start.reports, run.reports) == (reports, ())


@pytest.mark.supports("test_each_subagent_of_a_role_is_held_to_its_own_marks")
def test_each_start_of_a_role_holds_only_its_own_marks() -> None:
    """Given: the lines of write's Run with two Starts of writer, tied to a01 and a02.
    When: stand reads a02's Mark of Step 1.
    Then: the Start tied to a02 holds it, and the one tied to a01 none."""
    second = dataclasses.replace(STARTED, tool_use_id="toolu_v", text="Write 0.3.0")
    mark = Marked("r1", "writer", 1, None, "a02")
    given = (CALLED, STARTED, TIED, second, Tied("r1", "toolu_v", "a02"), mark)
    (run,) = stand(d.SESSION, given, d.ROUTES_OF_WRITE).runs
    assert [s.reports for s in run.starts] == [(), (mark,)]


@pytest.mark.supports("test_the_skills_mark_lies_on_its_run_with_no_agent_id")
def test_the_skills_marks_and_reads_lie_on_its_run() -> None:
    """Given: the lines of write's Run with writer's Start tied to a01.
    When: stand reads the main conversation's Read of plan.md and its Mark of write's Step 1.
    Then: the Run holds each, in the order added, and writer's Start holds none."""
    reports = (Read("r1", "write", "plan.md", 1, 3, None), Marked("r1", "write", 1, None, None))
    (run,) = stand(d.SESSION, (CALLED, STARTED, TIED, *reports), d.ROUTES_OF_WRITE).runs
    assert (run.reports, run.starts[0].reports) == (reports, ())
