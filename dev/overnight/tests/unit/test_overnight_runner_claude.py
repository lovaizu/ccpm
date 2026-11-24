"""The unit cases of runner/claude.py, how Claude Code is run for a piece: `run`, first and resumed,
of one tool and several, of tools whose rules hold spaces and commas, of a prompt of several lines,
of a run that Claude Code ends with an error, and where `claude` can't be found."""

from __future__ import annotations

import json
import os
from typing import Any

import overnight_stand_ins
import pytest
from claude_code import claude_double
from claude_code.claude_double import RUN
from overnight_files import PROMPT, PROMPT_AS_OPTIONS, TOOLS, piece_folder
from runner.carry import Piece
from runner.claude import Output, run

pytestmark = pytest.mark.xfail(strict=True, reason="runner.claude isn't built yet")


def piece(tmp_path: Any, tools: tuple[str, ...] = TOOLS, prompt: str = PROMPT) -> Piece:
    """The walkthrough's piece 1, with the tools and prompt, its folder made."""
    repo = os.path.join(str(tmp_path), "work", "myapp")
    folder = piece_folder(repo, 1)
    os.makedirs(folder, exist_ok=True)
    return Piece(repo, 1, folder, prompt, tools)


def ends(folder: str, last_words: str) -> Output:
    """What the stand-in gives for a run in the folder that ends with the last words."""
    given = claude_double.line(RUN, "a run ends with its last words")
    reply = json.loads(given["stdout"])
    reply["session_id"] = claude_double.conversation(folder)
    reply["result"] = last_words
    return Output(0, json.dumps(reply, separators=(",", ":"), ensure_ascii=False) + "\n", "")


@pytest.mark.supports(
    "test_a_piece_runs_with_the_named_tools_in_a_worktree_of_its_own_made_before_it_starts"
)
def test_a_first_run_asks_no_one_allows_only_the_tools_and_takes_the_prompt(
    tmp_path: Any, stand_in: str
):
    """Given the walkthrough's piece with its five tools, and Claude Code ending its run with
    `Done.`
    When Claude Code is run for it with no conversation
    Then the one run is in the piece's folder, in print mode with JSON output and the mode that
    asks no one, allowing exactly the five tools, resuming no conversation, with the prompt on its
    standard input; and it gives what Claude Code gave"""
    given = piece(tmp_path)
    claude_double.plays(stand_in, {"1": [{"kind": "ends", "last_words": "Done."}]})
    assert run(given, None) == ends(given.folder, "Done.")
    (call,) = claude_double.calls(stand_in)
    asked = {each: call[each] for each in ("cwd", "print", "output", "mode", "tools", "resume")}
    assert asked == {
        "cwd": os.path.realpath(given.folder),
        "print": True,
        "output": "json",
        "mode": "dontAsk",
        "tools": list(TOOLS),
        "resume": None,
    }
    assert call["stdin"] == PROMPT


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
def test_a_run_in_a_conversation_resumes_it(tmp_path: Any, stand_in: str):
    """Given the walkthrough's piece, and Claude Code ending a resumed run with `Went on.`
    When Claude Code is run for it in the conversation of its folder
    Then the one run resumes that conversation, asking no one, with only the five tools and the
    prompt on its standard input, and it gives what Claude Code gave"""
    given = piece(tmp_path)
    conversation = claude_double.conversation(given.folder)
    claude_double.plays(stand_in, {"1": [{"kind": "ends", "last_words": "Went on."}]})
    resumed = run(given, conversation)
    assert (resumed.code, resumed.stderr) == (0, "")
    assert json.loads(resumed.stdout)["result"] == "Went on."
    (call,) = claude_double.calls(stand_in)
    assert (call["resume"], call["mode"], call["tools"]) == (conversation, "dontAsk", list(TOOLS))
    assert call["stdin"] == PROMPT


@pytest.mark.supports(
    "test_a_piece_runs_with_the_named_tools_in_a_worktree_of_its_own_made_before_it_starts"
)
@pytest.mark.parametrize(
    "tools",
    [
        ("Read",),
        ("Bash(git commit -m *)", "Edit"),
        (
            "Bash(python3 -c 'print(1, 2)')",
            "mcp__github__get_issue",
            "WebFetch(domain:docs.python.org)",
        ),
    ],
    ids=["one tool", "a rule that holds spaces", "rules that hold commas, quotes, and colons"],
)
def test_each_tool_named_is_allowed_whole_and_no_other(
    tmp_path: Any, stand_in: str, tools: tuple[str, ...]
):
    """Given a piece whose tools are one, or rules that hold spaces, commas, quotes, or colons
    inside their parentheses
    When Claude Code is run for it
    Then the run allows exactly those tools, each rule whole"""
    claude_double.plays(stand_in, {"1": [{"kind": "ends"}]})
    run(piece(tmp_path, tools), None)
    (call,) = claude_double.calls(stand_in)
    assert call["tools"] == list(tools)


@pytest.mark.supports("test_the_prompt_reaches_claude_code_whole_on_its_standard_input")
def test_a_prompt_that_reads_as_options_reaches_claude_code_whole(tmp_path: Any, stand_in: str):
    """Given a prompt of several lines that starts with an option of Claude Code's, and holds
    quotes, a line `Tools:`, words beyond ASCII, and a blank line
    When Claude Code is run for the piece
    Then the run takes the prompt on its standard input as written, and its options stay those of
    the piece"""
    claude_double.plays(stand_in, {"1": [{"kind": "ends"}]})
    run(piece(tmp_path, prompt=PROMPT_AS_OPTIONS), None)
    (call,) = claude_double.calls(stand_in)
    assert (call["stdin"], call["resume"], call["tools"]) == (PROMPT_AS_OPTIONS, None, list(TOOLS))


@pytest.mark.supports("test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error")
def test_a_run_that_claude_code_ends_with_an_error_gives_its_code_and_words(
    tmp_path: Any, stand_in: str
):
    """Given Claude Code ending the piece's run by an error of its own, its turns run out
    When Claude Code is run for the piece
    Then it gives Claude Code's exit code 1, and its reply whole"""
    claude_double.plays(stand_in, {"1": [{"kind": "errs"}]})
    given = run(piece(tmp_path), None)
    assert (given.code, given.stderr) == (1, "")
    assert json.loads(given.stdout)["errors"] == ["Reached maximum number of turns (1)"]


@pytest.mark.supports(
    "test_a_piece_whose_claude_code_cant_start_is_recorded_failed_with_the_systems_words"
)
def test_a_run_where_claude_isnt_found_gives_a_failing_code_and_the_systems_words(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given a PATH on which no `claude` is found
    When Claude Code is run for the piece
    Then it gives a code other than 0, no standard output, and the system's words, without
    raising"""
    overnight_stand_ins.path_without_claude(monkeypatch)
    given = run(piece(tmp_path), None)
    assert given.code != 0
    assert given.stdout == ""
    assert given.stderr.strip()
