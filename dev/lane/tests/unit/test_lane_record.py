"""The unit cases of hooks/lane/record.py: runs, one for each class of a conversation's record, and
add, one for each class of entries it adds, with the transitions of the record that Lane's list of
Claude Code's states brings about: a run added at the skill's call, its folder at the next event,
each later entry after the ones before, a start kept with its prompt and the steps given for it, and
two conversations apart; with none, one, and several runs, an entry placed on its own run though a
later run was added, and none, one, and several entries added at once; and read_state, for the
start that each subagent was last tied to, and what counts for a subagent and for the main
conversation: the steps each marked, a step gone back to that undoes the marks of the steps it
names before it, one, two in either order, and one of another start, and the main conversation's
moves with no turn, after its latest turn of one, two, or three, and at a turn's first move."""

from __future__ import annotations

import json
import os
import stat

import lane_entries
import pytest
from record import Done, Entry, Run, add, read_state, runs

RUN: Entry = {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"}
FOLDER: Entry = {"kind": "folder", "run": "r1", "plugin_root": "/plugins/log"}
START: Entry = lane_entries.start("toolu_1")
TIE: Entry = lane_entries.tie("toolu_1", "a1")


@pytest.mark.supports("test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first")
def test_a_conversation_with_no_record_has_no_run():
    """Given no record of the conversation
    When Lane reads its runs
    Then there's none"""
    assert runs("session-1") == []


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_run_added_at_the_skills_call_has_no_folder():
    """Given a conversation with no record
    When Lane adds a run of log:up with the words 1.2.0
    Then the record holds that run, with no folder and its one entry"""
    add("session-1", [RUN])
    assert runs("session-1") == [Run("r1", "session-1", "log:up", "1.2.0", None, [RUN])]


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_folder_added_after_the_run_gives_the_run_its_folder():
    """Given a run with no folder
    When Lane adds the run's folder
    Then the run has that folder"""
    add("session-1", [RUN])
    add("session-1", [FOLDER])
    assert runs("session-1") == [
        Run("r1", "session-1", "log:up", "1.2.0", "/plugins/log", [RUN, FOLDER])
    ]


@pytest.mark.supports("test_the_results_of_two_subagents_are_both_kept")
def test_entries_added_at_once_and_after_keep_their_order():
    """Given a run with its folder
    When Lane adds a start and its tie in one write, and then a result
    Then the run's entries are the run, its folder, the start, the tie, and the result, in order"""
    result: Entry = {"kind": "result", "run": "r1", "agent_id": "a1", "result": "written"}
    add("session-1", [RUN, FOLDER])
    add("session-1", [START, TIE])
    add("session-1", [result])
    assert runs("session-1")[0].entries == [RUN, FOLDER, START, TIE, result]


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_start_is_kept_with_its_prompt_and_the_steps_given_for_it():
    """Given a run with its folder
    When Lane adds a start with the prompt that the main conversation gave it and the steps that
    the plugin's adapter of the rules gave
    Then the run's last entry holds both as they were given"""
    given: Entry = {
        **START,
        "prompt": "Write docs/changes/1.2.0.md.",
        "steps": [{"name": "write", "rules": [{"type": "writes", "paths": ["docs/"]}]}],
    }
    add("session-1", [RUN, FOLDER])
    add("session-1", [given])
    assert runs("session-1")[0].entries[-1] == given


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_two_runs_of_one_conversation_each_hold_their_own_entries():
    """Given a run r1 of log:up for 1.2.0 with a start
    When Lane adds a run r2 of log:up for 1.3.0, and a start of it
    Then the conversation has both runs, in order, each with its own entries"""
    other: Entry = {"kind": "run", "run": "r2", "skill": "log:up", "words": "1.3.0"}
    writer: Entry = {"kind": "start", "run": "r2", "role": "log:writer", "tool_use_id": "toolu_2"}
    add("session-1", [RUN, FOLDER, START])
    add("session-1", [other, writer])
    first, second = runs("session-1")
    assert (first.words, second.words) == ("1.2.0", "1.3.0")
    assert first.entries == [RUN, FOLDER, START]
    assert second.entries == [other, writer]


@pytest.mark.supports("test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first")
def test_each_conversation_has_a_record_of_its_own():
    """Given a run of the conversation session-1
    When Lane reads the runs of session-2
    Then there's none"""
    add("session-1", [RUN])
    assert runs("session-2") == []


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_the_record_lies_in_the_systems_temporary_folder(temp: str):
    """Given the system's temporary folder of the case
    When Lane adds a run
    Then the record lies in that folder, and nowhere else"""
    add("session-1", [RUN])
    [made] = os.listdir(temp)
    with open(os.path.join(temp, made), encoding="utf-8") as f:
        assert [json.loads(line) for line in f] == [RUN]


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_a_record_that_cant_be_written_is_refused(temp: str):
    """Given a system's temporary folder that can't be written
    When Lane adds a run
    Then it refuses with OSError"""
    os.chmod(temp, stat.S_IRUSR | stat.S_IXUSR)
    try:
        with pytest.raises(OSError):
            add("session-1", [RUN])
    finally:
        os.chmod(temp, stat.S_IRWXU)


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_an_entry_added_after_a_later_run_lies_on_its_own_run():
    """Given a run r1 of log:up, and a run r2 of memo:up added after it
    When Lane adds r1's folder and a start of r1, then r2's folder
    Then r1 holds its folder and its start, and r2 its own folder alone"""
    memo: Entry = {"kind": "run", "run": "r2", "skill": "memo:up", "words": ""}
    memo_folder: Entry = {"kind": "folder", "run": "r2", "plugin_root": "/plugins/memo"}
    add("session-1", [RUN, memo])
    add("session-1", [FOLDER, START])
    add("session-1", [memo_folder])
    assert runs("session-1") == [
        Run("r1", "session-1", "log:up", "1.2.0", "/plugins/log", [RUN, FOLDER, START]),
        Run("r2", "session-1", "memo:up", "", "/plugins/memo", [memo, memo_folder]),
    ]


@pytest.mark.supports("test_the_results_of_two_subagents_are_both_kept")
def test_no_entry_added_leaves_the_record_as_it_stands():
    """Given a run with its folder
    When Lane adds no entry
    Then the run's entries are those before"""
    add("session-1", [RUN, FOLDER])
    add("session-1", [])
    assert runs("session-1")[0].entries == [RUN, FOLDER]


# read_state


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_the_start_a_subagent_was_last_tied_to_is_that_of_its_latest_tie():
    """Given the writer a1 started by toolu_1 and resumed by toolu_3, tied to each in turn, and a2
    started by toolu_2 between them
    When Lane reads the start that each subagent was last tied to
    Then a1's is the start of toolu_3, a2's that of toolu_2, and a9, which no start ties, has
    none"""
    second: Entry = lane_entries.start("toolu_2", prompt="Write the second.")
    resume: Entry = lane_entries.start("toolu_3")
    entries = [START, TIE, second, lane_entries.tie("toolu_2", "a2"), resume]
    tied = read_state([*entries, lane_entries.tie("toolu_3", "a1")]).latest_start
    assert ({agent: start.entry for agent, start in tied.items()}, "a9" in tied) == (
        {"a1": resume, "a2": second},
        False,
    )


mark = lane_entries.mark
# The end of the main conversation's turn that the guard let through.
TURN_ENDED: Entry = {"kind": "turn_ended", "run": "r1"}


def turn(prompt: str = "") -> Entry:
    """The `turn` entry of the main conversation's turn of log:up, begun by the prompt."""
    return {"kind": "turn", "run": "r1", "role": "log:up", "prompt": prompt, "steps": []}


def begun(prompt: str) -> Entry:
    """The `turn_begun` entry of the prompt that begins a turn after the run's first."""
    return {"kind": "turn_begun", "run": "r1", "prompt": prompt}


def back(step: str, undone: list[str], agent_id: str | None = "a1") -> Entry:
    """The step that the subagent, or the main conversation for None, went back to, with the steps
    it undid: the step and each after it."""
    role = "log:up" if agent_id is None else "log:writer"
    return {
        "kind": "back",
        "run": "r1",
        "agent_id": agent_id,
        "role": role,
        "step": step,
        "undone": undone,
    }


def steps_marked(entries: list[Entry]) -> tuple[set[str], set[str], set[str]]:
    """The steps that a1, a2, and the main conversation marked done, by the state of the entries."""
    state = read_state(entries)
    return state.done_by("a1").steps, state.done_by("a2").steps, state.done_by(None).steps


@pytest.mark.supports("test_a_read_of_the_main_conversation_counts_for_no_subagent")
def test_the_steps_a_start_marked_are_its_own_marks_of_steps():
    """Given a run holding a1's marks of `write` and of the item `dated` of `report`, a2's mark of
    `report`, and the main conversation's mark of `lead`
    When Lane reads the steps that a1, a2, and the main conversation marked
    Then they are `write`, `report`, and `lead`"""
    entries = [
        mark("write"),
        mark("report", item="dated"),
        mark("report", "a2"),
        mark("lead", None),
    ]
    assert steps_marked(entries) == ({"write"}, {"report"}, {"lead"})


@pytest.mark.supports(
    "test_a_step_gone_back_to_asks_its_items_again_and_keeps_its_reads",
    "test_an_end_after_going_back_is_stopped_with_the_step_gone_back_to",
)
def test_a_step_gone_back_to_undoes_the_marks_and_items_of_each_step_it_undid():
    """Given a run whose writer a1 read NOTES.md, marked the items `dated` and `linked` and the step
    `write`, read CHANGELOG.md, gave `written`, and marked `report`, then went back to `write`,
    undoing `write` and `report`
    When Lane reads what counts for a1
    Then it's both reads and its result, with no mark of a step or an item"""
    entries = [
        START,
        TIE,
        lane_entries.read("a1", "NOTES.md", 1, 6),
        mark("write", item="dated"),
        mark("write", item="linked"),
        mark("write"),
        lane_entries.read("a1", "CHANGELOG.md", 1, 4),
        lane_entries.result("a1", "written"),
        mark("report"),
        back("write", ["write", "report"]),
    ]
    lines = {"NOTES.md": set(range(1, 7)), "CHANGELOG.md": set(range(1, 5))}
    assert read_state(entries).done_by("a1") == Done(lines=lines, result="written")


@pytest.mark.supports(
    "test_a_later_step_marked_after_going_back_is_stopped_with_the_step_gone_back_to"
)
def test_a_step_gone_back_to_leaves_the_marks_of_each_step_before_it():
    """Given a run whose writer a1 marked the item `dated` and the step `write`, and the step
    `report`, then went back to `report`, undoing it alone
    When Lane reads what counts for a1
    Then it's the marks of `write` and its item"""
    entries = [START, TIE, mark("write", item="dated"), mark("write"), mark("report")]
    state = read_state([*entries, back("report", ["report"])])
    assert state.done_by("a1") == Done(steps={"write"}, items={"write": {"dated"}})


@pytest.mark.supports("test_each_step_taken_again_in_order_after_going_back_lets_the_end_through")
def test_marks_after_a_step_gone_back_to_count():
    """Given a run whose writer a1 marked `write`, went back to it, then marked the item `dated`
    and the step `write` again
    When Lane reads what counts for a1
    Then it's the marks made after it went back: `write` and its item"""
    went = back("write", ["write", "report"])
    entries = [START, TIE, mark("write"), went, mark("write", item="dated"), mark("write")]
    assert read_state(entries).done_by("a1") == Done(steps={"write"}, items={"write": {"dated"}})


@pytest.mark.supports("test_each_step_taken_again_in_order_after_going_back_lets_the_end_through")
@pytest.mark.parametrize(
    "first, then",
    [
        (back("report", ["report"]), back("write", ["write", "report"])),
        (back("write", ["write", "report"]), back("report", ["report"])),
    ],
)
def test_each_step_gone_back_to_undoes_only_the_marks_before_it(first: Entry, then: Entry):
    """Given a run whose writer a1 marked `write` and `report`, went back to the first step, marked
    again each step it undid, went back to the second, and marked `write` again: back to `report`
    then `write`, or to `write` then `report`
    When Lane reads the steps a1 marked
    Then it marked `write` alone in each, as a step gone back to undoes no mark after it"""
    again = [mark(each) for each in first["undone"]]
    entries = [
        START,
        TIE,
        mark("write"),
        mark("report"),
        first,
        *again,
        then,
        *([mark("write")] if "write" in then["undone"] else []),
    ]
    assert read_state(entries).done_by("a1").steps == {"write"}


@pytest.mark.supports("test_two_starts_of_one_role_are_each_held_to_their_own_start")
def test_a_step_gone_back_to_undoes_only_the_marks_of_whoever_went_back():
    """Given a run whose writers a1 and a2 and the main conversation each marked their steps, then
    a2 went back to `write`, and the main conversation to `lead`
    When Lane reads the steps that a1, a2, and the main conversation marked
    Then a1 marked `write` and `report`, and a2 and the main conversation marked none"""
    entries = [
        START,
        TIE,
        lane_entries.start("toolu_2"),
        lane_entries.tie("toolu_2", "a2"),
        mark("write"),
        mark("report"),
        mark("write", "a2"),
        mark("lead", None),
        back("write", ["write", "report"], "a2"),
        back("lead", ["lead"], None),
    ]
    assert steps_marked(entries) == ({"write", "report"}, set(), set())


@pytest.mark.supports("test_two_starts_of_one_role_are_each_held_to_their_own_start")
def test_what_counts_for_a_subagent_holds_its_own_moves_across_turns():
    """Given a run whose writer a1 marked `write` in the main conversation's first turn and gave
    `written` in its second, with the main conversation's mark and the reviewer a2's mark beside
    them
    When Lane reads what counts for a1
    Then it's its mark and its result"""
    entries = [
        START,
        turn(),
        TIE,
        mark("write"),
        mark("up", None),
        TURN_ENDED,
        turn("Go on."),
        mark("review", "a2"),
        lane_entries.result("a1", "written"),
    ]
    assert read_state(entries).done_by("a1") == Done(steps={"write"}, result="written")


@pytest.mark.supports("test_a_read_of_the_main_conversation_counts_for_no_subagent")
def test_what_counts_for_the_main_conversation_with_no_turn_is_each_move_with_no_agent():
    """Given a run of log:up whose rules fix its steps, holding the writer's start, tie, and mark,
    and the main conversation's mark of `lead`
    When Lane reads what counts for the main conversation
    Then it's its mark of `lead` alone"""
    entries = [RUN, FOLDER, START, TIE, mark("write"), mark("lead", None)]
    assert read_state(entries).done_by(None) == Done(steps={"lead"})


@pytest.mark.supports(
    "test_a_turn_whose_first_move_is_its_end_is_held_to_its_own_steps_afresh",
    "test_two_subagents_ends_one_after_the_other_each_begin_a_turn_of_their_own",
)
@pytest.mark.parametrize("turns", [1, 2, 3])
def test_what_counts_for_the_main_conversation_is_its_moves_after_its_latest_turn(turns: int):
    """Given a run of log:up taking its steps at each turn, with one, two, or three turns, each
    with the main conversation's mark of a step named for the turn, and the writer's mark of
    `write`, after its `turn`
    When Lane reads what counts for the main conversation
    Then it's the mark of the latest turn alone"""
    entries: list[Entry] = [START, TIE]
    for each in range(turns):
        entries += [turn() if each == 0 else turn("Go on."), mark("write"), mark(f"up{each}", None)]
        if each < turns - 1:
            entries += [TURN_ENDED, begun("Go on.")]
    assert read_state(entries).done_by(None) == Done(steps={f"up{turns - 1}"})


@pytest.mark.supports("test_a_turn_whose_first_move_is_its_end_is_held_to_its_own_steps_afresh")
def test_nothing_counts_for_the_main_conversation_at_its_turns_first_move():
    """Given a run of log:up taking its steps at each turn, whose second turn's `turn` entry is its
    last, after the first turn's mark of `up`
    When Lane reads what counts for the main conversation
    Then nothing does"""
    entries = [turn(), mark("up", None), TURN_ENDED, begun("Go on."), turn("Go on.")]
    assert read_state(entries).done_by(None) == Done()
