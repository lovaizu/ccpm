"""The unit cases of tree/cut.py, what each role's Cut holds: the generator's, before the first
Round, after one with findings, of a condition held good and of one still short, with the user's
answer among its decisions, with none, one, and several inputs, for a refactor Round, and each
refusal; and the evaluator's, with only what the deliverable's people have, of a deliverable with
more paths, and each refusal. Each path of a Cut is from the folder the conversation works in, the
top of the user's repository."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any
from urllib.parse import quote

import pytest
import rn_files
from fault import Wrong
from practice import Found
from repository.place import RunPlace
from rn_files import COMMAND, GOAL, GUIDE
from rounds.files import Round
from tree.cut import evaluator, generator

pytestmark = pytest.mark.xfail(strict=True, reason="tree/cut.py's bodies raise NotImplementedError")

NAME = "20261120-a-command-with-which-the"
LIGHT = os.path.join(rn_files.PRACTICES, "light")


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The top of the user's repository."""
    return os.path.realpath(str(tmp_path))


def run_of(repo: str) -> RunPlace:
    """The walkthrough's run in the repository."""
    return RunPlace(repo, NAME)


def round_at(repo: str, deliverable: str, stage: str = "content", number: int = 1) -> Round:
    """The deliverable's Round of the stage and number in the walkthrough's run."""
    folder = rn_files.round_of(rn_files.folder_of(repo, NAME), deliverable, stage, number)
    return Round(folder, deliverable, stage, number)


def from_top(repo: str, path: str) -> str:
    """The path as the Cut names it, from the repository's top, made absolute and normal."""
    return os.path.normpath(os.path.join(repo, path))


def walkthrough(**given: Any) -> dict[str, Any]:
    """The walkthrough's tree, read from its JSON."""
    return json.loads(json.dumps(rn_files.walkthrough_tree(NAME, **given)))


def found(kind: str) -> Found:
    """rn's best practice of the kind with its folder, as practice.kinds and practice.read find
    them."""
    return Found(os.path.join(rn_files.PRACTICES, kind), rn_files.practice(kind))


def trial_of(deliverable: str, stage: str, number: int) -> str:
    """The people's folder of the walkthrough's run's Round, named by the Round's folder within the
    run's Rounds, each / as -."""
    within = f"{quote(deliverable, safe='')}-{stage}-{number}"
    return os.path.join(tempfile.gettempdir(), f"rn-trial-{NAME}-{within}")


def in_worktree(repo: str, path: str) -> str:
    """The path in the run's worktree."""
    return os.path.join(rn_files.worktree_of(repo, NAME), path)


