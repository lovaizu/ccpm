"""The property-based tests of Lane's parts whose contracts take a wide input, as Lane's Test
strategy names them: lay.py's reading of a plugin's Steps and its check of a Proposal, each lane
type's check of a call against the commands and the paths it takes, the guard's reading of each
hook event, and the Run written to its file and read back. Each finds no counterexample, by
hypothesis, and quality.sh runs them in CI."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

import hook
import pytest
import steps
from claude_code import RUN, line
from domain.event import COMMAND, WRITE, Call
from domain.fault import Fault
from domain.laid_set import Laid
from domain.lanes import Where
from domain.lanes.run_only import LANE_TYPE as RUN_ONLY
from domain.lanes.write_only import LANE_TYPE as WRITE_ONLY
from domain.run_record import Result, Start, dumps, loads
from hypothesis import given
from hypothesis import strategies as st
from lane_example import PROPOSAL, put
from lane_parts import run
from proposal import parse

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

WORDS = st.text(st.characters(blacklist_categories=("Cs", "Cc")), min_size=1, max_size=40)
NAMES = st.from_regex(r"[a-z][a-z0-9-]{0,11}", fullmatch=True)
WHERE = Where("/repo", "/repo")


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
@given(st.lists(WORDS.filter(lambda w: "\n" not in w), min_size=1, max_size=8))
def test_each_numbered_step_reads_back_with_its_words(words: list[str]):
    """Given a skill whose `## Steps` lists any one-line words, numbered from 1
    When the plugin's Roles are read
    Then the skill has one Step for each item, its words as written"""
    with tempfile.TemporaryDirectory() as root:
        listed = "\n".join(f"{n}. {w.strip() or 'x'}" for n, w in enumerate(words, 1))
        put(root, ".claude-plugin/plugin.json", '{"name": "p"}')
        put(root, "skills/s/SKILL.md", f"---\nname: s\n---\n\n## Steps\n\n{listed}\n")
        found = {role.name: role for role in steps.roles(root, Laid())}
        assert [s.words for s in found["s"].steps] == listed.split("\n")


@pytest.mark.supports("test_lay_print_refuses_a_proposal_not_in_the_form_of_the_schema")
@given(
    st.recursive(
        st.none() | st.booleans() | st.integers() | WORDS,
        lambda inner: st.lists(inner) | st.dictionaries(WORDS, inner),
        max_leaves=12,
    )
)
def test_any_json_value_parses_as_a_proposal_or_raises_a_fault(value: Any):
    """Given any JSON value
    When it's parsed as a Proposal
    Then it gives a Proposal or raises a Fault, and nothing else"""
    try:
        parse(value, "p.json")
    except Fault:
        pass


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
@given(st.lists(NAMES, min_size=1, max_size=4))
def test_a_proposal_with_any_results_of_reviewer_parses_with_each_route(results: list[str]):
    """Given the walkthrough's Proposal with reviewer giving any results, each with a Route
    When it's parsed
    Then it holds a Route after each"""
    routes = [*PROPOSAL["routes"][:2]] + [
        {"after": f"reviewer {r}", "moves": [{"kind": "no_more"}]} for r in results
    ]
    found = parse(dict(PROPOSAL, routes=routes), "p.json")
    assert {r.after for r in found.routes} >= {f"reviewer {r}" for r in results}


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
@given(st.lists(NAMES, min_size=1, max_size=4), st.lists(NAMES, min_size=1, max_size=4))
def test_a_command_passes_run_only_exactly_when_it_is_one_it_takes(
    taken: list[str], words: list[str]
):
    """Given a run_only Lane that takes any command of plain words
    When the role runs any command of plain words
    Then the call passes exactly where the command is the one taken, word for word"""
    takes = (" ".join(taken),)
    command = " ".join(words)
    verdict = RUN_ONLY.check_call(takes, Call(COMMAND, command=command), {}, WHERE, takes)
    assert verdict.passes == (command == takes[0])


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
@given(NAMES, NAMES)
def test_a_write_passes_write_only_exactly_when_it_names_the_file_it_takes(
    taken: str, written: str
):
    """Given a write_only Lane that takes any file at the root
    When the role writes any file at the root
    Then the call passes exactly where it's the file taken"""
    call = Call(WRITE, path=f"/repo/{written}.md")
    verdict = WRITE_ONLY.check_call((f"{taken}.md",), call, {}, WHERE, ())
    assert verdict.passes == (taken == written)


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
@given(st.dictionaries(WORDS, WORDS | st.integers() | st.none(), max_size=6))
def test_any_payload_reads_as_an_event_or_raises_a_fault(fields: dict[str, Any]):
    """Given the recorded PreToolUse of writer's `git log`, with any fields put in or replaced
    When the guard's entry reads it
    Then it gives an event or raises a Fault, and nothing else"""
    payload = dict(line(RUN, "writer runs git log")["payload"], **fields)
    try:
        hook.read(json.dumps(payload), {"CLAUDE_PROJECT_DIR": "/repo"})
    except Fault:
        pass


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_the_start_due")
@given(
    st.lists(st.tuples(NAMES, WORDS, st.dictionaries(NAMES, WORDS, max_size=2)), max_size=4),
    st.lists(st.tuples(NAMES, NAMES), max_size=4),
)
def test_any_run_written_reads_back_equal(started: list[Any], given_results: list[Any]):
    """Given a Run with any Starts, their texts and run values, and any Results
    When it's written to its record and read back
    Then it reads back equal"""
    written = run(
        starts=[Start(n, role, text, values) for n, (role, text, values) in enumerate(started, 1)],
        results=[Result(role, result) for role, result in given_results],
    )
    assert loads(dumps(written), os.path.join("/tmp", "run.jsonl")) == written
