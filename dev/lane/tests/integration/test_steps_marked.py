"""The integration cases of a role's Steps held by its Marks and Reads: lay.py, the laid guard, the
lane types reads_whole, reads_none, keeps_steps, and keeps_items, step.py, item.py, and the adapter
of a step's items, joined through the double of Claude Code, on each path of S6 that a run of
step.py or item.py, a Read, or an end with a Step unmarked takes, S5's Note on the skill's own
Marks and Reads, the Proposals that S1 shows or sends back, the Marks that S7 keeps, and the rule
that what no hook shows comes only from Lane's scripts."""

from __future__ import annotations

import os
import re
from typing import Any

import pytest
import walkthrough as w

CHANGELOG = "# Changelog\n\n## 0.1.0\n\n- Counts lines.\n- Reads standard input.\n"


def keeps_steps(b: w.Bench, role: str = "writer") -> str:
    """The sentence of the Lane of keeps_steps on the role's last Step, as a stop gives it."""
    return (
        f"As each step ends, run `python3 {b.changelog}/hooks/lane/step.py {role} <n>` as a command"
        " of its own, with the step's number."
    )


def keeps_items(b: w.Bench) -> str:
    """The sentence of the Lane of keeps_items on writer's step 3, as a stop gives it."""
    return (
        "As each item of this step's checklist is done, run"
        f" `python3 {b.changelog}/hooks/lane/item.py writer <id>` as a command of its own, with the"
        " item's ID."
    )


def names_step(said: str, sentence: str, step: int) -> bool:
    """Whether the stop opens with the plugin's name, holds the sentence, and names the Step due by
    its number beside it."""
    rest = said.replace(sentence, "")
    return (
        said.startswith("changelog: ")
        and sentence in said
        and bool(re.search(rf"\b{step}\b", rest))
    )


def writers_start(b: w.Bench, c: Any) -> Any:
    """writer's Start in write's Run, as result.py reads the run record."""
    (run,) = [r for r in w.where(b.changelog, b, c.session_id).runs if r.skill == "write"]
    return next(s for s in run.starts if s.role == "writer")


def through_step_2(b: w.Bench, writer: Any) -> None:
    """writer reads CHANGELOG.md whole and marks its steps 1 and 2, each let through."""
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    for step in (1, 2):
        ran = writer.bash(b.step("writer", step))
        assert not ran.blocked and ran.exit_code == 0, ran.said


def through_step_4(b: w.Bench, writer: Any) -> None:
    """writer marks each of its Steps in order, its file read whole and its Items marked."""
    through_step_2(b, writer)
    for item in ("dated", "linked"):
        assert not writer.bash(b.item("writer", item)).blocked
    for step in (3, 4):
        assert not writer.bash(b.step("writer", step)).blocked


@pytest.mark.supports("S1", "lane types", "Lane", "lay.py")
def test_a_proposal_of_the_lane_types_of_steps_shows_each_steps_sentence(tmp_path: Any) -> None:
    """Given: changelog whose writer reads CHANGELOG.md whole, never reads tally.py, keeps a
    checklist on its step 3, and does its Steps in order, with an adapter of a step's items.
    When: up hands lay.py print the Proposal with writer's Lanes of reads_whole, reads_none,
    keeps_items, and keeps_steps, and the adapter of a step's items.
    Then: lay.py print exits 0, and shows each of writer's Steps with its type's sentence, the
    commands by `${CLAUDE_PLUGIN_ROOT}` as laid."""
    b = w.marked_bench(str(tmp_path))
    printed, _ = w.propose(b, w.converse(b), make=w.marked_proposal)
    for said in (
        (
            "1. Read `CHANGELOG.md` whole, to learn its last version and its form."
            " Read `CHANGELOG.md` whole."
        ),
        "Never read `tally.py`.",
        (
            "As each item of this step's checklist is done, run"
            " `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/item.py writer <id>` as a command of its"
            " own, with the item's ID."
        ),
        (
            "As each step ends, run `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/step.py writer <n>`"
            " as a command of its own, with the step's number."
        ),
    ):
        assert said in printed.output