# generator


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
def test_the_first_rounds_cut_holds_the_node_its_input_and_no_findings(repo: str):
    """Given the walkthrough's tree, the command resting on invoicer's lines, and no Round before
    When the generator's Cut of the command's Round content-1 is made by the light best practice
    Then it holds the goal, the command's node as the tree holds it, the run's worktree, invoicer's
    lines in the worktree, light's folder, content, 1, the Round's folder, and no findings or last
    good"""
    the = walkthrough()
    got = generator(the, run_of(repo), round_at(repo, COMMAND), found("light"), (None, None))
    assert sorted(got) == sorted(
        [
            "goal",
            "deliverable",
            "worktree",
            "inputs",
            "best_practice",
            "stage",
            "number",
            "round",
            "findings",
            "last_good",
        ]
    )
    assert got["goal"] == GOAL
    assert got["deliverable"] == the["deliverables"][1]
    assert from_top(repo, got["worktree"]) == rn_files.worktree_of(repo, NAME)
    assert [from_top(repo, each) for each in got["inputs"]] == [
        in_worktree(repo, "invoicer/lines.py")
    ]
    assert from_top(repo, got["best_practice"]) == LIGHT
    assert (got["stage"], got["number"]) == ("content", 1)
    assert from_top(repo, got["round"]) == round_at(repo, COMMAND).folder
    assert (got["findings"], got["last_good"]) == (None, None)


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_the_next_rounds_cut_takes_the_findings_of_each_condition_not_good_as_given(repo: str):
    """Given the command's Round content-1, its generator good on N1, N2, and N3, its evaluator good
    on N2 and more on N1 and N3, and the tree holding N1 good and N2 and N3 not
    When the generator's Cut of Round content-2 is made
    Then its findings hold N2's good and N3's more word for word, none of N1, held good, and its
    last good the generator's good of content-1 as it gave it"""
    made = rn_files.made(
        [("N1", ["import sys"]), ("N2", ["print(1)"]), ("N3", ["x = 1"])], [COMMAND]
    )
    judged = rn_files.judged(
        [("N2", ["print(1)"])],
        [("N1", "The accountant reads the total."), ("N3", "The accountant reads the tax.")],
    )
    got = generator(
        walkthrough(command_good=["N1"]),
        run_of(repo),
        round_at(repo, COMMAND, number=2),
        found("light"),
        (made, judged),
    )
    assert got["findings"] == {
        "good": [{"condition": "N2", "lines": ["print(1)"]}],
        "more": [{"condition": "N3", "good_when": "The accountant reads the tax."}],
    }
    assert got["last_good"] == made["good"]
    assert (got["stage"], got["number"]) == ("content", 2)


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
def test_findings_of_conditions_each_held_good_leave_none(repo: str):
    """Given the guide's evaluator whose more names N1, and a tree that holds each of the guide's
    conditions good
    When the generator's Cut of its Round refactor-1 is made
    Then its findings hold no good and no more"""
    judged = rn_files.judged([("N2", ["a"]), ("N3", ["b"])], [("N1", "The accountant prints.")])
    got = generator(
        walkthrough(guide_good=True),
        run_of(repo),
        round_at(repo, GUIDE, "refactor", 1),
        found("refactor-doc"),
        (rn_files.made([], [GUIDE]), judged),
    )
    assert got["findings"] == {"good": [], "more": []}
    assert got["last_good"] == []


@pytest.mark.supports("test_a_generators_point_reaches_the_user_and_their_answer_resumes_it")
def test_the_cut_holds_the_users_answer_as_its_decision_by_user(repo: str):
    """Given a tree whose command's N1 holds the user's answer about the tax rate, and the
    generator's last result a point
    When the generator's Cut of the same Round, content-1, is made
    Then its deliverable holds the answer in N1 by user, and its findings none"""
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    the = walkthrough(command_decisions={"N1": [tax]})
    got = generator(
        the,
        run_of(repo),
        round_at(repo, COMMAND),
        found("light"),
        (rn_files.point(), None),
    )
    assert got["deliverable"]["necessary_conditions"][0]["decisions"] == [tax]
    assert got["findings"] is None


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
@pytest.mark.parametrize(
    "inputs",
    [[], [COMMAND], [COMMAND, "invoicer/lines.py", "invoicer/tax.py"]],
)
def test_the_cut_names_each_input_in_the_worktree_in_its_order(repo: str, inputs: list[str]):
    """Given a tree whose guide rests on none, on the command, or on the command and two of
    invoicer's files
    When the guide's generator's Cut is made by the readme best practice
    Then its inputs name each of them in the run's worktree, in the order the guide names them"""
    the = walkthrough()
    the["deliverables"][2]["inputs"] = inputs
    got = generator(the, run_of(repo), round_at(repo, GUIDE), found("readme"), (None, None))
    assert [from_top(repo, each) for each in got["inputs"]] == [
        in_worktree(repo, each) for each in inputs
    ]
    assert from_top(repo, got["best_practice"]) == os.path.join(rn_files.PRACTICES, "readme")


