"""The unit cases of session/permissions.py, what a task's session may do: `arguments`, of a task
that may only read and of one that may write, each anew and in its session, and of a prompt that
starts with a hyphen and holds quotes and line breaks, each read as Claude Code's parser reads them,
and each use decided as the documentation says Claude Code decides it, by the double of Claude
Code."""

from __future__ import annotations

import os
import uuid

import claude_double
import pytest
from claude_double import Use
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

WORK = os.path.join(os.sep, "home", "dev", "work", "shop fix")
HOME = os.path.join(os.sep, "home", "dev")
TMP = os.path.join(os.path.realpath(os.sep), "tmp", "claude")
READING = Task("review", os.path.join(HOME, "overnight", "review.md"), WORK, False)
WRITING = Task("fix", os.path.join(HOME, "overnight", "fix.md"), WORK, True)
PROMPT = "Review the payment module."


def arguments(task: Task, session: str | None, prompt: str = PROMPT) -> list[str]:
    from session.permissions import arguments as given

    return given(task, session, prompt)


def read(args: list[str]) -> tuple[dict[str, list[str]], str]:
    """The options and the prompt, as Claude Code's parser reads them, which finds nothing wrong."""
    flags, prompt, wrong = claude_double.parsed(args)
    assert wrong is None, wrong
    return flags, prompt


@pytest.mark.supports(
    "test_a_task_uses_its_tools_with_no_permission_asked",
    "test_a_task_writes_only_where_the_queue_lets_it",
)
@pytest.mark.parametrize("task", [READING, WRITING], ids=["reading", "writing"])
def test_a_task_anew_runs_its_prompt_in_a_session_of_its_own_id(task: Task):
    """Given a task that may only read, or one that may write, with no session
    When its arguments are made
    Then they print the stream, run the prompt in a session of a new ID, resume none, and bypass
    no permission check"""
    flags, prompt = read(arguments(task, None))

    assert prompt == PROMPT
    assert ("-p" in flags or "--print" in flags) and "--verbose" in flags
    assert flags["--output-format"] == ["stream-json"]
    assert uuid.UUID(flags["--session-id"][0])
    assert "--resume" not in flags and "-r" not in flags
    assert "--dangerously-skip-permissions" not in flags
    assert flags.get("--permission-mode") != ["bypassPermissions"]


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
@pytest.mark.parametrize("task", [READING, WRITING], ids=["reading", "writing"])
def test_a_task_in_its_session_goes_on_in_it(task: Task):
    """Given a task in the session `1b4e28ba`
    When its arguments are made
    Then they resume that session, and give no new ID"""
    flags, prompt = read(arguments(task, "1b4e28ba"))

    assert (prompt, flags["--resume"]) == (PROMPT, ["1b4e28ba"])
    assert "--session-id" not in flags


@pytest.mark.supports("test_a_task_uses_its_tools_with_no_permission_asked")
def test_a_prompt_that_starts_with_a_hyphen_reads_as_the_prompt():
    """Given a task whose prompt starts with `- ` and holds quotes and a line break
    When its arguments are made
    Then Claude Code's parser reads the prompt as given"""
    text = '- List each fault.\nName each by "file:line".'

    assert read(arguments(READING, None, text))[1] == text


@pytest.mark.supports(
    "test_a_task_uses_its_tools_with_no_permission_asked",
    "test_a_task_writes_only_where_the_queue_lets_it",
)
@pytest.mark.parametrize(
    ("use", "allowed"),
    [
        (Use("Read", os.path.join(WORK, "shop", "card.py")), True),
        (Use("Grep", os.path.join(WORK, "shop")), True),
        (Use("Glob", WORK), True),
        (Use("Edit", os.path.join(WORK, "shop", "card.py")), False),
        (Use("Write", os.path.join(WORK, "notes.md")), False),
        (Use("Bash", None, "ls"), False),
        (Use("Bash", os.path.join(WORK, "notes.md"), "echo x > notes.md"), False),
        (Use("NotebookEdit", os.path.join(WORK, "a.ipynb")), False),
    ],
    ids=["Read", "Grep", "Glob", "Edit", "Write", "a shell", "a shell's write", "NotebookEdit"],
)
def test_a_task_that_may_only_read_is_given_the_tools_that_read_and_no_shell(
    use: Use, allowed: bool
):
    """Given a task that may only read, in its folder
    When its session makes a use
    Then it may read, search, and list in its folder, and may not edit, write, or run a shell"""
    assert claude_double.allows(arguments(READING, None), WORK, use) is allowed


@pytest.mark.supports(
    "test_a_task_uses_its_tools_with_no_permission_asked",
    "test_a_task_writes_only_where_the_queue_lets_it",
)
@pytest.mark.parametrize(
    ("use", "allowed"),
    [
        (Use("Read", os.path.join(WORK, "shop", "checkout.py")), True),
        (Use("Edit", os.path.join(WORK, "shop", "checkout.py")), True),
        (Use("Write", os.path.join(WORK, "tests", "test_cache.py")), True),
        (Use("Bash", None, "pytest tests/test_checkout.py::test_total --count 20"), True),
        (Use("Bash", os.path.join(WORK, "log.txt"), "pytest > log.txt"), True),
        (Use("Bash", os.path.join(TMP, "cache.txt"), "echo x > $TMPDIR/cache.txt"), True),
        (Use("Bash", os.path.join(HOME, "outside.txt"), "echo x > ~/outside.txt"), False),
        (Use("Edit", os.path.join(HOME, "work", "shop", "checkout.py")), False),
        (Use("Write", os.path.join(HOME, ".bashrc")), False),
    ],
    ids=[
        "Read",
        "Edit in its dir",
        "Write in its dir",
        "a shell",
        "a shell's write in its dir",
        "a shell's write in the temporary folder",
        "a shell's write outside",
        "Edit beside its dir",
        "Write outside",
    ],
)
def test_a_task_that_may_write_writes_only_in_its_dir_and_its_temporary_folder(
    use: Use, allowed: bool
):
    """Given a task that may write, in its folder, where the sandbox runs
    When its session makes a use
    Then it may read, edit, and write in its folder, and run a shell that writes there or in its
    temporary folder, and may write nowhere else, by an edit, a write, or a shell"""
    assert claude_double.allows(arguments(WRITING, None), WORK, use) is allowed


@pytest.mark.supports("test_a_task_writes_only_where_the_queue_lets_it")
def test_a_writing_tasks_shell_writes_nowhere_else_where_the_sandbox_cant_start():
    """Given a task that may write, on a computer where the sandbox can't start
    When its session runs a shell that writes outside its folder
    Then it may not"""
    use = Use("Bash", os.path.join(HOME, "outside.txt"), "echo x > ~/outside.txt")

    assert claude_double.allows(arguments(WRITING, None), WORK, use, sandbox_runs=False) is False
