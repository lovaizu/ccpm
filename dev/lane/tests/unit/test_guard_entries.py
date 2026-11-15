"""The unit cases of guard.py and of the entries that Claude Code and up run, hook.py, result.py,
and lay.py's command line, through `guard.handle`, `hook.main`, `result.main`, and
`command.main`: an event in and outside a Run, a lanes.json the guard can't read, each exit code
that result.py and lay.py give, and each call that they refuse."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
from typing import Any

import lane_data as d
import pytest
from events import NotAnEvent
from form import write_lanes
from guard import handle
from lay.command import main as lay_main
from run_record import Called, Started, Tied, add, lines, record_path

LANE = os.path.join(os.path.dirname(d.__file__), *[".."] * 3, "plugins", "lane")


def entry(name: str) -> Any:
    """The module of one of Lane's entries in hooks/lane/, by its file's name."""
    path = os.path.join(LANE, "hooks", "lane", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"lane_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def plugin(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """changelog's folder, with its plugin.json and hooks/, and the system's temporary folder set to
    the case's own."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    os.makedirs(tmp_path / "temp")
    os.makedirs(tmp_path / "changelog" / ".claude-plugin")
    os.makedirs(tmp_path / "changelog" / "hooks")
    (tmp_path / "changelog" / ".claude-plugin" / "plugin.json").write_text('{"name": "changelog"}')
    return str(tmp_path / "changelog")


def laid(plugin: str) -> str:
    """Writes the walkthrough's lanes.json into the plugin, and gives its run record's path."""
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), d.lanes_file())
    return record_path("changelog", d.SESSION)