@pytest.mark.supports(
    "test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice"
)
def test_a_refactor_rounds_cut_names_the_refactor_best_practice(repo: str):
    """Given a tree whose guide holds each condition good
    When the generator's Cut of its Round refactor-1 is made by the refactor-doc best practice
    Then it names refactor-doc's folder, the stage refactor, and the number 1"""
    got = generator(
        walkthrough(guide_good=True),
        run_of(repo),
        round_at(repo, GUIDE, "refactor", 1),
        found("refactor-doc"),
        (None, None),
    )
    assert from_top(repo, got["best_practice"]) == os.path.join(rn_files.PRACTICES, "refactor-doc")
    assert (got["stage"], got["number"]) == ("refactor", 1)
    assert from_top(repo, got["round"]) == round_at(repo, GUIDE, "refactor", 1).folder


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
@pytest.mark.parametrize("path", [rn_files.plan_path(NAME), "invoicer/__main__", "docs/guide.txt"])
def test_the_generators_cut_refuses_a_round_of_no_open_deliverable(repo: str, path: str):
    """Given the walkthrough's tree, its plan done
    When the generator's Cut is made for a Round of the plan, or of a path near the command's or
    the guide's
    Then it refuses with Wrong"""
    with pytest.raises(Wrong):
        generator(
            walkthrough(),
            run_of(repo),
            round_at(repo, path),
            found("light"),
            (None, None),
        )


# evaluator


@pytest.mark.supports("test_the_evaluators_cut_holds_only_what_the_people_have")
def test_the_evaluators_cut_holds_only_what_the_people_have(repo: str):
    """Given the walkthrough's tree whose command holds the user's answer about the tax rate
    When the evaluator's Cut of the command's Round content-1 is made by the light best practice
    Then it holds the goal, the command's name and path alone, what light judges by, the run's
    worktree, the Round's folder, and the people's folder in the system's temporary folder, named
    by the run and the Round"""
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    the = walkthrough(command_decisions={"N1": [tax]})
    got = evaluator(the, run_of(repo), round_at(repo, COMMAND), found("light"))
    assert sorted(got) == ["deliverable", "goal", "judges_by", "round", "trial", "worktree"]
    assert got["goal"] == GOAL
    assert got["deliverable"] == {"name": rn_files.COMMAND_NAME, "path": COMMAND}
    assert got["judges_by"] == rn_files.judged_by("light")
    assert from_top(repo, got["worktree"]) == rn_files.worktree_of(repo, NAME)
    assert from_top(repo, got["round"]) == round_at(repo, COMMAND).folder
    trial = trial_of(COMMAND, "content", 1)
    assert os.path.normpath(got["trial"]) == trial
    assert rn_files.TAX_ANSWER not in json.dumps(got)


@pytest.mark.supports("test_the_evaluators_cut_holds_only_what_the_people_have")
def test_the_evaluators_cut_names_each_more_path_of_the_deliverable(repo: str):
    """Given a tree whose guide lies in more paths too
    When the evaluator's Cut of its Round refactor-2 is made by the readme best practice
    Then its deliverable holds the guide's name, path, and more paths, and it judges by readme, in
    a people's folder named by refactor-2"""
    the = walkthrough(guide_good=True)
    the["deliverables"][2]["more_paths"] = ["docs/images/"]
    got = evaluator(the, run_of(repo), round_at(repo, GUIDE, "refactor", 2), found("readme"))
    assert got["deliverable"] == {
        "name": rn_files.GUIDE_NAME,
        "path": GUIDE,
        "more_paths": ["docs/images/"],
    }
    assert got["judges_by"] == rn_files.judged_by("readme")
    trial = trial_of(GUIDE, "refactor", 2)
    assert os.path.normpath(got["trial"]) == trial


@pytest.mark.supports("test_the_evaluators_cut_holds_only_what_the_people_have")
def test_the_evaluators_cut_refuses_a_round_of_a_deliverable_done(repo: str):
    """Given the walkthrough's tree, its plan done
    When the evaluator's Cut is made for a Round of the plan
    Then it refuses with Wrong"""
    with pytest.raises(Wrong):
        evaluator(
            walkthrough(),
            run_of(repo),
            round_at(repo, rn_files.plan_path(NAME)),
            found("design-tree"),
        )