@pytest.mark.supports("S1", "lay.py", "Lane")
@pytest.mark.parametrize(
    "kind, named",
    [("reads_whole", "keeps_steps"), ("keeps_items", "keeps_steps"), ("keeps_items", "items")],
    ids=[
        "reads_whole with no keeps_steps",
        "keeps_items with no keeps_steps",
        "keeps_items with no adapter of a step's items",
    ],
)
def test_a_lane_that_only_keeps_steps_bounds_goes_back_to_up(
    tmp_path: Any, kind: str, named: str
) -> None:
    """Given: changelog whose writer keeps its Steps, with an adapter of a step's items, or with
    none for keeps_items with no adapter of a step's items, as an adapter in hooks/adapters/ that
    the Proposal doesn't name is the user's to fix.
    When: up hands lay.py print the Proposal with writer's Lane of reads_whole or keeps_items and
    no Lane of keeps_steps, or keeps_items with no adapter of a step's items.
    Then: lay.py print exits 1, naming writer and what it lacks, and shows no ID, as only the
    Marks bound a Step."""
    b = w.marked_bench(str(tmp_path))
    proposal = w.marked_proposal()
    if named == "keeps_steps":
        proposal["lanes"] = [x for x in proposal["lanes"] if x["type"] != "keeps_steps"]
    else:
        proposal["adapters"] = {}
        os.remove(os.path.join(b.changelog, w.ITEMS))
    c = w.converse(b)
    assert not c.type("/lane:up changelog").blocked
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 1
    assert "writer" in printed.output and kind in printed.output and named in printed.output
    assert "ID:" not in printed.output


@pytest.mark.supports("S2", "adapter", "Laid", "lay.py")
def test_lay_writes_the_adapter_of_a_steps_items_into_lanes_json(tmp_path: Any) -> None:
    """Given: changelog whose writer keeps its Steps, with an adapter of a step's items.
    When: the person approves the Proposal with writer's Lanes of its Steps, and lay.py write lays
    it.
    Then: changelog's lanes.json names the adapter of a step's items and holds writer's four Lanes,
    and agents/writer.md holds each sentence."""
    from form import read_lanes

    b = w.marked_bench(str(tmp_path))
    w.lay(b, w.marked_proposal)
    proposal = read_lanes(os.path.join(b.changelog, "hooks", "lanes.json")).proposal
    assert proposal.adapters.items == w.ITEMS
    kinds = {x.type for x in proposal.lanes if x.role == "writer"}
    assert {"reads_whole", "reads_none", "keeps_items", "keeps_steps"} <= kinds
    assert "Never read `tally.py`." in w.read(os.path.join(b.changelog, "agents", "writer.md"))


