"""The unit cases of adapters.py, answers.py, and script_calls.py: a start's text with and without
an adapter, what an adapter is handed, how it fails, and the Kept results it gives; the words of
each answer the guard gives; and the words of a run of lay.py print, lay.py write, and result.py."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import lane_data as d
import pytest
from adapters import AdapterFailed, KeptResult, Running, kept_results, start_text
from answers import cant_check, due, ended_unheld, gave, stopped
from form import Move
from lanes.kind import Broken, CantCheck
from runs import Due
from script_calls import id_line, printed, result_args, result_command, write_args

ECHO = """import json, os, sys
handed = json.load(sys.stdin)
print(json.dumps({"text": json.dumps([sys.argv[1:], handed, os.getcwd()]),
                  "values": {"version": "0.2.0"}}))
"""


def program(tmp_path: Any, text: str) -> str:
    """An executable Python program with the text, as an adapter of the plugin."""
    path = tmp_path / "adapter.py"
    path.write_text(f"#!{sys.executable}\n{text}")
    os.chmod(path, 0o755)
    return str(path)


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
@pytest.mark.parametrize("words, text", [("", "Carry out your steps"), ("0.2.0", "0.2.0")])
def test_with_no_adapter_a_start_takes_lanes_text_and_the_words(words: str, text: str) -> None:
    """Given: no adapter of a start's text, and the words typed after the command, none or 0.2.0.
    When: start_text gives writer's text.
    Then: it is Lane's text, `Carry out your steps`, holding the words typed, with no values."""
    given = start_text(None, "writer", (), words, d.REPO)
    assert given.text.startswith("Carry out your steps") and text in given.text
    assert given.values == {}


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_an_adapter_gives_each_start_its_text_and_values")
def test_an_adapter_is_handed_the_role_and_each_start_that_runs(tmp_path: Any) -> None:
    """Given: an adapter that gives back what it's handed, and writer's Start running.
    When: start_text asks it for reviewer's text in the folder tally.
    Then: the adapter got reviewer as its one argument, `{"running": [...]}` on standard input, and
    tally as its folder, and its values come back."""
    os.makedirs(tmp_path / "tally")
    running = (Running("writer", "Write 0.2.0", {"version": "0.2.0"}),)
    given = start_text(program(tmp_path, ECHO), "reviewer", running, "", str(tmp_path / "tally"))
    args, handed, cwd = json.loads(given.text)
    assert args == ["reviewer"]
    assert handed == {
        "running": [{"role": "writer", "text": "Write 0.2.0", "values": {"version": "0.2.0"}}]
    }
    assert os.path.realpath(cwd) == os.path.realpath(tmp_path / "tally")
    assert given.values == {"version": "0.2.0"}


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_an_adapter_that_fails_at_a_later_move_gives_why_and_who")
@pytest.mark.parametrize(
    "text",
    ["import sys\nsys.exit('no version')\n", "print('not json')\n", "print('{\"values\": {}}')\n"],
    ids=["exits 1", "prints what isn't JSON", "prints no text"],
)
def test_an_adapter_that_fails_or_strays_from_its_form_is_refused(tmp_path: Any, text: str) -> None:
    """Given: an adapter that exits 1, or prints what isn't its form.
    When: start_text asks it for writer's text.
    Then: it raises AdapterFailed."""
    with pytest.raises(AdapterFailed):
        start_text(program(tmp_path, text), "writer", (), "", str(tmp_path))


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_an_adapter_of_records_that_fails_stops_the_command")
def test_an_adapter_that_cant_run_is_refused(tmp_path: Any) -> None:
    """Given: an adapter's path where no program lies.
    When: start_text asks it for writer's text.
    Then: it raises AdapterFailed, naming the path."""
    with pytest.raises(AdapterFailed, match="missing.py"):
        start_text(str(tmp_path / "missing.py"), "writer", (), "", str(tmp_path))


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_a_new_conversation_picks_up_from_the_kept_results")
def test_kept_results_come_in_the_order_the_adapter_gives(tmp_path: Any) -> None:
    """Given: an adapter of records that prints writer's `written` and reviewer's `more`.
    When: kept_results asks it.
    Then: it gives both, in that order."""
    results = [{"role": "writer", "result": "written"}, {"role": "reviewer", "result": "more"}]
    path = program(tmp_path, f"print({json.dumps({'results': results})!r})\n")
    assert kept_results(path, "0.2.0", str(tmp_path)) == (
        KeptResult("writer", "written"),
        KeptResult("reviewer", "more"),
    )


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_the_words_typed_tell_a_new_request_from_a_pick_up")
@pytest.mark.parametrize("words", ["", "0.3.0", "--continue", "-c 0.2.0"])
def test_an_adapter_of_records_gets_the_words_on_standard_input(tmp_path: Any, words: str) -> None:
    """Given: an adapter of records that gives back, as a Result of its own, its arguments and the
    words it got on standard input.
    When: kept_results asks it with words typed after the command: none, a version, or words that
    begin with `-`.
    Then: the adapter got no argument, and `{"words": <the words>}` on standard input."""
    echo = (
        "import json, sys\n"
        "handed = json.load(sys.stdin)\n"
        "result = json.dumps([sys.argv[1:], handed])\n"
        'print(json.dumps({"results": [{"role": "echo", "result": result}]}))\n'
    )
    ((kept,),) = [kept_results(program(tmp_path, echo), words, str(tmp_path))]
    assert json.loads(kept.result) == [[], {"words": words}]


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_no_kept_results_start_a_new_run")
def test_an_adapter_of_records_may_give_none(tmp_path: Any) -> None:
    """Given: an adapter of records that prints no results.
    When: kept_results asks it.
    Then: it gives none."""
    assert kept_results(program(tmp_path, "print('{\"results\": []}')\n"), "", str(tmp_path)) == ()


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_an_adapter_of_records_that_fails_stops_the_command")
def test_an_adapter_of_records_that_fails_is_refused(tmp_path: Any) -> None:
    """Given: an adapter of records that exits 1 with why.
    When: kept_results asks it.
    Then: it raises AdapterFailed, with the adapter's why."""
    path = program(tmp_path, "import sys\nsys.exit('records.jsonl is not JSON')\n")
    with pytest.raises(AdapterFailed, match="records.jsonl is not JSON"):
        kept_results(path, "", str(tmp_path))


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_a_start_due_is_said_as_the_readme_shows() -> None:
    """Given: writer's start due, with Lane's text.
    When: due gives its words for changelog.
    Then: they read ``changelog: Start `changelog:writer` with `Carry out your steps`.``."""
    words = due("changelog", (d.due_start("writer"),))
    assert words == "changelog: Start `changelog:writer` with `Carry out your steps`."


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
@pytest.mark.parametrize(
    "moves, words",
    [
        ((d.due_start("reviewer"),), "Start `changelog:reviewer` with `Carry out your steps`."),
        ((Due(Move("no_more", result="good"), "", {}),), "Start no more subagents."),
    ],
    ids=["a start", "no more"],
)
def test_a_result_is_said_with_the_moves_of_its_route(moves: tuple[Due, ...], words: str) -> None:
    """Given: reviewer's Result, and the moves of its Route: a start, or no more.
    When: gave gives its words.
    Then: they read as the README shows."""
    assert (
        gave("changelog", "reviewer", "good", moves) == f"changelog: reviewer gave `good`. {words}"
    )


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_an_end_with_no_result_is_said_with_the_start_due_again() -> None:
    """Given: writer, ended by TaskStop, and its start due again.
    When: ended_unheld gives its words.
    Then: they name writer, that it gave no Result, and its start due."""
    words = ended_unheld("changelog", "writer", (d.due_start("writer"),))
    assert words.startswith("changelog: ") and "writer" in words
    assert "Start `changelog:writer` with `Carry out your steps`." in words


