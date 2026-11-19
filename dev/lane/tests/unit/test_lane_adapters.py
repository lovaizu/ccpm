"""The unit cases of hooks/lane/adapters.py: start_text, checklist, and kept_results, one for each
class of what a plugin's adapter gives: its output in the form of its schema, no adapter, an adapter
that fails, and output out of its form; with what Lane gives the adapter on its standard input, and
the folder it runs in."""

from __future__ import annotations

import json
import os

import lane_bench
import pytest
from adapters import AdapterFailed, checklist, kept_results, start_text
from record import Run
from repo_files import write_files
from routes import Due

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")

RUN = Run("r1", "session-1", "log:up", "1.2.0", None, [])
# An adapter that writes what it was given and the folder it runs in beside the conversation's
# files, and prints the output given.
ECHO = """\
import json, os, sys

with open("given.json", "w") as f:
    json.dump({{"input": json.load(sys.stdin), "cwd": os.getcwd()}}, f)
print({printed!r})
"""


def adapter(log: str, name: str, code: str | None) -> None:
    """Writes the adapter of `log`, or removes it where the code is None."""
    if code is None:
        os.remove(os.path.join(log, "lane", "adapters", name))
    else:
        write_files(log, {f"lane/adapters/{name}": code})


def given(cwd: str) -> dict[str, object]:
    """What the echoing adapter was given, and the folder it ran in."""
    with open(os.path.join(cwd, "given.json"), encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.supports("test_what_only_the_plugin_knows_comes_from_its_adapter")
def test_a_start_adapter_gives_the_text_of_the_start_due(log: str, cwd: str):
    """Given `log`'s start adapter
    When Lane asks it for the text of the writer due in the run for 1.2.0
    Then it gives the text that the adapter prints"""
    text = start_text(log, cwd, RUN, Due("log:writer"))
    assert text == lane_bench.text("log:writer")


@pytest.mark.supports("test_what_only_the_plugin_knows_comes_from_its_adapter")
def test_a_start_adapter_takes_the_run_and_the_role_in_the_conversations_folder(log: str, cwd: str):
    """Given a start adapter that writes what it's given
    When Lane asks it for the text of the writer due
    Then it was given the run's skill and words and the role, as start.in.schema.json says, and
    ran in the conversation's folder"""
    adapter(log, "start.py", ECHO.format(printed=json.dumps({"text": "Write it."})))
    start_text(log, cwd, RUN, Due("log:writer"))
    assert given(cwd) == {
        "input": {"run": {"skill": "log:up", "words": "1.2.0"}, "role": "log:writer"},
        "cwd": os.path.realpath(cwd),
    }


@pytest.mark.supports("test_a_plugin_without_a_start_adapter_gets_the_role_due_alone")
def test_a_plugin_without_a_start_adapter_gives_no_text(log: str, cwd: str):
    """Given `log` with no start adapter
    When Lane asks for the text of the writer due
    Then there's none"""
    adapter(log, "start.py", None)
    assert start_text(log, cwd, RUN, Due("log:writer")) is None


@pytest.mark.supports("test_a_start_adapter_that_fails_stops_with_the_adapter_and_what_it_said")
def test_a_start_adapter_that_fails_is_refused_with_its_file_and_what_it_said(log: str, cwd: str):
    """Given a start adapter that exits 1 saying it found no version
    When Lane asks it for the text of the writer due
    Then it refuses with AdapterFailed naming start.py and what it said"""
    adapter(log, "start.py", "import sys\n\nsys.exit('no version found')\n")
    with pytest.raises(AdapterFailed) as raised:
        start_text(log, cwd, RUN, Due("log:writer"))
    assert "start.py" in str(raised.value)
    assert "no version found" in str(raised.value)


@pytest.mark.supports("test_a_start_adapters_output_out_of_its_form_stops_naming_the_adapter")
@pytest.mark.parametrize("printed", ["Write it.", '{"words": "Write it."}', '{"text": ""}'])
def test_a_start_adapters_output_out_of_its_form_is_refused(log: str, cwd: str, printed: str):
    """Given a start adapter that prints text that isn't JSON, an object with no `text`, or an
    empty `text`
    When Lane asks it for the text of the writer due
    Then it refuses with AdapterFailed naming start.py"""
    adapter(log, "start.py", f"print({printed!r})\n")
    with pytest.raises(AdapterFailed) as raised:
        start_text(log, cwd, RUN, Due("log:writer"))
    assert "start.py" in str(raised.value)


@pytest.mark.supports("test_a_step_marked_before_its_items_names_each_item_not_done")
def test_a_checklist_adapter_gives_the_items_of_the_step(log: str, cwd: str):
    """Given `log`'s checklist adapter
    When Lane asks it for the items of the writer's step `write`
    Then it gives `dated` and `linked`, in order"""
    assert checklist(log, cwd, RUN, "log:writer", "write") == ["dated", "linked"]


@pytest.mark.supports("test_a_step_marked_once_each_item_is_done_holds")
def test_a_checklist_adapter_may_give_no_item(log: str, cwd: str):
    """Given `log`'s checklist adapter
    When Lane asks it for the items of the writer's step `report`
    Then it gives none"""
    assert checklist(log, cwd, RUN, "log:writer", "report") == []


@pytest.mark.supports("test_a_step_marked_before_its_items_names_each_item_not_done")
def test_a_checklist_adapter_takes_the_run_the_role_and_the_step(log: str, cwd: str):
    """Given a checklist adapter that writes what it's given
    When Lane asks it for the items of the writer's step `write`
    Then it was given the run, the role, and the step, as checklist.in.schema.json says"""
    adapter(log, "checklist.py", ECHO.format(printed=json.dumps({"items": []})))
    checklist(log, cwd, RUN, "log:writer", "write")
    assert given(cwd)["input"] == {
        "run": {"skill": "log:up", "words": "1.2.0"},
        "role": "log:writer",
        "step": "write",
    }


@pytest.mark.supports("test_a_checklist_rule_with_no_checklist_adapter_says_what_to_mend")
def test_a_plugin_without_a_checklist_adapter_is_refused(log: str, cwd: str):
    """Given `log` with no checklist adapter
    When Lane asks for the items of the writer's step `write`
    Then it refuses with AdapterFailed naming checklist.py"""
    adapter(log, "checklist.py", None)
    with pytest.raises(AdapterFailed) as raised:
        checklist(log, cwd, RUN, "log:writer", "write")
    assert "checklist.py" in str(raised.value)


@pytest.mark.supports("test_a_step_marked_before_its_items_names_each_item_not_done")
@pytest.mark.parametrize("printed", ['{"items": "dated"}', '{"items": [""]}', "[]"])
def test_a_checklist_adapters_output_out_of_its_form_is_refused(log: str, cwd: str, printed: str):
    """Given a checklist adapter that prints items that aren't a list, an empty item, or no
    object
    When Lane asks it for the items of the writer's step `write`
    Then it refuses with AdapterFailed"""
    adapter(log, "checklist.py", f"print({printed!r})\n")
    with pytest.raises(AdapterFailed):
        checklist(log, cwd, RUN, "log:writer", "write")


@pytest.mark.supports("test_a_new_conversation_picks_the_run_up_from_the_kept_results")
def test_a_kept_adapter_gives_the_results_kept_in_their_order(log: str, cwd: str):
    """Given `log` keeping the writer's `written` and the reviewer's `more` for 1.2.0
    When Lane asks its kept adapter for the results of log:up with 1.2.0
    Then it gives both, in their order"""
    kept = [
        {"role": "log:writer", "result": "written"},
        {"role": "log:reviewer", "result": "more"},
    ]
    write_files(cwd, {".log/kept/1.2.0.json": json.dumps(kept)})
    assert kept_results(log, cwd, "log:up", "1.2.0") == kept


@pytest.mark.supports("test_the_kept_adapter_is_asked_with_the_words_typed_after_the_command")
def test_a_kept_adapter_takes_the_skill_and_the_words(log: str, cwd: str):
    """Given a kept adapter that writes what it's given
    When Lane asks it for the results of log:up with 1.3.0
    Then it was given the skill and the words, as kept.in.schema.json says"""
    adapter(log, "kept.py", ECHO.format(printed=json.dumps({"results": []})))
    kept_results(log, cwd, "log:up", "1.3.0")
    assert given(cwd)["input"] == {"run": {"skill": "log:up", "words": "1.3.0"}}


@pytest.mark.supports("test_a_plugin_without_a_kept_adapter_starts_the_run_from_its_command")
def test_a_plugin_without_a_kept_adapter_gives_no_results(log: str, cwd: str):
    """Given `log` with no kept adapter
    When Lane asks for the results kept of log:up with 1.2.0
    Then there's none"""
    adapter(log, "kept.py", None)
    assert kept_results(log, cwd, "log:up", "1.2.0") is None


@pytest.mark.supports("test_a_kept_adapter_that_fails_stops_with_the_adapter_and_what_it_said")
@pytest.mark.parametrize(
    "code",
    [
        "import sys\n\nsys.exit('the kept file is broken')\n",
        'print(\'{"results": [{"role": "log:writer"}]}\')\n',
    ],
)
def test_a_kept_adapter_that_fails_or_gives_out_of_form_is_refused(log: str, cwd: str, code: str):
    """Given a kept adapter that exits 1, or gives a result with no `result`
    When Lane asks it for the results of log:up with 1.2.0
    Then it refuses with AdapterFailed naming kept.py"""
    adapter(log, "kept.py", code)
    with pytest.raises(AdapterFailed) as raised:
        kept_results(log, cwd, "log:up", "1.2.0")
    assert "kept.py" in str(raised.value)
