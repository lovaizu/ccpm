"""The unit cases of runner/command.py, runner.py's command line: `line`, of the walkthrough's
piece; `main`, of what `line` gives, of a prompt and tools that read as options and hold quotes,
commas, and words beyond ASCII, and of no standard input or an argument more than `line` gives."""

from __future__ import annotations

import os
import sys

import pytest
from claude_code import claude_double
from overnight_files import PLUGIN, PROMPT, PROMPT_AS_OPTIONS, TOOLS
from overnight_stand_ins import Clock, handed_over
from pieces.process import identify
from pieces.record import Record, read
from runner.command import line, main

pytestmark = pytest.mark.xfail(strict=True, reason="runner.command isn't built yet")


@pytest.mark.supports("test_a_piece_goes_on_after_the_session_that_handed_it_over_closes")
def test_line_runs_runner_py_by_this_python(repo: str):
    """Given the walkthrough's piece
    When the command line of its runner is asked
    Then its arguments start with this Python and overnight's `scripts/runner.py`, and its
    standard input holds the prompt"""
    piece, _ = handed_over(repo)
    args, stdin = line(piece)
    assert args[0] == sys.executable
    assert os.path.realpath(args[1]) == os.path.realpath(
        os.path.join(PLUGIN, "scripts", "runner.py")
    )
    assert PROMPT in stdin


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_main_of_what_line_gives_carries_the_piece_to_its_end(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code ending its run with `Done.`
    When runner.py runs with the arguments and standard input that `line` gives, less this Python
    and the script
    Then it gives 0, printing nothing; Claude Code ran once in the piece's folder with its tools
    and prompt; and the record is done with `Done.`"""
    piece, handed = handed_over(repo)
    claude_double.plays(stand_in, {"1": [{"kind": "ends", "last_words": "Done."}]})
    args, stdin = line(piece)
    assert main(args[2:], stdin) == (0, "", "")
    (call,) = claude_double.calls(stand_in)
    assert (call["cwd"], call["tools"], call["stdin"]) == (
        os.path.realpath(piece.folder),
        list(TOOLS),
        PROMPT,
    )
    assert read(repo) == [Record(handed, "done", identify(os.getpid()), (), "Done.")]


@pytest.mark.supports("test_the_prompt_reaches_claude_code_whole_on_its_standard_input")
def test_main_hands_on_a_prompt_and_tools_that_read_as_options_whole(
    repo: str, stand_in: str, clock: Clock
):
    """Given a piece whose prompt starts with an option of Claude Code's and holds quotes, a line
    `Tools:`, words beyond ASCII, and a blank line, and whose tools hold a rule with a comma and a
    space inside its parentheses
    When runner.py runs with what `line` gives
    Then Claude Code's run takes that prompt on its standard input and those tools, each whole"""
    tools = ("Read", "Bash(python3 -c 'print(1, 2)')")
    piece, _ = handed_over(repo, PROMPT_AS_OPTIONS, tools)
    claude_double.plays(stand_in, {"1": [{"kind": "ends"}]})
    args, stdin = line(piece)
    main(args[2:], stdin)
    (call,) = claude_double.calls(stand_in)
    assert (call["stdin"], call["tools"]) == (PROMPT_AS_OPTIONS, list(tools))


@pytest.mark.supports("test_a_piece_goes_on_after_the_session_that_handed_it_over_closes")
@pytest.mark.parametrize("more", [False, True], ids=["no standard input", "an argument more"])
def test_main_of_what_line_doesnt_give_is_refused_and_runs_nothing(
    repo: str, stand_in: str, more: bool
):
    """Given the walkthrough's piece recorded running
    When runner.py runs with the arguments that `line` gives and no standard input, or with one
    argument more than `line` gives
    Then it gives 2, printing nothing, with words of what's wrong; Claude Code never runs, and the
    record stays running"""
    piece, handed = handed_over(repo)
    args, stdin = line(piece)
    code, out, err = main([*args[2:], "extra"], stdin) if more else main(args[2:], "")
    assert (code, out) == (2, "")
    assert err.strip()
    assert claude_double.calls(stand_in) == []
    assert read(repo) == [Record(handed, "running", identify(os.getpid()), (), "")]