@pytest.mark.supports("test_calls_outside_the_run_go_unchecked")
def test_an_event_outside_every_run_goes_and_adds_nothing(plugin: str) -> None:
    """Given: changelog laid, and a conversation with no Run.
    When: handle answers the main conversation's Bash call `git status`.
    Then: it doesn't stop it, says nothing, and adds nothing to the run record."""
    path = laid(plugin)
    event = d.event("PreToolUse", tool_name="Bash", tool_input={"command": "git status"})
    answer = handle(event, plugin)
    assert (answer.stop, answer.words) == (False, "")
    assert lines(path) == ()


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_a_skills_call_adds_a_run_and_gives_the_first_start(plugin: str) -> None:
    """Given: changelog laid, and a conversation with no Run.
    When: handle answers the UserPromptExpansion of /changelog:write.
    Then: it adds the call of write's Run by a person, and gives writer's start due."""
    path = laid(plugin)
    event = d.event("UserPromptExpansion", command_name="changelog:write", command_args="")
    answer = handle(event, plugin)
    assert not answer.stop
    assert answer.words == "changelog: Start `changelog:writer` with `Carry out your steps`."
    ((called,),) = [[line for line in lines(path) if isinstance(line, Called)]]
    assert (called.skill, called.by) == ("write", "person")


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_an_event_with_lanes_json_unreadable_is_stopped_with_who_must_fix_it(plugin: str) -> None:
    """Given: changelog whose hooks/lanes.json isn't JSON, and write's Run with writer tied to
    a01.
    When: handle answers a01's Bash call.
    Then: it stops the call, saying lanes.json can't be read and who must fix it."""
    path = record_path("changelog", d.SESSION)
    for line in (
        Called("r1", "write", "person", ""),
        Started("r1", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
    ):
        add(path, line)
    with open(os.path.join(plugin, "hooks", "lanes.json"), "w", encoding="utf-8") as f:
        f.write("{")
    event = d.event("PreToolUse", agent_id="a01", tool_name="Bash", tool_input={"command": "ls"})
    answer = handle(event, plugin)
    assert answer.stop and "lanes.json" in answer.words


def writer_tied(plugin: str) -> str:
    """changelog laid, and write's Run with writer's Start tied to a01; gives the record's path."""
    path = laid(plugin)
    for line in (
        Called("r1", "write", "person", ""),
        Started("r1", "writer", "Carry out your steps", {}, "t1", False),
        Tied("r1", "t1", "a01"),
    ):
        add(path, line)
    return path


def end(plugin: str) -> str:
    """The stop of writer's end, its result script named by the plugin's folder, as the README
    shows a stop."""
    return f"changelog: End by running `python3 {plugin}/hooks/lane/result.py writer written`."


@pytest.mark.supports("test_a_subagents_start_of_a_role_is_stopped")
def test_a_subagents_start_of_a_role_is_stopped_with_its_last_lanes_sentence(plugin: str) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01.
    When: handle answers a01's Agent call of changelog:reviewer.
    Then: it stops the start with the sentence of the Lane on writer's last Step, and adds no
    Start."""
    path = writer_tied(plugin)
    tool_input = {"subagent_type": "changelog:reviewer", "prompt": "Carry out your steps"}
    event = d.event(
        "PreToolUse", agent_id="a01", tool_name="Agent", tool_input=tool_input, tool_use_id="t2"
    )
    answer = handle(event, plugin)
    assert answer.stop and answer.words == end(plugin)
    assert [x for x in lines(path) if isinstance(x, Started)] == [
        Started("r1", "writer", "Carry out your steps", {}, "t1", False)
    ]


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence")
def test_a_subagents_end_with_no_result_is_stopped_with_its_last_lanes_sentence(
    plugin: str,
) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01, which gave no
    Result.
    When: handle answers a01's SubagentStop.
    Then: it stops the end with the sentence of the Lane on writer's last Step."""
    writer_tied(plugin)
    event = d.event(
        "SubagentStop", agent_id="a01", agent_type="changelog:writer", last_message="Done."
    )
    answer = handle(event, plugin)
    assert answer.stop and answer.words == end(plugin)


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_the_hook_refuses_what_isnt_an_event(plugin: str) -> None:
    """Given: standard input that isn't JSON.
    When: hook.py's main reads it.
    Then: it raises NotAnEvent, so the hook fails and its entry's onFailure stops the call."""
    with pytest.raises(NotAnEvent):
        entry("hook").main("not json", plugin)


@pytest.mark.supports("test_calls_outside_the_run_go_unchecked")
def test_the_hook_answers_an_event_outside_every_run_with_nothing(plugin: str) -> None:
    """Given: changelog laid, and a conversation with no Run.
    When: hook.py's main answers the main conversation's PreToolUse of `git status`.
    Then: it exits 0 and denies nothing."""
    laid(plugin)
    text = d.payload("PreToolUse", tool_name="Bash", tool_input={"command": "git status"})
    out = entry("hook").main(text, plugin)
    assert out.code == 0 and "deny" not in out.stdout


@pytest.mark.supports("test_a_result_the_role_may_not_give_is_refused")
@pytest.mark.parametrize(
    "result, code", [("written", 0), ("good", 1)], ids=["one it may give", "one it may not"]
)
def test_result_py_takes_only_a_result_the_role_may_give(
    plugin: str, result: str, code: int
) -> None:
    """Given: changelog laid, and write's Run with writer's Start tied to a01.
    When: result.py's main takes writer's `written`, or `good`.
    Then: it gives 0 for `written`, and 1 with `written` as what writer may give for `good`."""
    writer_tied(plugin)
    env = {"CLAUDE_CODE_SESSION_ID": d.SESSION}
    given, out, err = entry("result").main(["writer", result], env, plugin)
    assert given == code
    if code:
        assert "written" in out + err


@pytest.mark.supports("test_a_result_the_role_may_not_give_is_refused")
@pytest.mark.parametrize(
    "argv, env",
    [
        (["writer"], {"CLAUDE_CODE_SESSION_ID": d.SESSION}),
        (["writer", "written", "more"], {"CLAUDE_CODE_SESSION_ID": d.SESSION}),
        (["writer", "written"], {}),
    ],
    ids=["one argument", "three arguments", "no session"],
)
def test_result_py_refuses_a_call_it_cant_read(
    plugin: str, argv: list[str], env: dict[str, str]
) -> None:
    """Given: changelog laid.
    When: result.py's main takes other than two arguments, or no CLAUDE_CODE_SESSION_ID.
    Then: it gives 2 with why."""
    laid(plugin)
    code, _, err = entry("result").main(argv, env, plugin)
    assert code == 2 and err


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_result_py_without_lanes_json_gives_2(plugin: str) -> None:
    """Given: changelog with no hooks/lanes.json.
    When: result.py's main takes writer's `written`.
    Then: it gives 2, naming lanes.json."""
    code, _, err = entry("result").main(
        ["writer", "written"], {"CLAUDE_CODE_SESSION_ID": d.SESSION}, plugin
    )
    assert code == 2 and "lanes.json" in err


@pytest.mark.supports("test_types_give_each_lane_type_and_the_form_of_a_proposal")
def test_lay_types_gives_the_types_and_the_form(plugin: str) -> None:
    """Given: Lane's folder.
    When: lay.py's main runs `types`.
    Then: it gives 0 with JSON of each type and the Proposal's form."""
    code, out, _ = lay_main(["types"], io.StringIO(""), {}, LANE)
    given = json.loads(out)
    assert code == 0 and given["proposal"]["required"] == ["lanes", "routes", "adapters"]
    assert "ends_by_result" in {each["name"] for each in given["types"]}


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_lay_steps_gives_the_steps_and_notes(tmp_path: Any) -> None:
    """Given: a copy of the walkthrough's changelog.
    When: lay.py's main runs `steps` on it.
    Then: it gives 0 with JSON of seven Steps and no notes."""
    import walkthrough

    walkthrough.write_files(str(tmp_path / "changelog"), walkthrough.FILES)
    code, out, _ = lay_main(["steps", str(tmp_path / "changelog")], io.StringIO(""), {}, LANE)
    given = json.loads(out)
    assert code == 0 and len(given["steps"]) == 7 and given["notes"] == []


@pytest.mark.supports("test_a_proposal_that_cant_stand_goes_back_to_up")
def test_lay_print_of_a_proposal_out_of_form_gives_1(tmp_path: Any) -> None:
    """Given: a copy of the walkthrough's changelog.
    When: lay.py's main runs `print` with standard input that isn't JSON.
    Then: it gives 1 with what's wrong."""
    import walkthrough

    walkthrough.write_files(str(tmp_path / "changelog"), walkthrough.FILES)
    code, out, err = lay_main(["print", str(tmp_path / "changelog")], io.StringIO("{"), {}, LANE)
    assert code == 1 and (out + err)


@pytest.mark.supports("test_lay_of_an_id_no_proposal_has_is_refused")
@pytest.mark.parametrize(
    "argv",
    [[], ["lay"], ["steps"], ["write", "changelog"], ["types", "more"]],
    ids=[
        "nothing",
        "an unknown command",
        "steps with no plugin",
        "write with no ID",
        "a word more",
    ],
)
def test_lay_refuses_a_command_line_it_cant_read(argv: list[str]) -> None:
    """Given: Lane's folder.
    When: lay.py's main runs a command line that isn't one of its commands.
    Then: it gives 2 with how to call lay.py."""
    code, _, err = lay_main(argv, io.StringIO(""), {}, LANE)
    assert code == 2 and "lay.py" in err
