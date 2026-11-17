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
from adapters import (
    AdapterFailed,
    KeptResult,
    NoWork,
    Running,
    StartText,
    kept_results,
    start_text,
)
from answers import cant_check, due, ended_unheld, gave, picked_up, stopped
from form import Move
from lanes.kind import Broken, CantCheck
from runs import Due, Left, Result
from script_calls import result_args, result_command

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
    assert isinstance(given, StartText)
    assert given.text.startswith("Carry out your steps") and text in given.text
    assert given.values == {}


@pytest.mark.supports("test_an_adapter_gives_each_start_its_text_and_values")
def test_an_adapter_is_handed_the_role_and_each_start_that_runs(tmp_path: Any) -> None:
    """Given: an adapter that gives back what it's handed, and writer's Start running.
    When: start_text asks it for reviewer's text in the folder tally.
    Then: the adapter got reviewer as its one argument, `{"running": [...]}` on standard input, and
    tally as its folder, and its values come back."""
    os.makedirs(tmp_path / "tally")
    running = (Running("writer", "Write 0.2.0", {"version": "0.2.0"}),)
    given = start_text(program(tmp_path, ECHO), "reviewer", running, "", str(tmp_path / "tally"))
    assert isinstance(given, StartText)
    args, handed, cwd = json.loads(given.text)
    assert args == ["reviewer"]
    assert handed == {
        "running": [{"role": "writer", "text": "Write 0.2.0", "values": {"version": "0.2.0"}}]
    }
    assert os.path.realpath(cwd) == os.path.realpath(tmp_path / "tally")
    assert given.values == {"version": "0.2.0"}


@pytest.mark.supports("test_a_start_no_work_waits_for_is_left_out_and_the_turn_ends")
def test_an_adapter_that_prints_none_gives_why_no_work_waits(tmp_path: Any) -> None:
    """Given: an adapter that prints `{"none": "0.2.0 waits for your approval"}`.
    When: start_text asks it for writer's text.
    Then: it gives NoWork with that why."""
    path = program(tmp_path, 'print(\'{"none": "0.2.0 waits for your approval"}\')\n')
    given = start_text(path, "writer", (), "", str(tmp_path))
    assert given == NoWork("0.2.0 waits for your approval")


@pytest.mark.supports("test_an_adapter_that_fails_at_a_later_move_gives_why_and_who")
@pytest.mark.parametrize(
    "text",
    [
        "import sys\nsys.exit('no version')\n",
        "print('not json')\n",
        "print('{\"values\": {}}')\n",
        "print('{\"none\": 3}')\n",
        "print('[]')\n",
        'print(\'{"text": "Write", "values": {"version": 2}}\')\n',
    ],
    ids=[
        "exits 1",
        "prints what isn't JSON",
        "prints no text",
        "prints a none that isn't text",
        "prints what isn't an object",
        "prints a value that isn't text",
    ],
)
def test_an_adapter_that_fails_or_strays_from_its_form_is_refused(tmp_path: Any, text: str) -> None:
    """Given: an adapter that exits 1, or prints what isn't its form.
    When: start_text asks it for writer's text.
    Then: it raises AdapterFailed."""
    with pytest.raises(AdapterFailed):
        start_text(program(tmp_path, text), "writer", (), "", str(tmp_path))


@pytest.mark.supports("test_an_adapter_of_records_that_fails_stops_the_command")
def test_an_adapter_that_cant_run_is_refused(tmp_path: Any) -> None:
    """Given: an adapter's path where no program lies.
    When: start_text asks it for writer's text.
    Then: it raises AdapterFailed, naming the path."""
    with pytest.raises(AdapterFailed, match="missing.py"):
        start_text(str(tmp_path / "missing.py"), "writer", (), "", str(tmp_path))


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


@pytest.mark.supports("test_no_kept_results_start_a_new_run")
def test_an_adapter_of_records_may_give_none(tmp_path: Any) -> None:
    """Given: an adapter of records that prints no results.
    When: kept_results asks it.
    Then: it gives none."""
    assert kept_results(program(tmp_path, "print('{\"results\": []}')\n"), "", str(tmp_path)) == ()


@pytest.mark.supports("test_an_adapter_of_records_that_fails_stops_the_command")
def test_an_adapter_of_records_that_fails_is_refused(tmp_path: Any) -> None:
    """Given: an adapter of records that exits 1 with why.
    When: kept_results asks it.
    Then: it raises AdapterFailed, with the adapter's why."""
    path = program(tmp_path, "import sys\nsys.exit('records.jsonl is not JSON')\n")
    with pytest.raises(AdapterFailed, match="records.jsonl is not JSON"):
        kept_results(path, "", str(tmp_path))


