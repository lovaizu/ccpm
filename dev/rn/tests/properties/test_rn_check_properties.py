"""The property-based test of the evaluator's answers, as rn's Test strategy names it: the evaluator
names, for each condition, what's good or what would make it good (P2.2), judging every condition
from one trial (Components), so its result holds each condition of its Cut once, in good or in
more. An AI writes the answers, and may leave one out, answer one twice or in both, or name one
the Cut doesn't hold; each such result must be refused at its end, else the orchestrator takes a
condition unjudged for judged, and one whose answer is whole must pass, else the run stops. The
model: the result passes where each ID of the Cut is answered exactly once and no other ID is.

A deliverable's Markdown is held to its kind's template (P3.2): whatever Markdown a generator
writes, its end gives the places where it leaves the template of a kind that has one, each as the
template check, which ccpm's developers run on rn's own documents, gives it, and none of a kind
that has none, else the people get a document whose form no reader of its kind expects."""

from __future__ import annotations

import os
import re
import tempfile
from typing import Any

import pytest
import rn_files
from check.result import faults
from hypothesis import given
from hypothesis import strategies as st
from template import check as template

LINE = "# Print an invoice"
WAYS = st.sampled_from(["good", "more", "both", "none", "good twice", "more twice"])


@st.composite
def answers(draw: Any) -> tuple[str, dict[str, Any], bool]:
    """A kind, the evaluator's result for a Cut of the kind, each condition answered in any of the
    ways an AI may write it, with or without an ID the Cut doesn't hold, and whether the model
    passes it."""
    kind = draw(st.sampled_from(["light", "readme"]))
    good, more, whole = [], [], True
    for each in rn_files.conditions(kind):
        way = draw(WAYS)
        whole = whole and way in ("good", "more")
        good += [{"condition": each, "lines": [LINE]}] * {
            "good": 1,
            "both": 1,
            "good twice": 2,
        }.get(way, 0)
        more += [{"condition": each, "good_when": "The accountant prints it alone."}] * {
            "more": 1,
            "both": 1,
            "more twice": 2,
        }.get(way, 0)
    extra = draw(st.sampled_from([None, "N99", "C1", "n1", "N1 "]))
    if extra:
        more.append({"condition": extra, "good_when": "It holds."})
        whole = False
    return kind, {"result": "judged", "good": good, "more": more}, whole


@pytest.mark.supports("test_an_evaluators_answers_leaving_a_condition_unanswered_are_refused")
@given(answers())
def test_an_evaluators_result_passes_exactly_where_each_condition_is_answered_once(
    case: tuple[str, dict[str, Any], bool],
):
    """Given any evaluator's result for a Cut of the guide, each condition answered in good, in
    more, in both, twice, or not at all, with or without an ID the Cut doesn't hold, each line it
    quotes standing in the guide
    When its faults are found
    Then it has none exactly where the model passes it
    (Model-based, resting on P2.2.)"""
    kind, result, whole = case
    with tempfile.TemporaryDirectory() as worktree:
        os.makedirs(os.path.join(worktree, "docs"))
        with open(os.path.join(worktree, "docs", "guide.md"), "w", encoding="utf-8") as f:
            f.write(LINE + "\n\nSave the lines as lines.csv.\n")
        cut = {
            "goal": rn_files.GOAL,
            "deliverable": {"name": rn_files.GUIDE_NAME, "path": rn_files.GUIDE},
            "judges_by": rn_files.judged_by(kind),
            "worktree": worktree,
            "round": rn_files.round_of(
                os.path.join(worktree, ".rn", "r"), rn_files.GUIDE, "content", 1
            ),
            "trial": os.path.join(tempfile.gettempdir(), "rn-trial-r-docs%2Fguide.md-content-1"),
        }
        found = faults("evaluator", cut, result, worktree, worktree)
    assert (found == []) == whole


# Markdown as a generator writes it: headings, paragraphs, list items, and code, in any order.
BLOCK = st.one_of(
    st.builds(
        lambda level, words: "#" * level + " " + words,
        st.integers(1, 3),
        st.sampled_from(
            ["Print an invoice", "Requirements", "Installation", "Walkthrough", "License", "rn"]
        ),
    ),
    st.sampled_from(
        [
            "Save the lines as `lines.csv`, and type the command.",
            "- Python 3.9 or later: `python3 --version` shows it.",
            "```console\npython3 -m invoicer lines.csv --rate 0.19\n```",
            "The accounting team prints each invoice themselves.",
        ]
    ),
)
MARKDOWN = st.lists(BLOCK, min_size=1, max_size=8).map(lambda blocks: "\n\n".join(blocks) + "\n")
TEMPLATED = re.compile(r"^docs/guide\.md:[0-9]+: ")


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
@given(MARKDOWN, st.sampled_from(["readme", "light"]))
def test_a_generators_markdown_gives_exactly_the_template_checks_places(text: str, kind: str):
    """Given any Markdown that a generator writes as the guide, of the kind readme, whose best
    practice has a template, or light, whose has none, and its result made, quoting the guide's
    first line as good of N1
    When its faults are found
    Then the places of the template among them are each `docs/guide.md:<line>: <what>` that the
    template check gives against readme's template, and none for light
    (Model-based, resting on P3.2, a deliverable's Markdown held to its kind's template.)"""
    first = text.splitlines()[0]
    with tempfile.TemporaryDirectory() as worktree:
        os.makedirs(os.path.join(worktree, "docs"))
        with open(os.path.join(worktree, rn_files.GUIDE), "w", encoding="utf-8") as f:
            f.write(text)
        round_ = rn_files.round_of(os.path.join(worktree, ".rn", "r"), rn_files.GUIDE, "content", 1)
        cut = {
            "goal": rn_files.GOAL,
            "language": rn_files.DELIVERABLES_LANGUAGE,
            "deliverable": rn_files.open_node(rn_files.GUIDE_NAME, rn_files.GUIDE, kind),
            "worktree": worktree,
            "inputs": [],
            "best_practice": os.path.join(rn_files.PRACTICES, kind),
            "stage": "content",
            "number": 1,
            "round": round_,
            "findings": None,
            "last_good": None,
        }
        result = rn_files.made([("N1", [first])], [rn_files.GUIDE])
        found = faults("generator", cut, result, worktree, worktree)
    model = []
    if kind == "readme":
        with open(template.of_kind(rn_files.RN, kind), encoding="utf-8") as f:
            form = f.read()
        model = [f"docs/guide.md:{each.line}: {each.what}" for each in template.faults(form, text)]
    assert [each for each in found if TEMPLATED.match(each)] == model
