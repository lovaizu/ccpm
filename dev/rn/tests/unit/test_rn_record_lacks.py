"""The unit cases of what rn's check reads and finds lacking: record/steps.py, the steps of a
prompt; record/practices.py, the practices of a best practice; record/order.py, what a record lacks
of them in order; and record/items.py, what a result leaves out of its Cut. The steps turn on the
prompt, a role's part, a command, or none of rn's, with steps or none; the practices on a best
practice in form, out of it, or missing; the order on each step and practice there and in place,
one missing, and one out of place; and the items on each role's result naming each item, leaving
one out, or being asks or lacks, each More kept by its best practice and condition."""

from __future__ import annotations

import os
import re
import shutil
from typing import Any

import pytest
from fault import CantRun, Wrong
from record import items, order, practices, steps
from record.form import Entry, Record
from record.practices import Phase, Practice
from tree.cut import Cut
from tree.results import Answers, Made

from dev.rn.tests.unit import rn_data as d

STEPS = "\n## Steps\n\n1. Read your Cut.\n2. Decide.\n3. Make.\n"
DECIDE, MAKE = Practice("N1.1", Phase.DECIDE), Practice("N1.2", Phase.MAKE)
DECISION = "deliverables/0/necessary_conditions/0/decisions/0"


def plugin_with_steps(tmp: Any, held: dict[str, str]) -> str:
    """A copy of rn whose prompt in each file given holds the Steps given in place of its own."""
    root = os.path.join(tmp, "rn")
    shutil.copytree(d.RN, root, ignore=shutil.ignore_patterns("__pycache__", "best-practices"))
    for file, given in held.items():
        with open(os.path.join(root, file), encoding="utf-8") as f:
            text = f.read()
        text = re.sub(r"\n## Steps\n.*?(?=\n## |\Z)", "", text, flags=re.DOTALL) + given
        with open(os.path.join(root, file), "w", encoding="utf-8") as f:
            f.write(text)
    return root


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
@pytest.mark.parametrize("of", ["generator", "dn"])
def test_the_steps_of_a_roles_part_or_a_command_are_numbered_in_order(
    tmp_path: Any, of: str
) -> None:
    """Given: rn with the generator's part and /rn:dn each holding steps 1 to 3 under Steps.
    When: the steps of the generator, and of dn, are asked.
    Then: each gives 1, 2, and 3."""
    held = {"domain/generator.md": STEPS, os.path.join("skills", "dn", "SKILL.md"): STEPS}
    assert steps.numbers(plugin_with_steps(tmp_path, held), of) == (1, 2, 3)


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_a_prompt_with_no_steps_gives_none(tmp_path: Any) -> None:
    """Given: rn with the evaluator's part holding Steps empty.
    When: the evaluator's steps are asked.
    Then: it gives none."""
    held = {"domain/evaluator.md": "\n## Steps\n"}
    assert steps.numbers(plugin_with_steps(tmp_path, held), "evaluator") == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_a_prompt_rn_doesnt_have_is_refused() -> None:
    """Given: rn.
    When: the steps of writer are asked.
    Then: it's refused, naming writer."""
    with pytest.raises(Wrong, match="writer"):
        steps.numbers(d.RN, "writer")


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_the_practices_of_a_best_practice_are_given_in_order_with_their_phases() -> None:
    """Given: rn's code best practice, whose N1 holds four items taken while deciding and two while
    making.
    When: its practices are asked.
    Then: they begin N1.1 to N1.4 deciding and N1.5 and N1.6 making, in the order of its
    conditions and items."""
    found = practices.practices(os.path.join(d.RN, "domain", "best-practices", "code"))
    assert found[:6] == tuple(
        Practice(f"N1.{n}", Phase.DECIDE if n <= 4 else Phase.MAKE) for n in range(1, 7)
    )


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_a_best_practice_out_of_form_or_missing_is_refused(tmp_path: Any) -> None:
    """Given: a folder whose best-practice.json lacks its goal, and a folder with none.
    When: the practices of each are asked.
    Then: the first is refused, and the second couldn't run."""
    bad = os.path.join(tmp_path, "bad")
    d.write_json(os.path.join(bad, "best-practice.json"), {"template": "template.md"})
    with pytest.raises(Wrong):
        practices.practices(bad)
    with pytest.raises(CantRun):
        practices.practices(os.path.join(tmp_path, "none"))