@pytest.mark.supports("test_a_call_that_breaks_a_lane_gets_its_steps_sentence")
def test_a_stop_is_said_with_the_sentence_and_what_the_role_may_do() -> None:
    """Given: a Broken Lane with its sentence and what writer may do.
    When: stopped gives its words.
    Then: they open with the plugin's name and the sentence, and then say what writer may do."""
    may = "The commands you may run, each word for word: `git log --oneline`."
    broken = Broken(
        d.lane("writer", "agents/writer.md", 2, "run_only"), "Run only `git log --oneline`.", may
    )
    assert stopped("changelog", broken) == f"changelog: Run only `git log --oneline`.\n{may}"


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_a_check_that_cant_be_made_is_said_with_why_and_who() -> None:
    """Given: a check that couldn't be made, with why, and that the plugin's developer must fix it.
    When: cant_check gives its words.
    Then: they open with the plugin's name, and hold why and who."""
    words = cant_check("changelog", CantCheck("hooks/lanes.json isn't JSON", "run /lane:up"))
    assert words.startswith("changelog: ")
    assert "hooks/lanes.json isn't JSON" in words and "run /lane:up" in words


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_the_id_line_names_the_id() -> None:
    """Given: the ID b9fd8fd8.
    When: id_line gives print's line of it.
    Then: it reads `ID: b9fd8fd8`."""
    assert id_line("b9fd8fd8") == "ID: b9fd8fd8"


