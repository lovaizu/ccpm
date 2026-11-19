"""The integration cases of each principle item of Lane's architecture: each where the parts keep
it, running `log` and Lane through the double of Claude Code, and each with the fixture `broken`,
which takes the part that holds the item out of the bench's copy of Lane where TRACE_BROKEN is 1, as
the plugin guide's A principle's test seen to fail says. A part taken out is an interface given
again at the end of its module, so the copy runs without what holds the item."""

from __future__ import annotations

import os
from collections.abc import Callable

import pytest
from lane_bench import UNREPORTED, WORDS, Bench, opened, started, text, written

pytestmark = UNREPORTED

# A plugin beside `log` that Lane never names either, whose scribe writes only MEMO.md.
MEMO_RULES = {
    "roles": {
        "memo:scribe": {
            "steps": [{"name": "note", "rules": [{"type": "writes", "paths": ["MEMO.md"]}]}]
        }
    },
    "routes": [{"after": {"command": "memo:up"}, "start": ["memo:scribe"]}],
}


def given_again(b: Bench, module: str, code: str) -> None:
    """Gives an interface of the module of the bench's copy of Lane again, at the end of its
    file."""
    with open(os.path.join(b.lane, "hooks", "lane", module), "a", encoding="utf-8") as f:
        f.write("\n\n" + code)


def sentence_left_out(b: Bench) -> None:
    """The rule type of the files a step writes stops a call with no sentence of the step."""
    given_again(
        b,
        "rule_types/writes.py",
        "def judge_call(rule, step, move):\n"
        "    path = move.event['tool_input']['file_path']\n"
        "    names = [os.path.join(move.event['cwd'], p) for p in rule['paths']]\n"
        "    return None if any(path.startswith(n) for n in names) else 'Stopped.'\n"
        "\n\nimport os\n",
    )


def rules_unread(b: Bench) -> None:
    """A plugin's lane/rules.json reads as no rules, whatever its form."""
    given_again(b, "rules.py", "def read_rules(plugin_root):\n    return None\n")


def reply_counts(b: Bench) -> None:
    """The rule type of a role's results takes any end, its reply among them."""
    given_again(b, "rule_types/result.py", "def judge_end(rule, step, move):\n    return None\n")


def folder_unfound(b: Bench) -> None:
    """No plugin's folder is found from the transcript."""
    given_again(b, "plugin.py", "def plugin_root(transcript_path, skill):\n    return None\n")


def adapter_unasked(b: Bench) -> None:
    """The plugin's order is never asked."""
    given_again(b, "adapters.py", "def starts_due(plugin_root, cwd, run, rules):\n    return []\n")


def no_skill_call(b: Bench) -> None:
    """No event reads as a skill's call, so no run is ever added."""
    given_again(b, "place.py", "def skill_call(event):\n    return None\n")


BREAKS: dict[str, Callable[[Bench], None]] = {
    "test_a_stopped_call_gives_the_step_left_and_what_to_do_instead": sentence_left_out,
    "test_rules_out_of_form_stop_the_call_saying_what_the_author_mends": rules_unread,
    "test_a_result_said_only_in_the_reply_counts_for_nothing": reply_counts,
    "test_each_plugins_run_is_held_to_the_rules_in_its_own_folder": folder_unfound,
    "test_what_only_the_plugin_knows_comes_from_its_adapter": adapter_unasked,
    "test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone": no_skill_call,
}


@pytest.fixture
def broken(b: Bench, request: pytest.FixtureRequest) -> None:
    """Takes out the part that holds the case's principle item where TRACE_BROKEN is 1."""
    if os.environ.get("TRACE_BROKEN") == "1":
        BREAKS[request.node.originalname](b)


@pytest.mark.supports("P1.1")
def test_a_stopped_call_gives_the_step_left_and_what_to_do_instead(b: Bench, broken: None):
    """Given the writer running at its step `write`
    When it writes notes.txt
    Then the write is stopped, and the writer reads the step `write` and the files it writes
    instead"""
    answer = started(opened(b)).write(b.at("notes.txt"), "x\n")
    assert answer.blocked
    assert "write" in answer.said
    assert "CHANGELOG.md" in answer.said


@pytest.mark.supports("P1.1")
def test_rules_out_of_form_stop_the_call_saying_what_the_author_mends(b: Bench, broken: None):
    """Given `log` whose lane/rules.json has no routes
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped, saying that Lane can't check the run, the file, and what its form
    lacks, for the plugin's author to mend"""
    b.rules({"roles": {}})
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "lane/rules.json" in answer.said
    assert "routes" in answer.said


@pytest.mark.supports("P1.2")
def test_a_result_said_only_in_the_reply_counts_for_nothing(b: Bench, broken: None):
    """Given the writer that kept each step but ran no reporter of its result
    When it ends replying `written`
    Then the end is stopped, as a result counts only from the AI's own call"""
    writer = started(opened(b))
    written(writer, result=None)
    answer = writer.end("lane-result written")[0]
    assert answer.blocked
    assert "written" in answer.said


@pytest.mark.supports("P2.1")
def test_each_plugins_run_is_held_to_the_rules_in_its_own_folder(b: Bench, broken: None):
    """Given `memo` beside `log`, whose scribe writes only MEMO.md
    When the person types /memo:up, the scribe starts, and it writes CHANGELOG.md
    Then the write is stopped naming MEMO.md, by the rules in memo's own folder"""
    c = b.converse(b.other("memo", MEMO_RULES))
    c.type("/memo:up")
    scribe = c.start("memo:scribe", "Take the memo.", "Take the memo")[1]
    assert scribe is not None
    answer = scribe.write(b.at("CHANGELOG.md"), "x\n")
    assert answer.blocked
    assert "MEMO.md" in answer.said


@pytest.mark.supports("P2.2")
def test_what_only_the_plugin_knows_comes_from_its_adapter(b: Bench, broken: None):
    """Given the person typed /log:up 1.2.0
    When the main conversation ends its turn
    Then it reads the writer due with the text that log's start adapter gives"""
    assert text("log:writer") in opened(b).stop("Started.").said


@pytest.mark.supports("P2.3")
def test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone(b: Bench, broken: None):
    """Given `plain`, a plugin with no lane/rules.json, beside `log`
    When the main conversation writes a file and ends its turn before any skill's call, then the
    person types /plain:up and it ends its turn, then the person types /log:up 1.2.0 and it ends its
    turn
    Then each move before /log:up goes through, and the last end is stopped with the writer due"""
    c = b.converse(b.other("plain", None))
    assert not c.write(None, b.at("notes.txt"), "x\n").blocked
    assert not c.stop("Nothing to do.").blocked
    c.type("/plain:up")
    assert not c.stop("Plain work.").blocked
    c.type(f"/log:up {WORDS}")
    assert c.stop("Started.").blocked
