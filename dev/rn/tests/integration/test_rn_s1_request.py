"""The integration cases of S1: a request, and a deliverable made in rounds. Each path of its
sequence beyond the walking skeleton's, whose cases lie in test_rn_walking_skeleton.py: a new run
beside a run left, the goal put to the user, a second generator's start, a generator that asks,
that lacks, that's sent back, and that ends done, with its end held where it falls short, the
round, a more kept for the next round, and no start where no work waits. The rules that S1 keeps
have their cases in test_rn_rules.py."""

from __future__ import annotations

import json
import os
import re

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench

pytestmark = pytest.mark.xfail(
    strict=True, reason="rn's parts have empty bodies, and Lane hasn't laid rn's guard"
)


@pytest.mark.supports("S1", "adapters", "S5")
def test_words_after_up_start_a_new_run_beside_a_run_left(b: Bench) -> None:
    """Given: a run of the walkthrough left, its worktree still there, from an earlier conversation.
    When: the user types /rn:up with another request in a new conversation at the root, and the
    orchestrator runs tree.py start for it.
    Then: the guard gives the tree-keeper's start due as for a run started anew, never a pick-up,
    and tree.py runs lists both runs."""
    c, _ = w.asked(b)
    first, _ = w.run_made(b, c)
    again, asked = w.asked(b, words="a README for invoicer that tells a newcomer whether it fits")
    assert "rn:tree-keeper" in asked.said
    assert "Picking up" not in asked.said
    second = w.printed(again.bash(b.tree("start", "a README for invoicer")))
    names = [each["worktree"] for each in w.printed(again.bash(b.tree("runs")))]
    assert sorted(names) == sorted([first["worktree"], second["worktree"]])


@pytest.mark.supports("S1", "Point", "user")
def test_the_goal_is_put_to_the_user_once_the_design_tree_holds_it(b: Bench) -> None:
    """Given: the walkthrough's goal drafted and its plan in the design tree.
    When: the orchestrator ends its turn with the goal, as the README shows it, and the user types
    yes.
    Then: the guard lets the turn end, as it puts no work up; the README's goal is the one in the
    design tree; and once the tree-keeper writes the user's yes, the goal is the user's."""
    walk = w.confirmed(b)
    assert " ".join(w.GOAL.split()) in " ".join(w.GOAL_SHOWN.split())
    assert w.tree_in(walk)["goal"] == {"decided": w.GOAL, "by": "user"}