@pytest.mark.supports("test_what_print_showed_is_kept_in_ups_run")
def test_a_run_of_print_gives_its_id_and_words() -> None:
    """Given: a Bash command that ran lay.py print, and its output ending with the ID line.
    When: printed reads them.
    Then: it gives the ID, and the whole output."""
    output = "Routes of write, laid on its step 1:\n...\nID: b9fd8fd8\nReply yes to lay these.\n"
    command = "python3 /lane/scripts/lay.py print changelog < /tmp/proposal.json"
    assert printed(command, output) == ("b9fd8fd8", output)


@pytest.mark.supports("test_what_print_showed_is_kept_in_ups_run")
@pytest.mark.parametrize(
    "command, output",
    [
        ("python3 /lane/scripts/lay.py steps changelog", "ID: b9fd8fd8\n"),
        ("python3 /lane/scripts/lay.py print changelog", "Lane x: not a lane type\n"),
        ("git log --oneline", "ID: b9fd8fd8\n"),
    ],
    ids=["steps", "print with no ID", "another command"],
)
def test_what_isnt_a_shown_proposal_gives_none(command: str, output: str) -> None:
    """Given: another command of lay.py, a print whose output names no ID, or another command.
    When: printed reads them.
    Then: it gives None."""
    assert printed(command, output) is None


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_the_result_command_names_the_role_and_its_result() -> None:
    """Given: writer and its Result `written`.
    When: result_command gives the command by which writer gives it.
    Then: it reads as the README's walkthrough lays it."""
    command = result_command("writer", "written")
    assert command == "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written"


ROOT = "/home/you/tally/changelog"


@pytest.mark.supports("test_a_result_is_added_for_the_subagents_start")
@pytest.mark.parametrize(
    "command, read",
    [
        (f"python3 {ROOT}/hooks/lane/result.py writer written", ("writer", "written")),
        ("python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py write good", ("write", "good")),
        (f"python3 {ROOT}/hooks/lane/result.py writer", None),
        (f"python3 {ROOT}/hooks/lane/result.py writer written more", None),
        ("python3 /other/hooks/lane/result.py writer written", None),
        (f"python3 {ROOT}/hooks/lane/result.py writer written && rm CHANGELOG.md", None),
        ("git log --oneline", None),
    ],
    ids=[
        "the plugin's result.py",
        "by the root's name",
        "no Result",
        "a word more",
        "another plugin's",
        "and another command",
        "another command",
    ],
)
def test_a_run_of_result_py_names_its_role_and_result(command: str, read: Any) -> None:
    """Given: a Bash command, and changelog's folder.
    When: result_args reads it.
    Then: it gives the role and the Result only for one run of changelog's result.py with two
    arguments."""
    assert result_args(command, ROOT) == read


@pytest.mark.supports("test_lay_before_the_persons_reply_is_stopped")
@pytest.mark.parametrize(
    "words, read",
    [
        (["/lane/scripts/lay.py", "write", "changelog", "b9fd8fd8"], ("changelog", "b9fd8fd8")),
        (["/lane/scripts/lay.py", "write", "changelog"], None),
        (["/lane/scripts/lay.py", "write", "changelog", "b9fd8fd8", "more"], None),
        (["/lane/scripts/lay.py", "print", "changelog"], None),
        (["/other/write.py", "write", "changelog", "b9fd8fd8"], None),
    ],
    ids=["write", "no ID", "a word more", "print", "another script"],
)
def test_a_call_of_write_names_its_plugin_and_id(words: list[str], read: Any) -> None:
    """Given: the words of a command, from the script on.
    When: write_args reads them.
    Then: it gives the plugin and the ID only for `lay.py write <plugin> <ID>`."""
    assert write_args(words) == read
