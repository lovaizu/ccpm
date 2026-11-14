"""The unit cases of domain/guard.py: what the guard gives on each moment, through `decide`, with
the walkthrough's laid set and run records in a folder of each test's own, and the decisions it
alone makes, through `in_run`, `result_since`, and `starts_from_main`."""

from __future__ import annotations

import os
from typing import Any

import pytest
from domain.event import (
    BEGUN,
    CALL,
    COMMAND,
    ENDS,
    RAN,
    REACHED,
    SKILL,
    START,
    TURN_ENDS,
    TYPED,
    Call,
    Event,
)
from domain.guard import LET_THROUGH, decide, in_run, result_since, run_of, starts_from_main
from domain.laid_set import START as MOVE_START
from domain.laid_set import Lane, Move
from domain.run_record import AI, PERSON, Called, Noted, Result, Run, Start, Tied, load
from lane_parts import (
    CARRY_OUT,
    PLUGIN_ROOT,
    REVIEWER_END,
    ROOT,
    RUN_ONLY,
    SESSION,
    WRITER_GAVE_WRITTEN,
    WRITER_RUNNING,
    command,
    event,
    keep,
    laid_set,
    run,
    two_skills,
    writer_gave_written,
    writer_running,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

START_WRITER = "changelog: Start `changelog:writer` with `Carry out your steps`."
START_REVIEWER = "changelog: Start `changelog:reviewer` with `Carry out your steps`."


@pytest.fixture
def temp(tmp_path: Any) -> str:
    return os.path.realpath(str(tmp_path))


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_the_skills_command_typed_starts_the_run_with_the_first_start(temp: str):
    """Given `changelog` laid, and no Run in the conversation
    When the person types `/changelog:write`
    Then the guard gives writer's start beside the prompt, and adds the call of the person's Run of
    `write` to the run record"""
    decided = decide(event(TYPED, command="changelog:write"), laid_set(), PLUGIN_ROOT, temp)
    assert (decided.stop, decided.context) == (False, START_WRITER)
    assert load(temp, "changelog", SESSION) == (Called("write", PERSON),)


@pytest.mark.supports(
    "test_an_ai_that_called_up_by_the_skill_tool_lays_by_its_own_run_of_lay_write"
)
def test_the_skill_called_by_the_skill_tool_starts_a_run_of_an_ai(temp: str):
    """Given `changelog` laid, and no Run in the conversation
    When the main conversation calls `changelog:write` by the Skill tool
    Then the guard lets the call through, and adds the call of an AI's Run of `write`"""
    moment = event(CALL, call=Call(SKILL, skill="changelog:write"))
    assert not decide(moment, laid_set(), PLUGIN_ROOT, temp).stop
    assert load(temp, "changelog", SESSION) == (Called("write", AI),)


@pytest.mark.supports("test_the_main_conversations_own_work_before_and_after_a_run_goes_unchecked")
def test_a_prompt_outside_a_run_is_let_through_as_it_is(temp: str):
    """Given `changelog` laid, and no Run in the conversation
    When the person types `What does tally do?`
    Then the guard lets it through with nothing to add"""
    moment = event(TYPED, prompt="What does tally do?")
    assert decide(moment, laid_set(), PLUGIN_ROOT, temp) == LET_THROUGH


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_start_that_the_moves_open_is_let_through_and_added(temp: str):
    """Given a Run whose move due starts reviewer with `Carry out your steps`
    When the main conversation starts `changelog:reviewer` with it
    Then the guard lets it through, and adds the Start, with the skill of its Run, as a line after
    the lines before"""
    keep(temp, *WRITER_GAVE_WRITTEN)
    moment = event(CALL, call=Call(START, role="changelog:reviewer", text=CARRY_OUT))
    assert not decide(moment, laid_set(), PLUGIN_ROOT, temp).stop
    added = Start(2, "reviewer", CARRY_OUT, skill="write")
    assert load(temp, "changelog", SESSION) == (*WRITER_GAVE_WRITTEN, added)


@pytest.mark.supports("test_a_start_that_the_moves_dont_open_is_stopped_with_the_moves")
def test_a_start_that_the_moves_dont_open_is_stopped_with_the_moves(temp: str):
    """Given a Run whose move due starts reviewer
    When the main conversation starts `changelog:writer`
    Then the guard stops it, with reviewer's start"""
    keep(temp, *WRITER_GAVE_WRITTEN)
    moment = event(CALL, call=Call(START, role="changelog:writer", text=CARRY_OUT))
    decided = decide(moment, laid_set(), PLUGIN_ROOT, temp)
    assert decided.stop and START_REVIEWER in decided.said


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_subagents_call_that_breaks_a_lane_is_stopped_with_its_sentence(temp: str):
    """Given a Run in which writer, subagent a1, runs
    When writer runs `git -C /repo log --oneline`
    Then the guard stops it, with the sentence of step 2 first"""
    keep(temp, *WRITER_RUNNING)
    moment = command("git -C /repo log --oneline", agent="a1", role="changelog:writer")
    decided = decide(moment, laid_set(), PLUGIN_ROOT, temp)
    assert decided.stop and decided.said.startswith(f"changelog: {RUN_ONLY}\n")


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_subagents_call_that_keeps_every_lane_is_let_through_and_not_kept(temp: str):
    """Given a Run in which writer, subagent a1, runs
    When writer runs `git log --oneline`
    Then the guard lets it through, and adds no line, as no later move rests on the Call"""
    keep(temp, *WRITER_RUNNING)
    moment = command("git log --oneline", agent="a1", role="changelog:writer")
    assert not decide(moment, laid_set(), PLUGIN_ROOT, temp).stop
    assert load(temp, "changelog", SESSION) == WRITER_RUNNING


@pytest.mark.supports(
    "test_an_end_that_starts_no_line_with_a_line_that_its_command_printed_is_held"
)
def test_what_a_lanes_command_printed_is_kept_for_its_subagent(temp: str):
    """Given a Run in which writer, subagent a1, runs, with a names_printed Lane on
    `git log --oneline`
    When `git log --oneline` ran and printed `d417d74 Add --lines`
    Then the guard adds that line, for a1"""
    lane = Lane("writer", 2, "agents/writer.md", "names_printed", ("git log --oneline",), "")
    given = laid_set(lanes=(*laid_set().lanes, lane))
    keep(temp, *WRITER_RUNNING)
    ran = event(
        RAN,
        agent="a1",
        role="changelog:writer",
        call=Call("command", command="git log --oneline"),
        printed="d417d74 Add --lines\n",
    )
    decide(ran, given, PLUGIN_ROOT, temp)
    printed = Noted("printed", "a1", "d417d74 Add --lines")
    assert load(temp, "changelog", SESSION) == (*WRITER_RUNNING, printed)


@pytest.mark.supports(
    "test_a_subagents_start_of_a_role_is_stopped_with_the_sentence_of_its_last_step"
)
def test_a_subagents_start_of_a_role_is_stopped_with_its_last_steps_sentence(temp: str):
    """Given a Run in which writer, subagent a1, runs
    When writer starts `changelog:reviewer`
    Then the guard stops it, with the sentence of writer's last step"""
    keep(temp, *WRITER_RUNNING)
    moment = event(
        CALL, agent="a1", role="changelog:writer", call=Call(START, role="changelog:reviewer")
    )
    decided = decide(moment, laid_set(), PLUGIN_ROOT, temp)
    assert decided.stop and "writer written" in decided.said


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_a_subagents_end_with_no_result_is_stopped_with_its_last_steps_sentence(temp: str):
    """Given a Run in which reviewer, subagent a2, runs, and gave no Result
    When reviewer ends with `No more entries`
    Then the guard stops the end, with the sentence of reviewer's step 2, its plugin's folder in
    place of `${CLAUDE_PLUGIN_ROOT}`"""
    keep(temp, *WRITER_GAVE_WRITTEN, Start(2, "reviewer", CARRY_OUT, skill="write"), Tied(2, "a2"))
    moment = event(ENDS, agent="a2", role="changelog:reviewer", message="No more entries")
    decided = decide(moment, laid_set(), PLUGIN_ROOT, temp)
    sentence = REVIEWER_END.replace("${CLAUDE_PLUGIN_ROOT}", PLUGIN_ROOT)
    assert decided.stop and decided.said == f"changelog: {sentence}"


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_an_end_that_reaches_the_main_conversation_after_a_result_gives_the_next_start(temp: str):
    """Given a Run in which writer, subagent a1, gave `written` and ended
    When its end reaches the main conversation
    Then the guard gives ``writer gave `written`.`` and reviewer's start beside it"""
    keep(temp, *WRITER_RUNNING, Result("writer", "written", "a1"))
    moment = event(REACHED, agent="a1", status="completed", message="Gave written.")
    decided = decide(moment, laid_set(), PLUGIN_ROOT, temp)
    assert decided.context == (
        "changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out your steps`."
    )


@pytest.mark.supports(
    "test_the_main_conversation_stopping_while_a_start_is_due_and_none_runs_is_held"
)
def test_the_turn_ending_while_a_start_is_due_and_none_runs_is_stopped_with_the_moves(temp: str):
    """Given a Run whose move due starts reviewer, and no subagent runs
    When the main conversation ends its turn
    Then the guard stops the end, with reviewer's start alone, as the walkthrough shows"""
    keep(temp, *WRITER_GAVE_WRITTEN)
    decided = decide(event(TURN_ENDS, message="Should I go on?"), laid_set(), PLUGIN_ROOT, temp)
    assert (decided.stop, decided.said) == (True, START_REVIEWER)


@pytest.mark.supports(
    "test_a_resume_that_a_route_lists_counts_as_a_start_of_the_subagent_it_resumes"
)
def test_a_subagent_beginning_after_a_start_is_tied_to_that_start(temp: str):
    """Given a Run whose Start 2 of reviewer the guard let through, with no subagent named yet
    When subagent a2 of `changelog:reviewer` begins
    Then the guard adds the tie of Start 2 to a2"""
    started = Start(2, "reviewer", CARRY_OUT, skill="write")
    keep(temp, *WRITER_GAVE_WRITTEN, started)
    decide(event(BEGUN, agent="a2", role="changelog:reviewer"), laid_set(), PLUGIN_ROOT, temp)
    assert load(temp, "changelog", SESSION) == (*WRITER_GAVE_WRITTEN, started, Tied(2, "a2"))


@pytest.mark.supports("test_the_main_conversations_own_work_before_and_after_a_run_goes_unchecked")
def test_a_moment_before_the_skills_call_lies_outside_the_run():
    """Given `changelog` laid, and no Run
    When the main conversation starts `changelog:reviewer`
    Then the moment lies outside a Run"""
    moment = event(CALL, call=Call(START, role="changelog:reviewer"))
    assert not in_run(moment, laid_set(), ())


@pytest.mark.supports("test_the_main_conversations_own_work_before_and_after_a_run_goes_unchecked")
def test_a_moment_after_the_run_ended_lies_outside_it():
    """Given a Run of `changelog` that ended
    When the main conversation runs `git status`
    Then the moment lies outside the Run"""
    assert not in_run(command("git status"), laid_set(), [run(ended=True)])


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_call_of_the_main_conversation_or_a_role_of_the_plugin_in_the_run_lies_in_it():
    """Given a Run of `changelog` that goes on
    When the main conversation runs `git status`, and writer runs `git log --oneline`
    Then each moment lies in the Run"""
    given = [writer_running()]
    assert in_run(command("git status"), laid_set(), given)
    assert in_run(command("git log --oneline", "a1", "changelog:writer"), laid_set(), given)


@pytest.mark.supports("test_the_main_conversations_own_work_before_and_after_a_run_goes_unchecked")
def test_a_call_of_a_subagent_of_another_plugin_lies_outside_the_run():
    """Given a Run of `changelog` that goes on
    When subagent a9 of `other:helper` runs `git status`
    Then the moment lies outside the Run"""
    assert not in_run(command("git status", "a9", "other:helper"), laid_set(), [writer_running()])


@pytest.mark.supports("test_a_subagent_of_a_role_that_no_start_of_the_run_ties_goes_unchecked")
def test_a_call_of_a_subagent_of_a_role_that_no_start_ties_lies_outside_the_run():
    """Given a Run of `changelog` whose Start 1 ties writer's subagent a1
    When subagent a7 of `changelog:writer` runs `git status`
    Then the moment lies outside the Run"""
    moment = command("git status", "a7", "changelog:writer")
    assert not in_run(moment, laid_set(), [writer_running()])


@pytest.mark.supports(
    "test_compact_while_a_subagent_runs_lets_the_summary_end_and_holds_the_subagent_after_it"
)
def test_the_end_of_the_compactions_summary_lies_outside_the_run():
    """Given a Run of `changelog` in which writer runs
    When subagent a8, with no role, ends, as the compaction's summary does
    Then the moment lies outside the Run"""
    moment = event(ENDS, agent="a8", role="", message="<the compaction's summary>")
    assert not in_run(moment, laid_set(), [writer_running()])


@pytest.mark.supports(
    "test_a_run_in_one_conversation_holds_nothing_in_another_in_the_same_repository"
)
def test_a_moment_of_another_conversation_lies_outside_the_run():
    """Given a Run of `changelog` in one conversation
    When the main conversation of another conversation, by its `session_id`, runs `git status`
    Then the moment lies outside the Run"""
    moment = Event(CALL, "another-session", ROOT, ROOT, call=Call(COMMAND, command="git status"))
    assert not in_run(moment, laid_set(), [writer_running()])


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_the_result_since_a_start_is_the_one_its_subagent_gave():
    """Given a Run in which writer, subagent a1, gave `written` since its Start
    When the result since a1's Start is asked
    Then it is `written`"""
    given = writer_running()
    given.results.append(Result("writer", "written", "a1", 1))
    assert result_since(given, "a1") == Result("writer", "written", "a1", 1)


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_no_result_since_a_start_is_none():
    """Given a Run in which writer, subagent a1, gave nothing since its Start
    When the result since a1's Start is asked
    Then there is none"""
    assert result_since(writer_running(), "a1") is None


@pytest.mark.supports(
    "test_a_resume_that_a_route_lists_counts_as_a_start_of_the_subagent_it_resumes"
)
def test_a_result_from_before_a_resume_is_none_since_it():
    """Given a Run in which writer, subagent a1, gave `written`, and a resume of a1 counts as
    Start 3 since
    When the result since a1's last Start is asked
    Then there is none"""
    given = writer_gave_written()
    given.starts.append(Start(3, "writer", CARRY_OUT, agent="a1", running=True, resumes=1))
    assert result_since(given, "a1") is None


@pytest.mark.supports(
    "test_a_subagents_start_of_a_role_is_stopped_with_the_sentence_of_its_last_step"
)
def test_a_start_from_the_main_conversation_comes_from_main_and_a_subagents_doesnt():
    """Given a start of `changelog:reviewer` by the main conversation, and one by subagent a1
    When it's asked of each whether it comes from the main conversation
    Then the first does and the second doesn't"""
    by_main = event(CALL, call=Call(START, role="changelog:reviewer"))
    by_a1 = event(
        CALL, agent="a1", role="changelog:writer", call=Call(START, role="changelog:reviewer")
    )
    assert starts_from_main(by_main) and not starts_from_main(by_a1)


def review_running() -> Run:
    """A Run of `review` in which reviewer, subagent a2 of Start 2, runs."""
    started = Start(2, "reviewer", CARRY_OUT, agent="a2", running=True, skill="review")
    return run(skill="review", starts=[started])


@pytest.mark.supports("test_runs_of_two_skills_go_on_side_by_side_each_moved_by_its_own_results")
def test_a_subagents_moment_goes_to_the_run_of_the_start_that_ties_it():
    """Given a Run of `write` in which writer, a1, runs, and a Run of `review` in which reviewer,
    a2, runs
    When reviewer runs `git status`, and writer runs `git log --oneline`
    Then the first goes to the Run of `review`, and the second to the Run of `write`"""
    write, review = writer_running(), review_running()
    assert (
        run_of(command("git status", "a2", "changelog:reviewer"), two_skills(), [write, review])
        is review
    )
    assert (
        run_of(
            command("git log --oneline", "a1", "changelog:writer"), two_skills(), [write, review]
        )
        is write
    )


@pytest.mark.supports("test_runs_of_two_skills_go_on_side_by_side_each_moved_by_its_own_results")
def test_a_skills_call_goes_to_the_run_of_that_skill():
    """Given a Run of `write` and a Run of `review`
    When the person types `/changelog:review`
    Then the moment goes to the Run of `review`"""
    write, review = writer_running(), review_running()
    moment = event(TYPED, command="changelog:review")
    assert run_of(moment, two_skills(), [write, review]) is review


@pytest.mark.supports("test_the_skills_own_result_ends_only_the_run_of_the_skill_it_names")
def test_the_main_conversations_run_of_result_py_goes_to_the_run_of_the_skill_it_names():
    """Given a Run of `write` and a Run of `review`
    When the main conversation runs `result.py review good`
    Then the moment goes to the Run of `review`"""
    write, review = writer_running(), review_running()
    moment = command(f"python3 {PLUGIN_ROOT}/hooks/lane/result.py review good")
    assert run_of(moment, two_skills(), [write, review]) is review


@pytest.mark.supports(
    "test_a_start_that_the_moves_of_two_runs_open_goes_to_the_run_that_began_first"
)
def test_a_start_that_two_runs_moves_open_goes_to_the_run_that_began_first():
    """Given a Run of `write` whose move due starts reviewer, and a later Run of `review` whose
    move due starts reviewer too
    When the main conversation starts `changelog:reviewer` with `Carry out your steps`
    Then the moment goes to the Run of `write`"""
    write = writer_gave_written()
    review = run(skill="review", moves=[Move(MOVE_START, "reviewer")])
    moment = event(CALL, call=Call(START, role="changelog:reviewer", text=CARRY_OUT))
    assert run_of(moment, two_skills(), [write, review]) is write


@pytest.mark.supports("test_runs_of_two_skills_go_on_side_by_side_each_moved_by_its_own_results")
def test_a_start_that_one_runs_moves_open_goes_to_that_run():
    """Given a Run of `write` in which writer runs, and a Run of `review` whose move due starts
    reviewer
    When the main conversation starts `changelog:reviewer` with `Carry out your steps`
    Then the moment goes to the Run of `review`"""
    write = writer_running()
    review = run(skill="review", moves=[Move(MOVE_START, "reviewer")])
    moment = event(CALL, call=Call(START, role="changelog:reviewer", text=CARRY_OUT))
    assert run_of(moment, two_skills(), [write, review]) is review


@pytest.mark.supports("test_a_subagent_of_a_role_that_no_start_of_the_run_ties_goes_unchecked")
def test_a_subagent_that_no_start_ties_goes_to_no_run():
    """Given a Run of `write` whose Start 1 ties writer's subagent a1
    When subagent a7 of `changelog:writer` runs `git status`
    Then the moment goes to no Run"""
    moment = command("git status", "a7", "changelog:writer")
    assert run_of(moment, two_skills(), [writer_running()]) is None


@pytest.mark.supports(
    "test_the_main_conversation_is_held_to_the_lanes_of_each_skill_whose_run_goes_on"
)
def test_the_main_conversations_call_passes_where_a_going_skills_lanes_allow_it(temp: str):
    """Given the Runs of `write`, whose step 1 runs only `git log --oneline`, and of `review`,
    whose step 1 runs only `git diff`, going on
    When the main conversation runs `git diff`, and then `git status`
    Then the guard lets the first through, and stops the second with the sentence of each skill's
    step"""
    lanes = (
        Lane(
            "write",
            1,
            "skills/write/SKILL.md",
            "run_only",
            ("git log --oneline",),
            "Run only `git log --oneline`.",
        ),
        Lane(
            "review", 1, "skills/review/SKILL.md", "run_only", ("git diff",), "Run only `git diff`."
        ),
    )
    given = two_skills()
    given = two_skills(lanes=(*given.lanes, *lanes))
    keep(temp, Called("write", PERSON), Called("review", PERSON))
    assert not decide(command("git diff"), given, PLUGIN_ROOT, temp).stop
    stopped = decide(command("git status"), given, PLUGIN_ROOT, temp)
    assert stopped.stop and "`git log --oneline`" in stopped.said and "`git diff`." in stopped.said
