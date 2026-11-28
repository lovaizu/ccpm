"""The cases of how a run is asked of Claude Code and how its reply is read, which support the cases
of one work in test_overnight_work.py."""

from __future__ import annotations

from claude import claude_double
from overnight import claude

TOOLS = "Read,Edit,Bash(pytest:*)"


def test_asks_a_new_run_with_the_prompt_on_stdin_in_the_work_folder(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work with no conversation yet
    When overnight asks Claude Code for a run
    Then it runs `claude -p` in JSON with the work's tools, in the work's folder, the prompt on
    stdin."""
    double.answer(claude_double.DONE)

    claude_reply_of(work_dir, None)

    call = double.calls()[0]
    assert (call["args"], call["stdin"], call["cwd"]) == (
        ["-p", "--output-format", "json", "--allowed-tools", TOOLS],
        "Move the tests",
        work_dir,
    )


def test_asks_a_run_in_the_same_conversation_by_resume(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose conversation is known
    When overnight asks Claude Code for a run
    Then it runs `claude -p` with `--resume` and the conversation's session ID."""
    double.answer(claude_double.RESUMED)

    claude_reply_of(work_dir, claude_double.SESSION_ID)

    assert double.calls()[0]["args"] == [
        "-p",
        "--output-format",
        "json",
        "--allowed-tools",
        TOOLS,
        "--resume",
        claude_double.SESSION_ID,
    ]


def test_reads_a_run_with_exit_0_and_no_error_as_done(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given Claude Code that exits 0 with a result that says no error
    When overnight reads its reply
    Then the run is done, in the result's conversation."""
    double.answer(claude_double.DONE)

    assert claude_reply_of(work_dir, None) == claude.Reply(
        done=True, session_id=claude_double.SESSION_ID, reason=""
    )


def test_reads_the_usage_limit_with_exit_1_as_stopped_with_its_message(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given Claude Code that exits 1 at the usage limit
    When overnight reads its reply
    Then the run stopped, in the result's conversation, for the result's message."""
    double.answer(claude_double.LIMIT)

    assert claude_reply_of(work_dir, None) == claude.Reply(
        done=False, session_id=claude_double.SESSION_ID, reason=claude_double.LIMIT_TEXT
    )


def test_reads_the_usage_limit_with_exit_0_as_stopped_with_its_message(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given Claude Code that exits 0 at the usage limit, with a result that says it's an error
    When overnight reads its reply
    Then the run stopped, in the result's conversation, for the result's message."""
    double.answer(claude_double.LIMIT_EXIT_0)

    assert claude_reply_of(work_dir, None) == claude.Reply(
        done=False, session_id=claude_double.SESSION_ID, reason=claude_double.LIMIT_TEXT
    )


def test_reads_an_error_with_no_result_as_stopped_with_its_stderr(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given Claude Code that exits 1 with no result and a message on stderr
    When overnight reads its reply
    Then the run stopped, in no known conversation, for the message on stderr."""
    double.answer(claude_double.NO_CONVERSATION)

    assert claude_reply_of(work_dir, claude_double.SESSION_ID) == claude.Reply(
        done=False, session_id=None, reason=claude_double.NO_CONVERSATION_TEXT
    )


def test_reads_a_run_killed_with_no_word_as_stopped_with_its_exit_code(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given Claude Code that a signal kills before it says a word
    When overnight reads its reply
    Then the run stopped, in no known conversation, for the exit code that it ended with."""
    double.answer(claude_double.KILLED)

    assert claude_reply_of(work_dir, None) == claude.Reply(
        done=False, session_id=None, reason="claude ended with code -9 and no message"
    )


def claude_reply_of(work_dir: str, session_id: str | None) -> claude.Reply:
    return claude.ask(work_dir, TOOLS, "Move the tests", session_id)
