"""The integration cases of how the guard places each hook event on its Run, its Start, and its
role, as the guard's line in Components and the choice beside it say: a Run by the conversation's
`session_id`, the main conversation by an event with no `agent_id`, and a Start and its role by the
`agent_id` that the PostToolUse of its Agent call ties to it, in each state of Claude Code that
claude-code-states.md names. The test plays the person, the main conversation, and each subagent on
the double of Claude Code, which sends each event as the records show."""

from __future__ import annotations

import pytest
from claude_code import POSTED_FIRST, Conversation
from lane_example import Repo, conversation, gives, result_command, starts

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

START_REVIEWER = "Start `changelog:reviewer` with `Carry out your steps`."
START_WRITER = "changelog: Start `changelog:writer` with `Carry out your steps`."
RUN_ONLY = "changelog: Run only `git log --oneline`."


@pytest.mark.supports("guard", "Start", "Run")
def test_a_background_subagents_calls_after_a_later_prompt_are_held_by_its_own_start(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` in which writer runs in the background
    When the person types a prompt, which gives each later event a new `prompt_id`, and writer
    runs `git -C <repo> log --oneline`, and then gives `written`
    Then the guard stops the call with the sentence of writer's step 2, and Lane names reviewer's
    start after `written`"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    run.stop("writer runs.")
    run.type("How long does writer take?")
    stopped = writer.bash(f"git -C {laid.root} log --oneline")
    assert stopped.blocked and stopped.said.startswith(RUN_ONLY)
    assert START_REVIEWER in gives(laid, writer, "written").said


@pytest.mark.supports("guard", "Start")
def test_a_subagent_whose_start_comes_after_its_agent_calls_post_tool_use_is_tied_to_its_start(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog`
    When the main conversation starts writer, and Claude Code sends the PostToolUse of the Agent
    call before writer's SubagentStart, and writer runs `git -C <repo> log --oneline`
    Then the guard stops the call with the sentence of writer's step 2"""
    run.type("/changelog:write")
    _, writer = run.start("changelog:writer", "Carry out your steps", "writer", how=POSTED_FIRST)
    assert writer
    stopped = writer.bash(f"git -C {laid.root} log --oneline")
    assert stopped.blocked and stopped.said.startswith(RUN_ONLY)


@pytest.mark.supports("guard", "Run", "Start")
def test_compact_while_a_subagent_runs_lets_the_summary_end_and_holds_the_subagent_after_it(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` in which writer runs in the background
    When the person types `/compact`, whose summary ends as a subagent that no Start ties, and
    writer then runs `git -C <repo> log --oneline`, and gives `written`
    Then the guard lets the compaction through, stops writer's call with the sentence of its step
    2, and Lane names reviewer's start after `written`"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    assert not run.compact().blocked
    stopped = writer.bash(f"git -C {laid.root} log --oneline")
    assert stopped.blocked and stopped.said.startswith(RUN_ONLY)
    assert START_REVIEWER in gives(laid, writer, "written").said


@pytest.mark.supports("guard", "Start", "Result")
def test_a_message_queued_for_a_running_subagent_keeps_it_on_its_own_start(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog`, whose routes list no resume, in which writer runs
    When the main conversation sends writer a message by SendMessage, which Claude Code queues,
    and writer gives `written` and ends, starts again on the message, runs
    `git -C <repo> log --oneline`, and ends again
    Then the guard lets the message through, stops the call with the sentence of writer's step 2,
    and Lane names reviewer's start once writer's end reaches the main conversation"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    assert not run.resume(writer, "Run result.py at the end.").blocked
    writer.bash(result_command(laid, "writer", "written"))
    ended, reached = writer.end("Gave written.")
    assert not ended.blocked and reached is None and writer.running
    stopped = writer.bash(f"git -C {laid.root} log --oneline")
    assert stopped.blocked and stopped.said.startswith(RUN_ONLY)
    _, reached = writer.end("Gave written.")
    assert reached is not None and START_REVIEWER in reached.said


@pytest.mark.supports("guard", "Run")
def test_the_run_goes_on_after_the_main_conversation_enters_a_worktree(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` whose move due starts writer
    When the main conversation enters a worktree by EnterWorktree, which moves each event's `cwd`
    and `transcript_path`, and ends its turn
    Then the guard holds the stop with writer's start, as the Run of the same `session_id` goes
    on"""
    run.type("/changelog:write")
    assert not run.enter_worktree(name="entries").blocked
    stopped = run.stop("Done.")
    assert stopped.blocked and START_WRITER in stopped.said


@pytest.mark.supports("guard", "Start", "Run")
def test_a_subagent_of_a_role_that_no_start_of_the_run_ties_goes_unchecked(
    run: Conversation, laid: Repo
):
    """Given `changelog` laid, and writer started by the main conversation's own work before any
    Run
    When the person types `/changelog:write`, and that writer runs `git -C <repo> log --oneline`
    Then the guard lets the call through, as no Start of the Run ties that writer"""
    _, early = starts(run, "writer")
    assert early
    run.type("/changelog:write")
    assert not early.bash(f"git -C {laid.root} log --oneline").blocked


@pytest.mark.supports("guard", "Run")
def test_a_run_in_one_conversation_holds_nothing_in_another_in_the_same_repository(laid: Repo):
    """Given two conversations in one repository with `changelog` laid, and a Run of `changelog`
    in the first, whose move due starts writer
    When the second conversation's main conversation starts reviewer and ends its turn
    Then the guard lets both through, as the second conversation's `session_id` has no Run"""
    first = conversation(laid, laid.plugin)
    second = conversation(laid, laid.plugin)
    first.type("/changelog:write")
    answer, _ = starts(second, "reviewer")
    assert not answer.blocked
    assert not second.stop("Done.").blocked
