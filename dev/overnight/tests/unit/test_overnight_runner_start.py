"""The unit cases of runner/start.py, how a runner is started apart from the session: `start`, of a
piece whose run Claude Code holds, which gives at once the ID of the process that carries the
piece, apart from this session."""

from __future__ import annotations

import os
import time

import overnight_files
import pytest
from claude_code import claude_double
from overnight_files import PROMPT, TOOLS, handed, piece_folder
from pieces.record import begin, read
from runner.carry import Piece
from runner.start import start

pytestmark = pytest.mark.xfail(strict=True, reason="runner.start isn't built yet")

# The longest that start may take, as it returns while its runner carries the piece.
AT_ONCE = 5.0


def piece(repo: str) -> Piece:
    """The walkthrough's piece 1, its folder made beside the repository."""
    folder = piece_folder(repo, 1)
    os.makedirs(folder)
    return Piece(repo, 1, folder, PROMPT, TOOLS)


@pytest.mark.supports("test_a_piece_goes_on_after_the_session_that_handed_it_over_closes")
def test_start_gives_at_once_the_runner_that_carries_the_piece_apart_from_the_session(
    repo: str, stand_in: str
):
    """Given the walkthrough's piece, and Claude Code holding its run until the case releases it,
    then ending it with `Done.`
    When its runner is started, the piece is recorded with the ID that start gives, and the run
    is released
    Then start gave within five seconds, while the run was held; the ID is the parent of Claude
    Code's run; where the OS keeps sessions, the runner's is another than this process's; and the
    record comes to done with `Done.`"""
    given = piece(repo)
    claude_double.plays(stand_in, {"1": [{"kind": "ends", "hold": "run", "last_words": "Done."}]})
    began = time.monotonic()
    pid = start(given)
    assert time.monotonic() - began < AT_ONCE
    begin(repo, handed(1, TOOLS), pid)
    overnight_files.until(lambda: len(claude_double.calls(stand_in)) == 1, what="the run")
    assert claude_double.calls(stand_in)[0]["ppid"] == pid
    if hasattr(os, "getsid"):
        assert os.getsid(pid) != os.getsid(0)
    claude_double.release(stand_in, "run")
    overnight_files.until(lambda: read(repo)[0].state == "done", what="the piece to end")
    assert read(repo)[0].last_words == "Done."
