"""The property-based tests of Lane's reading of Steps and Proposals, of each lane type's check, and
of the guard's reading of events, as Lane's Test strategy names them: a user writes Steps and an AI
writes each Proposal, and Claude Code hands each event, in forms that no developer foresees. Each
finds no counterexample, by hypothesis, and quality.sh runs them in CI."""

from __future__ import annotations

import json
from typing import Any

import lane_data as d
import pytest
from events import NotAnEvent, read_event
from form import Laid, LaidSentence, OutOfForm, read_proposal
from hypothesis import given
from hypothesis import strategies as st
from lanes.ends_by_result import TYPE as ENDS_BY_RESULT
from lanes.kind import Held
from lanes.run_only import TYPE as RUN_ONLY
from lanes.write_only import TYPE as WRITE_ONLY
from lay.laid import as_laid, strip
from lay.steps import Step

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")

WORD = st.text("abcdefghijklmnopqrstuvwxyz`.-", min_size=1, max_size=10)
SENTENCE = st.lists(WORD, min_size=1, max_size=6).map(
    lambda words: " ".join(words).capitalize() + "."
)
NAME = st.text("abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=8)
HELD = Held(d.run(starts=(d.start("writer"),), due=()), d.start("writer"), d.ROOT)


@st.composite
def steps_and_sentences(draw: Any) -> tuple[tuple[Step, ...], dict[tuple[str, int], str]]:
    """Steps of one file, and a sentence for some of them that no Step already says."""
    texts = draw(st.lists(SENTENCE, min_size=1, max_size=5))
    steps = tuple(Step("writer", "agents/writer.md", n, t) for n, t in enumerate(texts, 1))
    sentences = {}
    for step in steps:
        sentence = draw(st.one_of(st.none(), SENTENCE))
        if sentence and sentence not in step.text:
            sentences[(step.file, step.number)] = sentence
    return steps, sentences


@st.composite
def proposals(draw: Any) -> dict[str, Any]:
    """A Proposal in lanes.schema.json's form."""
    lane = st.fixed_dictionaries(
        {
            "role": NAME,
            "file": NAME.map(lambda n: f"agents/{n}.md"),
            "step": st.integers(1, 30),
            "type": NAME,
            "args": st.dictionaries(NAME, st.one_of(WORD, st.lists(WORD, max_size=3)), max_size=2),
        }
    )
    after = st.one_of(
        st.just({"first": True}),
        st.fixed_dictionaries({"role": NAME, "result": NAME}),
        st.fixed_dictionaries({"command": NAME}),
        st.fixed_dictionaries({"returned": NAME}),
    )
    move = st.one_of(
        *[st.fixed_dictionaries({kind: NAME}) for kind in ("start", "resume", "no_more", "call")],
        st.fixed_dictionaries({"wait": st.one_of(st.just(""), NAME)}),
    )
    route = st.fixed_dictionaries(
        {"skill": NAME, "after": after, "moves": st.lists(move, min_size=1, max_size=3)}
    )
    adapters = st.fixed_dictionaries({}, optional={"text": NAME, "records": NAME})
    return {
        "lanes": draw(st.lists(lane, max_size=4)),
        "routes": draw(st.lists(route, max_size=4)),
        "adapters": draw(adapters),
    }


@pytest.mark.supports("test_steps_after_a_lay_come_without_lanes_sentences")
@given(steps_and_sentences())
def test_steps_laid_then_stripped_read_as_written(given_: Any) -> None:
    """Given: any Steps, and a sentence for some of them that the Step doesn't already say.
    When: as_laid lays the sentences, and strip takes out the Laid of them.
    Then: each Step reads as it was written, with no note."""
    steps, sentences = given_
    laid = Laid("0.1.0", tuple(LaidSentence(f, n, t) for (f, n), t in sentences.items()))
    assert strip(as_laid(steps, sentences), laid) == (steps, ())


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
@given(proposals())
def test_a_proposal_in_form_reads_whole(proposal: dict[str, Any]) -> None:
    """Given: any Proposal in lanes.schema.json's form.
    When: read_proposal reads it.
    Then: it gives as many Lanes and Routes, each Route with as many moves."""
    read = read_proposal(json.dumps(proposal))
    assert len(read.lanes) == len(proposal["lanes"])
    assert [len(r.moves) for r in read.routes] == [len(r["moves"]) for r in proposal["routes"]]


@pytest.mark.supports("test_a_proposal_that_cant_stand_goes_back_to_up")
@given(
    st.one_of(
        st.text(max_size=40),
        st.recursive(
            st.none() | st.integers() | st.text(max_size=5),
            lambda inner: st.lists(inner, max_size=3) | st.dictionaries(NAME, inner, max_size=3),
        ).map(json.dumps),
    )
)
def test_any_text_reads_as_a_proposal_or_is_out_of_form(text: str) -> None:
    """Given: any text, JSON or not.
    When: read_proposal reads it.
    Then: it gives a Proposal or raises OutOfForm, never another error."""
    try:
        read_proposal(text)
    except OutOfForm:
        pass


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
@given(
    st.one_of(
        st.text(max_size=40),
        st.dictionaries(
            st.sampled_from(["hook_event_name", "session_id", "cwd", "agent_id", "tool_input"]),
            st.one_of(st.none(), st.integers(), st.text(max_size=8)),
            max_size=5,
        ).map(json.dumps),
    )
)
def test_any_input_reads_as_an_event_or_is_refused(text: str) -> None:
    """Given: any standard input, JSON or not.
    When: read_event reads it.
    Then: it gives an Event or raises NotAnEvent, never another error."""
    try:
        read_event(text)
    except NotAnEvent:
        pass


@pytest.mark.supports("test_a_call_that_breaks_a_lane_gets_its_steps_sentence")
@given(
    st.one_of(st.just("git log --oneline"), st.lists(WORD, min_size=1, max_size=4).map(" ".join))
)
def test_run_only_allows_a_command_only_word_for_word(command: str) -> None:
    """Given: writer's run_only Lane for `git log --oneline`, and any Bash command.
    When: the type judges it.
    Then: it allows the command only where it is `git log --oneline` word for word."""
    allowed = RUN_ONLY.allows(d.run_only(), d.bash(command), HELD)
    assert allowed is (command == "git log --oneline")


@pytest.mark.supports("test_the_sentence_laid_is_the_sentence_a_stop_gives")
@given(st.one_of(st.just("CHANGELOG.md"), st.lists(NAME, min_size=1, max_size=3).map("/".join)))
def test_write_only_allows_only_its_path(path: str) -> None:
    """Given: writer's write_only Lane for `CHANGELOG.md`, and a Write of any path in tally.
    When: the type judges it.
    Then: it allows the Write only of tally's CHANGELOG.md."""
    call = d.write(f"{d.REPO}/{path}")
    assert WRITE_ONLY.allows(d.write_only(), call, HELD) is (path == "CHANGELOG.md")


@pytest.mark.supports("test_a_result_is_added_for_the_subagents_start")
@given(NAME, st.one_of(st.just("writer"), NAME), st.lists(WORD, max_size=3).map(" ".join))
def test_ends_by_result_allows_only_its_roles_run_of_the_result_script(
    result: str, role: str, more: str
) -> None:
    """Given: the Lane on writer's last Step, and a run of the plugin's result.py for any role and
    Result, with any words after it.
    When: the type judges it.
    Then: it allows it only where the role is writer and nothing follows the Result, and judges no
    other."""
    command = f"{d.RESULT} {role} {result} {more}".rstrip()
    allowed = ENDS_BY_RESULT.allows(d.WRITER_END, d.bash(command), HELD)
    assert allowed is (True if role == "writer" and not more else None)