@pytest.mark.supports("S6", "step.py", "Mark", "guard")
def test_a_step_marked_out_of_order_is_stopped_with_the_step_due(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, and writer started, with no Step marked.
    When: writer runs step.py writer 2.
    Then: the guard stops it with the sentence of keeps_steps and Step 1 due, and adds no Mark."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    stopped = writer.bash(b.step("writer", 2))
    assert stopped.blocked and names_step(stopped.said, keeps_steps(b), 1)
    assert writers_start(b, c).reports == ()


@pytest.mark.supports("S6", "step.py", "Mark", "Start")
def test_a_step_marked_in_its_turn_is_added_for_the_subagents_start(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, and writer started, which read CHANGELOG.md whole.
    When: writer runs step.py writer 1, and its PostToolUse reaches the guard.
    Then: the guard lets it through, step.py exits 0 with no words, and writer's Start holds the
    Mark of Step 1 with writer's agent_id, after its Read."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    ran = writer.bash(b.step("writer", 1))
    assert (ran.blocked, ran.exit_code, ran.output) == (False, 0, "")
    *_, mark = writers_start(b, c).reports
    assert (mark.role, mark.step, mark.item, mark.agent_id) == ("writer", 1, None, writer.id)


@pytest.mark.supports("S6", "Call", "Mark", "lane types")
def test_a_step_marked_before_its_file_is_read_whole_goes_back_to_the_step(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, and writer started.
    When: writer runs step.py writer 1 before any Read, then reads CHANGELOG.md whole, then runs
    step.py writer 1 again.
    Then: the guard stops the first with reads_whole's sentence and the path not read whole, and
    lets the second through, as the Step's Read now covers each line."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    stopped = writer.bash(b.step("writer", 1))
    assert stopped.blocked and stopped.said.startswith("changelog: Read `CHANGELOG.md` whole.")
    assert "CHANGELOG.md" in stopped.said.replace("Read `CHANGELOG.md` whole.", "")
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    assert not writer.bash(b.step("writer", 1)).blocked


@pytest.mark.supports("S6", "Call", "guard")
def test_a_file_read_in_part_leaves_its_step_unmarked(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, and CHANGELOG.md of 7 lines, as Read counts
    them.
    When: writer reads lines 1 to 3 of CHANGELOG.md, runs step.py writer 1, reads lines 4 to 7,
    and runs step.py writer 1 again.
    Then: writer's Start holds each Read with its lines; the guard stops the first step.py with
    reads_whole's sentence, and lets the second through, as the two Reads cover each line."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    path = os.path.join(b.repo, "CHANGELOG.md")
    assert w.read(path) == CHANGELOG
    assert not writer.read(path, offset=1, limit=3).blocked
    stopped = writer.bash(b.step("writer", 1))
    assert stopped.blocked and "Read `CHANGELOG.md` whole." in stopped.said
    assert not writer.read(path, offset=4, limit=4).blocked
    assert not writer.bash(b.step("writer", 1)).blocked
    reads = [(r.path, r.first, r.last) for r in writers_start(b, c).reports if hasattr(r, "first")]
    assert reads == [("CHANGELOG.md", 1, 3), ("CHANGELOG.md", 4, 7)]


@pytest.mark.supports("S6", "Call", "guard")
def test_only_a_read_of_a_path_reads_whole_names_is_kept(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, and writer started.
    When: writer reads README.md, then CHANGELOG.md whole.
    Then: the guard lets both through, and writer's Start holds only the Read of CHANGELOG.md,
    lines 1 to 7, with writer's agent_id."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    w.write_files(b.repo, {"README.md": "# tally\n"})
    assert not writer.read(os.path.join(b.repo, "README.md")).blocked
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    (read,) = writers_start(b, c).reports
    assert (read.path, read.first, read.last, read.agent_id) == ("CHANGELOG.md", 1, 7, writer.id)


@pytest.mark.supports("S6", "lane types", "Call", "A stop gives the step back")
def test_a_call_that_reaches_a_path_never_to_read_is_stopped(tmp_path: Any, broken: None) -> None:
    """Given: the marked Proposal laid, and writer started.
    When: writer reads tally.py by Read.
    Then: the guard stops it with reads_none's sentence, as its step 2 says."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    read = writer.read(os.path.join(b.repo, "tally.py"))
    assert read.blocked and read.said.startswith("changelog: Never read `tally.py`.")


@pytest.mark.supports("S6", "item.py", "Item", "Mark", "adapter")
def test_an_item_of_the_step_due_is_marked(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, which marked its steps 1 and 2.
    When: writer runs item.py writer dated, and its PostToolUse reaches the guard.
    Then: the guard lets it through, item.py exits 0 with no words, and writer's Start holds the
    Mark of the Item `dated` of Step 3, the Step due, with writer's agent_id."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    through_step_2(b, writer)
    ran = writer.bash(b.item("writer", "dated"))
    assert (ran.blocked, ran.exit_code, ran.output) == (False, 0, "")
    *_, mark = writers_start(b, c).reports
    assert (mark.step, mark.item, mark.agent_id) == (3, "dated", writer.id)


@pytest.mark.supports("S6", "item.py", "Item")
def test_an_item_not_of_the_step_due_is_stopped_with_the_items_left(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, which marked its steps 1 and 2.
    When: writer runs item.py writer undated, which the adapter doesn't give for Step 3.
    Then: the guard stops it with the Items left, `dated` and `linked`, and adds no Mark."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    through_step_2(b, writer)
    before = writers_start(b, c).reports
    stopped = writer.bash(b.item("writer", "undated"))
    assert stopped.blocked and stopped.said.startswith("changelog: ")
    assert "dated" in stopped.said.replace("undated", "") and "linked" in stopped.said
    assert writers_start(b, c).reports == before


@pytest.mark.supports("S6", "Item", "adapter", "lane types")
def test_a_step_with_an_item_left_goes_back_to_the_step(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, which marked its steps 1 and 2 and the Item
    `dated`.
    When: writer runs step.py writer 3, then item.py writer linked, then step.py writer 3 again.
    Then: the guard stops the first with keeps_items' sentence and the Item left, `linked`, and
    lets the second and the third through."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    through_step_2(b, writer)
    assert not writer.bash(b.item("writer", "dated")).blocked
    stopped = writer.bash(b.step("writer", 3))
    assert stopped.blocked and keeps_items(b) in stopped.said
    assert "linked" in stopped.said.replace(keeps_items(b), "")
    assert not writer.bash(b.item("writer", "linked")).blocked
    assert not writer.bash(b.step("writer", 3)).blocked


@pytest.mark.supports("S6", "adapter", "Item")
def test_the_adapter_of_a_steps_items_is_handed_the_role_the_step_and_the_run_values(
    tmp_path: Any,
) -> None:
    """Given: the marked Proposal laid, writer started with no run values, which marked its steps
    1 and 2.
    When: writer runs item.py writer dated, item.py writer linked, and step.py writer 3.
    Then: the adapter was handed writer and Step 3 as its two arguments, and writer's run values,
    none, on standard input, at each run that asks it, and never for Step 1 or 2, on which no Lane
    of keeps_items lies."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    through_step_2(b, writer)
    assert w.handed(b) == []
    for item in ("dated", "linked"):
        assert not writer.bash(b.item("writer", item)).blocked
    assert not writer.bash(b.step("writer", 3)).blocked
    assert w.handed(b) == [{"args": ["writer", "3"], "values": {}}] * 3


@pytest.mark.supports("S6", "adapter", "guard")
def test_an_adapter_of_a_steps_items_that_fails_stops_the_mark_with_who_must_fix_it(
    tmp_path: Any,
) -> None:
    """Given: the marked Proposal laid with an adapter of a step's items that exits 1 with
    `CHECKLIST.md is not there`, and writer started, which marked its steps 1 and 2.
    When: writer runs item.py writer dated, then step.py writer 3.
    Then: the guard stops each with why and that changelog's developer must fix its adapter."""
    b = w.marked_bench(str(tmp_path), w.FAILING_ITEMS)
    _, writer = w.marked_writer(b)
    through_step_2(b, writer)
    for command in (b.item("writer", "dated"), b.step("writer", 3)):
        stopped = writer.bash(command)
        assert stopped.blocked and "CHECKLIST.md is not there" in stopped.said
        assert "The developer of changelog must fix its adapter" in stopped.said


@pytest.mark.supports("S6", "lane types", "Mark")
def test_a_step_with_no_lane_on_it_is_marked_on_its_turn_alone(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, which read CHANGELOG.md whole and marked
    its step 1.
    When: writer runs step.py writer 2, whose Step holds no Lane of reads_whole or keeps_items.
    Then: the guard lets it through, as only a Step's own Lanes hold its Mark."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    assert not writer.bash(b.step("writer", 1)).blocked
    ran = writer.bash(b.step("writer", 2))
    assert not ran.blocked and ran.exit_code == 0


@pytest.mark.supports("S6", "step.py", "item.py", "lane types")
def test_lanes_scripts_go_beside_a_lane_that_runs_only_some_commands(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, whose run_only Lane on writer's step 2 lets it run only
    `git log --oneline` and its result script, and writer started.
    When: writer marks each of its Steps and Items by step.py and item.py.
    Then: the guard stops none of them for run_only, as Lane's scripts go by every type, while it
    stops `git status`."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    through_step_4(b, writer)
    stopped = writer.bash("git status")
    assert stopped.blocked and "Run only `git log --oneline`." in stopped.said


@pytest.mark.supports("S6", "step.py", "Mark")
def test_a_run_of_step_py_that_fails_adds_no_mark(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, which read CHANGELOG.md whole, and
    changelog's hooks/lane/step.py taken away after the lay.
    When: writer runs step.py writer 1, which the guard lets through and which then fails.
    Then: writer's Start holds no Mark, as the guard adds one only at the PostToolUse of a run that
    gave 0."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    os.remove(os.path.join(b.changelog, "hooks", "lane", "step.py"))
    ran = writer.bash(b.step("writer", 1))
    assert not ran.blocked and ran.exit_code != 0
    assert all(not hasattr(r, "step") for r in writers_start(b, c).reports)


@pytest.mark.supports("S6", "lane types", "Mark")
def test_an_end_with_a_step_unmarked_is_stopped_with_the_step_due(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, which marked its steps 1 and 2 and gave
    `written`.
    When: writer ends, then marks its Items and steps 3 and 4 and ends again.
    Then: the guard stops the first end with keeps_steps' sentence and Step 3 due, and lets the
    second end reach the main conversation."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    through_step_2(b, writer)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    stopped, reached = writer.end("Gave written.")
    assert stopped.blocked and reached is None and names_step(stopped.said, keeps_steps(b), 3)
    for item in ("dated", "linked"):
        assert not writer.bash(b.item("writer", item)).blocked
    for step in (3, 4):
        assert not writer.bash(b.step("writer", step)).blocked
    ended, reached = writer.end("Gave written.")
    assert not ended.blocked and reached is not None


@pytest.mark.supports("S6", "Mark")
def test_a_mark_of_step_1_begins_a_new_pass(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, writer started, which marked each of its Steps and gave
    `written`.
    When: writer reads CHANGELOG.md whole again, runs step.py writer 1, and ends.
    Then: the guard lets step.py writer 1 through, and stops the end with Step 2 due, as the Mark
    of Step 1 began a new pass."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    through_step_4(b, writer)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    assert not writer.bash(b.step("writer", 1)).blocked
    stopped, _ = writer.end("Gave written.")
    assert stopped.blocked and names_step(stopped.said, keeps_steps(b), 2)


@pytest.mark.supports("S6", "Result", "lane types")
def test_an_end_with_no_result_is_stopped_before_its_steps_are_checked(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, and writer started, with no Step marked and no Result.
    When: writer ends.
    Then: the guard stops the end with the sentence of the Lane on writer's last Step, which names
    its result script, and not keeps_steps' sentence."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    stopped, _ = writer.end("Wrote the entries.")
    assert stopped.blocked and b.result("writer", "written") in stopped.said
    assert keeps_steps(b) not in stopped.said


@pytest.mark.supports("S6", "S5", "Mark", "Start")
def test_each_subagent_of_a_role_is_held_to_its_own_marks(tmp_path: Any) -> None:
    """Given: the Proposal laid with keeps_steps on writer's step 4 and an adapter of a start's
    text that gives writer a text for 0.2.0, then 0.3.0, and two Starts of writer running side by
    side.
    When: the first writer marks its steps 1 and 2, then the second runs step.py writer 2.
    Then: the guard stops the second's run with Step 1 due, as each Mark is checked by the call's
    agent_id, and the first's Start alone holds its Marks."""
    adapter = (
        "#!/usr/bin/env python3\nimport json, sys\n"
        'held = {s["values"].get("version") for s in json.load(sys.stdin)["running"]}\n'
        'waiting = [v for v in ("0.2.0", "0.3.0") if v not in held]\n'
        'print(json.dumps({"text": f"Write the entries for {waiting[0]}",'
        ' "values": {"version": waiting[0]}} if waiting else {"none": "each has its writer"}))\n'
    )
    b = w.bench(str(tmp_path), dict(w.FILES, **{"hooks/adapters/text.py": adapter}))
    w.executable(os.path.join(b.changelog, "hooks", "adapters", "text.py"))

    def make() -> dict[str, Any]:
        proposal = w.walkthrough_proposal()
        proposal["lanes"].append(w.lane("writer", "agents/writer.md", 4, "keeps_steps"))
        proposal["adapters"] = {"text": "hooks/adapters/text.py"}
        return proposal

    c = w.laid(b, make=make)
    assert not c.type("/changelog:write").blocked
    _, first = c.start("changelog:writer", "Write the entries for 0.2.0", "writer")
    _, second = c.start("changelog:writer", "Write the entries for 0.3.0", "writer")
    assert first and second
    for step in (1, 2):
        assert not first.bash(b.step("writer", step)).blocked
    stopped = second.bash(b.step("writer", 2))
    assert stopped.blocked and names_step(stopped.said, keeps_steps(b), 1)
    (run,) = w.where(b.changelog, b, c.session_id).runs
    assert [len(s.reports) for s in run.starts] == [2, 0]


@pytest.mark.supports("What no hook shows only from Lane's scripts", "S6", "Mark")
def test_a_reply_that_says_the_steps_are_done_marks_none(tmp_path: Any, broken: None) -> None:
    """Given: the marked Proposal laid, and writer started, which gave `written` and ran no
    step.py.
    When: writer ends with the reply `Steps 1 to 4 done.`
    Then: the guard stops the end with keeps_steps' sentence and Step 1 due, as a Mark comes only
    from step.py."""
    b = w.marked_bench(str(tmp_path))
    _, writer = w.marked_writer(b)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    stopped, reached = writer.end("Steps 1 to 4 done.")
    assert stopped.blocked and reached is None and names_step(stopped.said, keeps_steps(b), 1)


def with_skills_steps() -> dict[str, Any]:
    """The walkthrough's Proposal, with keeps_steps on write's step 1, its last."""
    proposal = w.walkthrough_proposal()
    proposal["lanes"].append(w.lane("write", "skills/write/SKILL.md", 1, "keeps_steps"))
    return proposal


@pytest.mark.supports("S5", "step.py", "Mark", "Run")
def test_the_skills_mark_lies_on_its_run_with_no_agent_id(tmp_path: Any) -> None:
    """Given: the Proposal laid with keeps_steps on write's step 1, and the person typed
    /changelog:write.
    When: the main conversation runs step.py write 1, and the run goes on until reviewer gives
    `good`, the main conversation runs result.py write good, and ends its turn.
    Then: the guard lets step.py through, write's Run holds the Mark of Step 1 with no agent_id,
    and the turn ends."""
    b = w.bench(str(tmp_path))
    c = w.laid(b, make=with_skills_steps)
    assert not c.type("/changelog:write").blocked
    ran = c.bash(b.step("write", 1))
    assert not ran.blocked and ran.exit_code == 0
    (run,) = w.where(b.changelog, b, c.session_id).runs
    (mark,) = run.reports
    assert (mark.role, mark.step, mark.agent_id) == ("write", 1, None)
    _, writer = w.start(c, "writer")
    assert writer
    w.give(b, writer, "written")
    _, reviewer = w.start(c, "reviewer")
    assert reviewer
    w.give(b, reviewer, "good")
    given = c.bash(b.result("write", "good"))
    assert given.exit_code == 0, given.output
    assert not c.stop("The entries are reviewed good.").blocked


@pytest.mark.supports("S5", "result.py", "lane types", "Mark")
def test_the_skills_result_with_its_step_unmarked_is_refused(tmp_path: Any) -> None:
    """Given: the Proposal laid with keeps_steps on write's step 1, and a run of /changelog:write in
    which reviewer gave `good`, with no step.py.
    When: the main conversation runs result.py write good.
    Then: result.py refuses it with keeps_steps' sentence for write and Step 1 due, and write's Run
    holds no Result and goes on."""
    b = w.bench(str(tmp_path))
    c = w.laid(b, make=with_skills_steps)
    w.give(b, w.to_reviewer(b, c), "good")
    refused = c.bash(b.result("write", "good"))
    assert refused.exit_code == 1
    assert keeps_steps(b, "write") in refused.output, "the Lane's sentence is named"
    assert re.search(r"\b1\b", refused.output.replace(keeps_steps(b, "write"), "")), "Step 1"
    (run,) = w.where(b.changelog, b, c.session_id).runs
    assert (run.results[-1].role, run.ended) == ("reviewer", False)


@pytest.mark.supports("S5", "lane types", "Mark")
def test_the_skills_turn_end_with_its_step_unmarked_goes_while_it_waits(tmp_path: Any) -> None:
    """Given: the Proposal laid with keeps_steps on write's step 1, and a run of /changelog:write in
    which writer runs in the background, with no step.py.
    When: the main conversation ends its turn to wait on writer.
    Then: the guard lets the turn end, as keeps_steps holds the skill's Steps at its Result."""
    b = w.bench(str(tmp_path))
    c = w.laid(b, make=with_skills_steps)
    assert not c.type("/changelog:write").blocked
    _, writer = w.start(c, "writer")
    assert writer
    assert not c.stop("writer runs; I'll wait for it.").blocked


@pytest.mark.supports("S7", "Mark", "Run")
def test_marks_go_on_after_compact(tmp_path: Any) -> None:
    """Given: the marked Proposal laid, and writer started, which marked its steps 1 and 2.
    When: the person types /compact, and writer runs step.py writer 4.
    Then: the guard stops it with Step 3 due, as the run record holds writer's Marks."""
    b = w.marked_bench(str(tmp_path))
    c, writer = w.marked_writer(b)
    through_step_2(b, writer)
    c.compact()
    stopped = writer.bash(b.step("writer", 4))
    assert stopped.blocked and names_step(stopped.said, keeps_steps(b), 3)
