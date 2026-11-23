"""Decides what a task's session may do: the tools it's allowed and refused, and the sandbox that
holds a writing task's commands to its dir and its temporary files."""

from __future__ import annotations

from stacker.queue_file import Task


def arguments(task: Task, session: str | None, prompt: str) -> list[str]:
    """The arguments of `claude` that run the task's prompt with what the task may do.

    Takes: the task, the session it goes on in, or None for a new one, and the prompt's text.
    Gives: the arguments that run the prompt in a session of its own ID, or that go on in the
    session, with the task's tools allowed and every other tool refused, a task that may only read
    given only the tools that read and no shell, and a writing task given its edits in its dir and
    its shell in Claude Code's sandbox, which lets it write only there and in its own temporary
    folder, with no retry outside it.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("session.permissions.arguments")