@pytest.mark.supports("S1", "adapters", "Cut")
def test_a_second_generator_starts_with_the_next_deliverable_doing(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, and the generator of its first deliverable running.
    When: the orchestrator starts another generator with the text that the guard gives due.
    Then: the second Cut names "invoicer marked as typed" at invoicer/py.typed, with a record of
    its own after the first's."""
    walk = w.planned(b)
    _, first = w.generator_started(walk)
    _, second = w.generator_started(walk)
    assert second["deliverable"] == w.TYPED_PATH and second["cut"]["name"] == w.TYPED
    assert second["record"] != first["record"]
    assert sorted([first["record"], second["record"]]) == [first["record"], second["record"]]


@pytest.mark.supports("S1", "S2", "generator", "Decision", "Point")
def test_a_generator_that_asks_is_resumed_once_the_tree_holds_the_decision(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer" running.
    When: it gives asks with the point of what a Line's quantity takes, the user answers, the
    tree-keeper writes the user's decision, and the orchestrator resumes the generator with its
    ground and the user's words.
    Then: the main conversation reads asks with the generator's point, the design tree holds the
    decision by the user, and the guard lets the resume through."""
    walk = w.planned(b)
    generator, _ = w.generator_started(walk)
    point = "For the person:\nShould a Line's quantity take a fraction?\nI recommend whole numbers."
    then = w.reached(b, generator, "asks", point)
    assert "asks" in then.said
    decision = {"about": "what a quantity takes", "decided": "whole numbers", "by": "user"}
    nodes = {"deliverables/0/necessary_conditions/1/decisions/0": decision}
    w.keeper_writes(b, walk, "The user's answer.", {"nodes": nodes, "more": []}, "whole numbers")
    held = w.tree_in(walk)["deliverables"][0]["necessary_conditions"][1]["decisions"]
    assert held == [decision]
    text = w.resume_text("The user decided it.", "whole numbers")
    assert not walk.c.resume(generator, text).blocked


@pytest.mark.supports("S1", "generator", "Point", "user")
def test_a_generator_that_lacks_a_tool_has_it_put_to_the_user(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer" running.
    When: it gives lacks, naming mypy, which isn't installed; the orchestrator ends its turn with
    what it lacks; the user clears it; and the orchestrator resumes the generator.
    Then: the main conversation reads lacks; the guard lets the turn end, as it puts no work up;
    and the guard lets the resume through."""
    walk = w.planned(b)
    generator, _ = w.generator_started(walk)
    then = w.reached(b, generator, "lacks", "For the person:\nmypy isn't installed.")
    assert "lacks" in then.said
    assert not walk.c.stop("For you: mypy isn't installed. Install it, and tell me.").blocked
    assert not walk.c.type("installed").blocked
    assert not walk.c.resume(generator, w.resume_text("mypy is installed.", "installed")).blocked


@pytest.mark.supports("S1", "record.py", "Record", "generator")
def test_a_generators_done_result_is_kept_in_its_record(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer", which made it and recorded
    each step and practice.
    When: it gives done and ends, and rn's check passes its end.
    Then: its record keeps the result done, by the generator, after each entry it recorded."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    w.made(b, walk, generator, cut)
    w.reached(b, generator, "done", "Made.")
    with open(os.path.join(walk.run["worktree"], cut["record"]), encoding="utf-8") as f:
        record = json.load(f)
    assert record["kept"] == {"role": "generator", "result": "done"}
    assert record["entries"]


@pytest.mark.supports("S1", "record.py", "Best practice", "guard")
def test_a_generators_end_with_its_deliverable_off_its_template_is_held(b: Bench) -> None:
    """Given: a plan of invoicer's README alone, signed off, and its generator, which recorded each
    step and practice and wrote a README.md of one heading, leaving out every section of the readme
    best practice's template.
    When: it gives done and ends.
    Then: the guard holds its end with each place where README.md leaves the template, by its line,
    and the record keeps no result."""
    walk = w.planned(b, w.readme_plan())
    generator, cut = w.generator_started(walk)
    w.made(b, walk, generator, cut)
    readme = os.path.join(walk.run["worktree"], "README.md")
    assert not generator.write(readme, "# invoicer\n").blocked
    ended, _ = w.give(b, generator, "done", "Made.")
    assert ended.blocked
    assert re.search(r"README\.md:\d+: ", ended.said)
    with open(os.path.join(walk.run["worktree"], cut["record"]), encoding="utf-8") as f:
        assert "kept" not in json.load(f)


@pytest.mark.supports("S1", "orchestrator", "generator")
def test_a_generator_sent_back_by_the_orchestrator_goes_on_from_the_ground(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer", whose end passed.
    When: the orchestrator finds it short of its Cut, resumes it with the ground, and it gives done
    again.
    Then: the guard lets the resume through, passes its second end, and gives the evaluators'
    starts due."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    w.made(b, walk, generator, cut)
    w.reached(b, generator, "done", "Made.")
    grounds = "invoicer/render.py has no hints, though the user decided each file."
    assert not walk.c.resume(generator, w.resume_text(grounds)).blocked
    then = w.reached(b, generator, "done", "Made again.")
    assert w.cut_of(w.due_text(then.said, "evaluator"))["deliverable"] == w.HINTS_PATH


@pytest.mark.supports("S1", "Round", "Made", "Answers", "tree.py")
def test_the_round_gives_each_evaluators_answers_and_what_the_generator_made(b: Bench) -> None:
    """Given: the first round of "Type hints in each file of invoicer": its Made, and each
    evaluator's Answers, every condition good.
    When: the orchestrator runs tree.py round invoicer.
    Then: it gives one round, numbered 1, with the Made as the generator wrote it, and the Answers
    of each evaluator."""
    walk, cut, cuts = w.first_round(b)
    [round_] = w.printed(walk.c.bash(b.tree("round", cut["deliverable"])))
    assert round_["number"] == 1
    assert round_["made"]["settled"] == [w.DECIMAL]
    assert len(round_["answers"]) == len(cuts)
    asked = sorted(c for each in cuts for c in each["conditions"])
    answered = sorted(g["question"] for each in round_["answers"] for g in each["good"])
    assert answered == asked


@pytest.mark.supports("S1", "More kept", "tree-keeper", "Decision")
def test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator(b: Bench) -> None:
    """Given: the first round of "Type hints in each file of invoicer", with N2 in more.
    When: the orchestrator judges the people fall short by it, and the tree-keeper writes the
    decision it changes under N2 with the more to keep.
    Then: tree.py write keeps the more, and the guard gives the generator's start due again, its
    Cut holding the decision and the More kept, with its Made in a new round."""
    good_when = "A caller's editor shows the type of each argument as they type the call."
    walk, cut, _ = w.first_round(b, {"N2": good_when})
    decision = {"about": "what the hints name", "decided": "every argument", "by": "reasoning"}
    nodes = {"deliverables/0/necessary_conditions/1/decisions/0": decision}
    more = [{"deliverable": w.HINTS_PATH, "condition": "N2", "good_when": good_when}]
    w.keeper_writes(b, walk, "The people fall short by N2.", {"nodes": nodes, "more": more})
    _, again = w.generator_started(walk)
    assert again["cut"]["more"] == [{"condition": "N2", "good_when": good_when}]
    assert decision["decided"] in [d["decision"]["decided"] for d in again["cut"]["decisions"]]
    assert os.path.dirname(again["made"]) != os.path.dirname(cut["made"])


@pytest.mark.supports("S1", "adapters", "S3")
def test_no_generator_start_is_due_while_every_deliverable_doing_waits(b: Bench) -> None:
    """Given: a plan of "Type hints in each file of invoicer" alone, made, judged good, and put up
    for the user's sign-off.
    When: the orchestrator ends its turn with the sign-off.
    Then: the guard lets the turn end, and gives no generator's start due, as no work waits."""
    walk, _ = w.sign_off_put_up(b, w.hints_plan())
    stopped = walk.c.stop(f'"{w.HINTS}", for your sign-off:')
    assert not stopped.blocked
    assert "Start `rn:generator`" not in walk.said + stopped.said
