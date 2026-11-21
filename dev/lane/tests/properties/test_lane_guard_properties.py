"""The property-based test of the guard's judging of a write as Claude Code sends it, run through
the double of Claude Code: Claude Code sends the file that an AI writes whole, as the folder that
the conversation works in names it, through a link to that folder, or under a worktree that the
conversation entered, and the guard must judge the write by the file alone, from that folder, as a
whole path judged against one from the top stopped a right write in an E2E run. One bench serves
each input, as a bench takes Lane and `log` copied and a repository committed."""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Iterator

import lane_bench
import pytest
from claude_code import Agent
from hypothesis import given
from hypothesis import strategies as st

# Parts of a path, some of which nearly match the files that the writer's step `write` names,
# CHANGELOG.md and docs/changes/, and none of which the bench's repository holds.
PART = st.sampled_from(["docs", "changes", "changes-old", "CHANGELOG.md", "notes.md", "名前"])
FILE = st.builds(
    lambda up, parts: "../" * up + "/".join(parts),
    st.integers(0, 1),
    st.lists(PART, min_size=1, max_size=3),
)
# The folder that the writer's conversation works in, as Claude Code names the file in it: the
# repository, a link to it, or a worktree that the conversation entered.
FORMS = ("whole", "link", "worktree")


@pytest.fixture(scope="module")
def writers() -> Iterator[dict[str, tuple[Agent, str]]]:
    """For each form, a writer of a conversation in which the person typed /log:up 1.2.0, running
    at its step `write`, and the folder by which its file is named whole: the repository, a link
    to it, or the worktree that a second conversation entered before it started the writer, with
    the guard of the bench, as lane_bench.guard_of_the_bench says."""
    with tempfile.TemporaryDirectory() as tmp, lane_bench.guard_of_the_bench():
        b = lane_bench.bench(tmp)
        link = os.path.join(tmp, "link")
        os.symlink(b.repo, link)
        writer = lane_bench.started(lane_bench.opened(b))
        in_worktree = lane_bench.opened(b)
        in_worktree.enter_worktree("entry")
        worktree = os.path.join(b.repo, ".claude", "worktrees", "entry")
        yield {
            "whole": (writer, b.repo),
            "link": (writer, link),
            "worktree": (lane_bench.started(in_worktree), worktree),
        }


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_names_goes_through")
@given(FILE, st.sampled_from(FORMS))
def test_a_write_is_judged_by_the_file_it_names_whatever_its_form(
    writers: dict[str, tuple[Agent, str]], file: str, form: str
):
    """Given the writer of log running at its step `write`, which writes CHANGELOG.md and
    docs/changes/, in the repository or in a worktree that its conversation entered, and any file
    inside the conversation's folder or outside it
    When the writer writes the file through the double of Claude Code, which names it whole, from
    the folder or from a link to it
    Then the guard stops the write exactly where the file, from the conversation's folder, is
    neither CHANGELOG.md nor under docs/changes/, and the file is written exactly where the guard
    lets it through
    (Model-based and metamorphic, resting on S1, the Strategy of each move placed on its run and
    start, and named_files.of_call's Gives.)"""
    agent, folder = writers[form]
    top = os.path.normpath(file)
    parts = top.split("/")
    first = os.path.join(folder, *parts[: 2 if parts[0] == ".." else 1])
    try:
        answer = agent.write(os.path.join(folder, top), "x\n")
        written = os.path.isfile(os.path.realpath(os.path.join(folder, top)))
    finally:
        if os.path.isdir(first) and not os.path.islink(first):
            shutil.rmtree(first)
        elif os.path.lexists(first):
            os.remove(first)
    allowed = top == "CHANGELOG.md" or top.startswith("docs/changes/")
    assert (answer.blocked, written) == (not allowed, allowed), answer.said