def record(*entries: tuple[str, int | str]) -> Record:
    """A record of the entries, each a step by its number or a practice by its ID."""
    return Record(
        tuple(
            Entry(of, n, None, "a.py:1") if isinstance(n, int) else Entry(of, None, n, "a.py:1")
            for of, n in entries
        ),
        None,
    )


CODE = {"code": (DECIDE, MAKE)}


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_a_record_with_each_step_and_practice_in_order_lacks_nothing() -> None:
    """Given: a record of step 1, the deciding practice, step 2, the making practice, and step 3.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it lacks nothing."""
    held = record(
        ("generator", 1), ("code", "N1.1"), ("generator", 2), ("code", "N1.2"), ("generator", 3)
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
@pytest.mark.parametrize(
    ("held", "named"),
    [
        (record(("generator", 1), ("code", "N1.1"), ("generator", 2), ("code", "N1.2")), "3"),
        (record(("generator", 1), ("generator", 2), ("code", "N1.2"), ("generator", 3)), "N1.1"),
        (
            record(
                ("generator", 2),
                ("generator", 1),
                ("code", "N1.1"),
                ("code", "N1.2"),
                ("generator", 3),
            ),
            "1",
        ),
        (record(), "1"),
    ],
)
def test_a_record_lacking_a_step_or_practice_or_out_of_order_names_it(
    held: Record, named: str
) -> None:
    """Given: a record missing step 3, missing the deciding practice, with step 2 before step 1,
    or empty.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it names the step or practice lacking or out of place."""
    found = order.lacks(held, "generator", (1, 2, 3), CODE)
    assert found and any(named in each for each in found)


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_practices_recorded_in_one_run_in_any_order_lack_nothing() -> None:
    """Given: a record of step 1, the making practice and then the deciding one in one run, as a
    role records the practices of a best practice at once, then steps 2 and 3.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it lacks nothing, as the record shows that each practice was taken, within the steps."""
    held = record(
        ("generator", 1), ("code", "N1.2"), ("code", "N1.1"), ("generator", 2), ("generator", 3)
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_a_prompt_with_no_steps_and_no_practices_lacks_nothing() -> None:
    """Given: an empty record.
    When: what it lacks of a prompt with no steps and no best practice is asked.
    Then: it lacks nothing."""
    assert order.lacks(record(), "evaluator", (), {}) == ()


# The state of a pass as order.lacks reads a record entry by entry: no pass begun, at a step of it,
# or past its last step; and each entry that can come in each state, its next step, the step again
# in a row, the first step again, a step before the one it's at, a step past the next, a practice,
# a practice of a best practice the role doesn't work by, and an entry of another prompt.
FOUR = (1, 2, 3, 4)


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_before_a_pass_a_later_step_begins_none_and_each_step_lacks() -> None:
    """Given: a record of steps 2 and 3 and the practices, with no step 1.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it names steps 1, 2, and 3 and both practices, as no pass has begun."""
    held = record(("generator", 2), ("code", "N1.1"), ("code", "N1.2"), ("generator", 3))
    found = order.lacks(held, "generator", (1, 2, 3), CODE)
    assert [f for f in found if "step" in f] == [
        f"generator step {n} isn't recorded" for n in (1, 2, 3)
    ]
    assert {"code N1.1 isn't recorded", "code N1.2 isn't recorded"} <= set(found)


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_before_a_pass_a_practice_lies_outside_it_and_is_named() -> None:
    """Given: a record of the deciding practice, then steps 1, 2, and 3 with the making practice.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it names the deciding practice alone, as it lies before the pass."""
    held = record(
        ("code", "N1.1"), ("generator", 1), ("code", "N1.2"), ("generator", 2), ("generator", 3)
    )
    found = order.lacks(held, "generator", (1, 2, 3), CODE)
    assert len(found) == 1 and "N1.1" in found[0]


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_at_a_step_the_same_step_again_in_a_row_is_taken_once() -> None:
    """Given: a record of step 1, step 2 at three places in a row, the practices, and step 3.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it lacks nothing, as a role records a step at each place where its result lies."""
    held = record(
        ("generator", 1),
        ("generator", 2),
        ("generator", 2),
        ("code", "N1.1"),
        ("generator", 2),
        ("code", "N1.2"),
        ("generator", 3),
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_at_a_step_the_first_step_again_begins_a_pass_that_lacks_each_step_after_it() -> None:
    """Given: a record of steps 1 and 2 with the practices, then step 1 again, as a role resumed.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it names steps 2 and 3 and both practices, of the pass that step 1 began again."""
    held = record(
        ("generator", 1), ("code", "N1.1"), ("generator", 2), ("code", "N1.2"), ("generator", 1)
    )
    found = order.lacks(held, "generator", (1, 2, 3), CODE)
    assert sorted(found) == sorted(
        [
            "generator step 2 isn't recorded after step 1",
            "generator step 3 isn't recorded after step 1",
            "code N1.1 isn't recorded",
            "code N1.2 isn't recorded",
        ]
    )


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_at_a_step_a_step_past_the_next_is_named_out_of_its_place() -> None:
    """Given: a record of step 1, step 3, then steps 2 and 3, with the practices between.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it names step 3 recorded before step 2, as the role took step 3 before step 2."""
    held = record(
        ("generator", 1),
        ("generator", 3),
        ("code", "N1.1"),
        ("code", "N1.2"),
        ("generator", 2),
        ("generator", 3),
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == (
        "generator step 3 is recorded before step 2",
    )


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
@pytest.mark.xfail(
    strict=True,
    reason="a step taken again after a later one, mid-pass, holds the end for good, though each"
    " step after it is then recorded in order and none was skipped",
)
def test_at_a_step_an_earlier_step_again_lacks_nothing_once_each_step_after_it_follows() -> None:
    """Given: a record of steps 1, 2, and 3 with the practices, step 2 again, as the role went back
    to decide again, then step 4.
    When: what it lacks of steps 1 to 4 and the code practices is asked.
    Then: it lacks nothing, as each step was taken in its order and none skipped, and a record
    only grows, so a step named out of place can't be mended but by every step again."""
    held = record(
        ("generator", 1),
        ("code", "N1.1"),
        ("generator", 2),
        ("code", "N1.2"),
        ("generator", 3),
        ("generator", 2),
        ("generator", 4),
    )
    assert order.lacks(held, "generator", FOUR, CODE) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_past_the_last_step_an_earlier_step_again_lacks_nothing() -> None:
    """Given: a record of steps 1, 2, and 3 with the practices, then step 2 again.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it lacks nothing, as each step was taken in its order."""
    held = record(
        ("generator", 1),
        ("code", "N1.1"),
        ("generator", 2),
        ("code", "N1.2"),
        ("generator", 3),
        ("generator", 2),
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_past_the_last_step_a_practice_lies_outside_the_steps_and_is_named() -> None:
    """Given: a record of steps 1, 2, and 3 with the deciding practice, then the making one.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it names the making practice as recorded outside the steps."""
    held = record(
        ("generator", 1), ("code", "N1.1"), ("generator", 2), ("generator", 3), ("code", "N1.2")
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == (
        "code N1.2 is recorded outside the steps of generator",
    )


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
@pytest.mark.xfail(
    strict=True,
    reason="a practice recorded within the steps and again past the last is named outside them, as"
    " the check reads only its latest place",
)
def test_past_the_last_step_a_practice_taken_within_the_steps_too_lacks_nothing() -> None:
    """Given: a record of steps 1 to 3 with both practices between, then the making practice again
    at another place.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it lacks nothing, as the record shows the practice taken within the steps."""
    held = record(
        ("generator", 1),
        ("code", "N1.1"),
        ("generator", 2),
        ("code", "N1.2"),
        ("generator", 3),
        ("code", "N1.2"),
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_at_any_state_another_best_practices_practice_or_another_prompts_step_is_passed_over() -> (
    None
):
    """Given: a record of each step and practice in order, with a practice of the readme best
    practice, which the role doesn't work by, and steps of up between them.
    When: what it lacks of the generator's steps 1 to 3 and the code practices is asked.
    Then: it lacks nothing."""
    held = record(
        ("up", 2),
        ("generator", 1),
        ("readme", "N1.1"),
        ("code", "N1.1"),
        ("up", 1),
        ("generator", 2),
        ("code", "N1.2"),
        ("up", 4),
        ("generator", 3),
        ("readme", "N9.9"),
    )
    assert order.lacks(held, "generator", (1, 2, 3), CODE) == ()


def generator_cut(*more: str) -> Cut:
    """A generator's Cut of invoicer with the user's decision, and the More kept of N2 of each best
    practice given."""
    part = {
        "cut": {
            "decisions": [
                {
                    "condition": "N1",
                    "decision": {"path": DECISION, "point": "p", "decided": "d", "ground": "g"},
                }
            ],
            "more": [
                {"best_practice": b, "condition": "N2", "decision": DECISION, "good_when": "w"}
                for b in more
            ],
        }
    }
    return Cut("generator", {"deliverable": "invoicer"}, part)


@pytest.mark.supports("test_a_made_that_leaves_out_a_decision_of_the_cut_is_held_with_it")
def test_a_made_naming_each_decision_and_more_lacks_nothing() -> None:
    """Given: a generator's Cut with one decision and the More kept of N2 of code, and a Made
    naming both.
    When: what the result done leaves out is asked.
    Then: it leaves out nothing."""
    made = Made({DECISION: "invoicer"}, {("code", "N2"): "invoicer"}, ())
    assert items.lacks(generator_cut("code"), "done", made, None) == ()


@pytest.mark.supports("test_a_made_that_leaves_out_a_decision_of_the_cut_is_held_with_it")
@pytest.mark.parametrize(
    ("more", "made", "named"),
    [
        (("code",), Made({}, {("code", "N2"): "invoicer"}, ()), (DECISION,)),
        (("code",), Made({DECISION: "invoicer"}, {}, ()), ("code", "N2")),
        (
            ("code", "refactor-code"),
            Made({DECISION: "invoicer"}, {("code", "N2"): "invoicer"}, ()),
            ("refactor-code", "N2"),
        ),
    ],
)
def test_a_made_that_leaves_out_an_item_names_it(
    more: tuple[str, ...], made: Made, named: tuple[str, ...]
) -> None:
    """Given: a generator's Cut with one decision and the More kept of N2 of code, or of code and
    refactor-code, and a Made that leaves out the decision, the More kept, or the refactor one.
    When: what the result done leaves out is asked.
    Then: it names the item left out, a More kept by its best practice and condition."""
    found = items.lacks(generator_cut(*more), "done", made, None)
    assert found and any(all(n in each for n in named) for each in found)


@pytest.mark.supports("test_a_generator_that_asks_is_resumed_once_the_tree_holds_the_decision")
@pytest.mark.parametrize("result", ["asks", "lacks"])
def test_a_result_of_asks_or_lacks_carries_no_item(result: str) -> None:
    """Given: a generator's Cut with one decision, and no Made.
    When: what the result asks, or lacks, leaves out is asked.
    Then: it leaves out nothing."""
    assert items.lacks(generator_cut(), result, None, None) == ()


@pytest.mark.supports("test_one_evaluator_starts_for_each_group_of_necessary_conditions")
@pytest.mark.parametrize(
    ("answers", "lacking"),
    [
        (Answers({"N1": ("l",), "N2": ("l",)}, {"N3": "w"}), ()),
        (Answers({"N1": ("l",)}, {"N3": "w"}), ("N2",)),
    ],
)
def test_answers_name_each_condition_of_the_group(
    answers: Answers, lacking: tuple[str, ...]
) -> None:
    """Given: an evaluator's Cut of the group N1 to N3, and Answers naming each, or all but N2.
    When: what the result done leaves out is asked.
    Then: it leaves out nothing, or names N2."""
    found = items.lacks(
        Cut("evaluator", {}, {"conditions": ["N1", "N2", "N3"]}), "done", None, answers
    )
    assert all(any(c in each for each in found) for c in lacking) and bool(found) == bool(lacking)
