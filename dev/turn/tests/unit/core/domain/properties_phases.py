"""Properties of phases.py over many runs of rounds, Answers, lines and design trees: the rounds
settled, whatever each met and however the design changed between them, follow the phase table,
numbered on by one with each round before kept apart; Answers that answer each question given once
hold, and one left out or given twice is named alone; a line lies in the work exactly where it runs
from the first line to the file's last; and the decisions that serve a question are exactly those
from which a chain of contributions reaches it."""

from __future__ import annotations

import os
import tempfile
import unittest

import helpers
from helpers import RUN, VERIFICATION, met, phases, short

hypothesis = helpers.testing.hypothesis()
given, st = hypothesis.given, hypothesis.strategies

DESIGN = os.path.join(RUN, "design-tree.json")
CONTENT_GROUPS = [["note/Q1"], ["note/Q2"], ["note/Q3"]]


def due(made: list[dict], design: int) -> str | None:
    """The phase the table gives after the rounds made, on the design as it is: content until the
    last content round was made on it and met every question, then reading until a reading round
    after it met every question, then none."""
    content = [n for n, r in enumerate(made) if r["phase"] == "content"]
    if not content or made[content[-1]]["design"] != design or not made[content[-1]]["met"]:
        return "content"
    after = made[content[-1] + 1 :]
    return None if after and after[-1]["met"] else "reading"


class TestSettle(helpers.RoundsTest):
    @given(st.lists(st.tuples(st.booleans(), st.booleans(), st.integers(0, 2)), max_size=12))
    def test_the_rounds_follow_the_phase_table_whatever_each_meets(self, steps):
        # Given: a run in its rounds, laid anew for each example
        os.chdir(tempfile.mkdtemp(dir=self.base))
        self.lays()
        made: list[dict] = []
        design = 0
        for changes, meets, falls in steps:
            # When: the design may change, then the next round is settled and answered
            if changes:
                design += 1
                self.write_json(
                    DESIGN, {**helpers.TREE, "goal": {"what": str(design), "grounds": []}}
                )
            settled = phases.settle(RUN)
            # Then: its phase is the table's, and its number follows the last, kept apart
            expected = due(made, design)
            if expected is None:
                self.assertIsNone(settled)
                continue
            assert settled is not None
            self.assertEqual((settled["phase"], settled["round"]), (expected, len(made) + 1))
            for n in range(1, len(made) + 1):
                kept = self.read_json(os.path.join(VERIFICATION, str(n), "round.json"))
                self.assertEqual(kept["round"], n)
            groups = CONTENT_GROUPS if expected == "content" else [["refactor-doc/Q1"]]
            for n, questions in enumerate(groups, 1):
                fell = not meets and n == falls % len(groups) + 1
                self.answers(f"G{n}.json", short(*questions) if fell else met(*questions))
            made.append({"phase": expected, "design": design, "met": meets})


QUESTIONS = st.integers(1, 6).map(lambda n: [f"k/Q{i}" for i in range(1, n + 1)])


@st.composite
def answered(draw) -> tuple[list[str], dict]:
    """Questions given, and Answers that answer each once, met or not met, in any order."""
    given_ = draw(QUESTIONS)
    order = draw(st.permutations(given_))
    meets = [q for q in order if draw(st.booleans())]
    data = {
        "met": [{"question": q, "lines": []} for q in meets],
        "not_met": [{"question": q, "lacks": "l"} for q in order if q not in meets],
    }
    return given_, data


class TestFaults(unittest.TestCase):
    @given(answered(), st.booleans())
    def test_answers_to_each_question_given_once_hold_and_give_the_tables_result(
        self, drawn, opens
    ):
        given_, data = drawn
        self.assertEqual(phases.faults(data, given_, [], opens), [])
        content = "more" if data["not_met"] else "met"
        reading = "reword" if data["not_met"] else "good"
        self.assertEqual(phases.result(data, False, phases.CONTENT), content)
        self.assertEqual(phases.result(data, False, phases.READING), reading)
        self.assertEqual(phases.result(data, True, phases.CONTENT), "made")

    @given(answered(), st.data())
    def test_a_question_left_out_is_named_alone(self, drawn, data):
        given_, answers = drawn
        side = data.draw(st.sampled_from([s for s in ("met", "not_met") if answers[s]]))
        gone = answers[side].pop(data.draw(st.integers(0, len(answers[side]) - 1)))
        found = phases.faults(answers, given_, [], True)
        self.assertEqual(found, [f"{gone['question']} has no answer"])

    @given(answered(), st.data())
    def test_a_question_answered_twice_is_named_alone(self, drawn, data):
        given_, answers = drawn
        side = data.draw(st.sampled_from([s for s in ("met", "not_met") if answers[s]]))
        twice = data.draw(st.sampled_from(answers[side]))
        answers[data.draw(st.sampled_from(["met", "not_met"]))].append(
            {**twice, "lines": [], "lacks": "l"}
        )
        found = phases.faults(answers, given_, [], True)
        self.assertEqual(found, [f"{twice['question']} is answered more than once"])


class TestLine(helpers.testing.FolderTest):
    @given(st.integers(0, 12), st.integers(-1, 14), st.none() | st.integers(-1, 14))
    def test_a_line_lies_in_the_work_exactly_from_the_first_line_to_the_last(
        self, count, first, last
    ):
        self.write("W.md", "".join(f"{n}\n" for n in range(count)))
        line = f"W.md:{first}" + ("" if last is None else f"-{last}")
        end = first if last is None else last
        fault = phases.line_fault(line, ["W.md"])
        self.assertEqual(fault == "", first >= 1 and first <= end <= count, fault)


@st.composite
def trees(draw) -> dict:
    """A design tree of up to eight decisions, each contributing to any of three questions or of
    the decisions, before or after it or itself, so joins may come back round."""
    ids = [f"D{n}" for n in range(1, draw(st.integers(0, 8)) + 1)]
    targets = ["Q1", "Q2", "Q3", *ids]
    return {
        "decisions": [
            {"id": d, "contributes_to": draw(st.lists(st.sampled_from(targets), max_size=3))}
            for d in ids
        ]
    }


class TestServing(unittest.TestCase):
    @given(trees(), st.sampled_from(["Q1", "Q2", "Q3"]))
    def test_the_decisions_serving_a_question_are_those_a_chain_leads_from(self, tree, question):
        reached: set[str] = set()
        grown = True
        while grown:
            new = {
                d["id"]
                for d in tree["decisions"]
                if any(c == question or c in reached for c in d["contributes_to"])
            }
            grown = not new <= reached
            reached |= new
        expected = [d["id"] for d in tree["decisions"] if d["id"] in reached]
        self.assertEqual(phases.serving(tree, question), expected)


if __name__ == "__main__":
    unittest.main()