@pytest.mark.supports("test_an_adapter_of_records_that_fails_stops_the_command")
@pytest.mark.parametrize(
    "text",
    [
        "print('{}')\n",
        'print(\'{"results": {"role": "writer", "result": "written"}}\')\n',
        'print(\'{"results": ["written"]}\')\n',
        'print(\'{"results": [{"role": "writer"}]}\')\n',
        'print(\'{"results": [{"role": "writer", "result": 2}]}\')\n',
    ],
    ids=[
        "prints no results",
        "prints results that aren't a list",
        "prints a result that isn't an object",
        "prints a result with no result",
        "prints a result that isn't text",
    ],
)
def test_an_adapter_of_records_that_strays_from_its_form_is_refused(
    tmp_path: Any, text: str
) -> None:
    """Given: an adapter of records that prints what isn't its form.
    When: kept_results asks it.
    Then: it raises AdapterFailed, naming the form of `results`."""
    with pytest.raises(AdapterFailed, match="`results` must be a list"):
        kept_results(program(tmp_path, text), "", str(tmp_path))


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


WAITING = "0.2.0 waits for your approval"


def left(role: str) -> Left:
    """The start of the role, left out of the moves due as no work waits for it."""
    return Left(Move("start", role=role), WAITING)


def said_with_why(words: str, role: str) -> bool:
    """Whether the words give why in place of the role's start, and not its start."""
    return (
        WAITING in words
        and f"`changelog:{role}`" in words
        and f"Start `changelog:{role}`" not in words
    )


@pytest.mark.supports("test_a_start_no_work_waits_for_is_left_out_and_the_turn_ends")
def test_a_start_left_out_is_said_with_why_in_its_place() -> None:
    """Given: writer's start left out, as no work waits for it, with why.
    When: due gives its words for changelog.
    Then: they open with the plugin's name, and give why in place of writer's start."""
    words = due("changelog", (left("writer"),))
    assert words.startswith("changelog: ") and said_with_why(words, "writer")


@pytest.mark.supports("test_a_start_no_work_waits_for_is_left_out_and_the_turn_ends")
def test_a_start_left_out_beside_a_start_due_is_said_with_both() -> None:
    """Given: writer's start left out, with why, and reviewer's start due.
    When: due gives its words for changelog.
    Then: they give why in place of writer's start, and reviewer's start with its text."""
    words = due("changelog", (left("writer"), d.due_start("reviewer")))
    assert said_with_why(words, "writer")
    assert "Start `changelog:reviewer` with `Carry out your steps`." in words


@pytest.mark.supports("test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run")
def test_a_resume_due_is_said_with_sendmessage() -> None:
    """Given: writer's resume due.
    When: due gives its words for changelog.
    Then: they read ``changelog: Resume `changelog:writer` by SendMessage.``."""
    resume = Due(Move("resume", role="writer"), "", {})
    assert due("changelog", (resume,)) == "changelog: Resume `changelog:writer` by SendMessage."


@pytest.mark.supports("test_a_new_conversation_picks_up_from_the_kept_results")
def test_a_pick_up_is_said_with_each_result_kept_and_the_moves_due() -> None:
    """Given: writer's `written` and reviewer's `more` picked up, and writer's start due.
    When: picked_up gives its words.
    Then: they name both Results in order, and on the next line writer's start."""
    results = (Result("writer", "written"), Result("reviewer", "more"))
    assert picked_up("changelog", results, (d.due_start("writer"),)) == (
        "changelog: The run picks up after writer gave `written`, then reviewer gave `more`.\n"
        "changelog: Start `changelog:writer` with `Carry out your steps`."
    )


@pytest.mark.supports("test_a_start_no_work_waits_for_after_a_result_is_said_with_why")
def test_a_result_is_said_with_why_in_place_of_a_start_left_out() -> None:
    """Given: writer's Result `written`, and reviewer's start left out, with why.
    When: gave gives its words.
    Then: they give writer's Result, then why in place of reviewer's start."""
    words = gave("changelog", "writer", "written", (left("reviewer"),))
    assert words.startswith("changelog: writer gave `written`. ")
    assert said_with_why(words, "reviewer")


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_an_end_with_no_result_is_said_with_why_in_place_of_its_start_left_out() -> None:
    """Given: writer, ended by TaskStop, and its start left out, with why.
    When: ended_unheld gives its words.
    Then: they name writer, and give why in place of its start."""
    words = ended_unheld("changelog", "writer", (left("writer"),))
    assert words.startswith("changelog: ") and said_with_why(words, "writer")


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


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_a_check_that_cant_be_made_is_said_with_why_and_who() -> None:
    """Given: a check that couldn't be made, with why, and that the plugin's developer must fix it.
    When: cant_check gives its words.
    Then: they open with the plugin's name, and hold why and who."""
    words = cant_check("changelog", CantCheck("hooks/lanes.json isn't JSON", "run /lane:up"))
    assert words.startswith("changelog: ")
    assert "hooks/lanes.json isn't JSON" in words and "run /lane:up" in words


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
        (f"python3 {ROOT}/hooks/lane/result.py writer 'written", None),
    ],
    ids=[
        "the plugin's result.py",
        "by the root's name",
        "no Result",
        "a word more",
        "another plugin's",
        "and another command",
        "another command",
        "a command shlex can't split",
    ],
)
def test_a_run_of_result_py_names_its_role_and_result(command: str, read: Any) -> None:
    """Given: a Bash command, and changelog's folder.
    When: result_args reads it.
    Then: it gives the role and the Result only for one run of changelog's result.py with two
    arguments."""
    assert result_args(command, ROOT) == read
