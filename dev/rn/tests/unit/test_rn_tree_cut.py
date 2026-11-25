"""The unit cases of tree/cut.py, what each role's Cut holds: the generator's, before the first
Round, after one judged, holding the tree's decisions and the last good but no evaluator's
findings, with several inputs and its kind's template, for a refactor Round, and each refusal; the
evaluator's, with only what the deliverable's people have, of a deliverable with more paths, and
refused for a deliverable done; and the fixer's, of an open deliverable and of a done one with more
paths, holding only its node, paths, problem, and folders, and refused for a path of no deliverable
and a Fix with no problem. Each path of a Cut is from the folder the conversation works in, the
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
from practice import Found, kinds
from repository.place import RunPlace
from rn_files import COMMAND, GOAL, GUIDE
from rounds.files import Fix, Round
from tree.cut import evaluator, fixer, generator

NAME = "20261120-a-command-with-which-the"
LIGHT = os.path.join(rn_files.PRACTICES, "light")
# The folder of each kind's best practice, rn's own, as practice.kinds finds them.
KINDS = kinds(rn_files.RN, os.path.join(rn_files.RN, "no-worktree"))


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


def test_the_first_rounds_cut_holds_the_node_its_input_and_no_last_good(repo: str):
    """Given the walkthrough's tree, the command resting on invoicer's lines, and no Round before
    When the generator's Cut of the command's Round content-1 is made by the light best practice
    Then it holds the goal, the deliverables' language, the command's node as the tree holds it,
    the run's worktree, invoicer's lines in the worktree, light's folder, no template, as light's
    folder holds none, content, 1, the Round's
    folder, the people's folder in the system's temporary folder, named by the run and the Round,
    and no last good, and no findings, as the generator mends by its decisions alone"""
    the = walkthrough()
    got = generator(the, run_of(repo), round_at(repo, COMMAND), KINDS, None)
    assert sorted(got) == sorted(
        [
            "goal",
            "language",
            "deliverable",
            "worktree",
            "inputs",
            "best_practice",
            "template",
            "stage",
            "number",
            "round",
            "trial",
            "last_good",
        ]
    )
    assert got["goal"] == GOAL
    assert got["language"] == rn_files.DELIVERABLES_LANGUAGE
    assert got["deliverable"] == the["deliverables"][1]
    assert from_top(repo, got["worktree"]) == rn_files.worktree_of(repo, NAME)
    assert [from_top(repo, each) for each in got["inputs"]] == [
        in_worktree(repo, "invoicer/lines.py")
    ]
    assert from_top(repo, got["best_practice"]) == LIGHT
    assert got["template"] is None, "light's folder holds no template"
    assert (got["stage"], got["number"]) == ("content", 1)
    assert from_top(repo, got["round"]) == round_at(repo, COMMAND).folder
    assert os.path.normpath(got["trial"]) == trial_of(COMMAND, "content", 1)
    assert got["last_good"] is None


def test_the_next_rounds_cut_holds_the_trees_decisions_and_the_last_good_alone(repo: str):
    """Given the command's Round content-1, its generator good on N1, N2, and N3, and the tree
    holding N1 good and, in N3, the remedy that the pruner kept of the evaluator's finding
    When the generator's Cut of Round content-2 is made
    Then its deliverable is the command's node as the tree holds it, the remedy among N3's
    decisions, it holds no findings, and its last good is the generator's good of content-1 as it
    gave it"""
    made = rn_files.made(
        [("N1", ["import sys"]), ("N2", ["print(1)"]), ("N3", ["x = 1"])], [COMMAND]
    )
    remedy = rn_files.decision("the tax", "The invoice shows the tax on its own line.", "reasoning")
    the = walkthrough(command_good=["N1"], command_decisions={"N3": [remedy]})
    got = generator(the, run_of(repo), round_at(repo, COMMAND, number=2), KINDS, made)
    assert "findings" not in got
    assert got["deliverable"] == the["deliverables"][1]
    assert got["deliverable"]["necessary_conditions"][2]["decisions"] == [remedy]
    assert got["last_good"] == made["good"]
    assert (got["stage"], got["number"]) == ("content", 2)


def test_the_cut_names_each_input_in_the_worktree_in_its_order(repo: str):
    """Given a tree whose guide rests on the command and two of invoicer's files
    When the guide's generator's Cut is made by the readme best practice
    Then its inputs name each of them in the run's worktree, in the order the guide names them,
    and its template is the readme best practice's"""
    inputs = [COMMAND, "invoicer/lines.py", "invoicer/tax.py"]
    the = walkthrough()
    the["deliverables"][2]["inputs"] = inputs
    got = generator(the, run_of(repo), round_at(repo, GUIDE), KINDS, None)
    assert [from_top(repo, each) for each in got["inputs"]] == [
        in_worktree(repo, each) for each in inputs
    ]
    assert from_top(repo, got["best_practice"]) == os.path.join(rn_files.PRACTICES, "readme")
    assert from_top(repo, got["template"]) == os.path.join(
        rn_files.PRACTICES, "readme", "template.md"
    )


def test_a_refactor_rounds_cut_names_the_refactor_best_practice(repo: str):
    """Given a tree whose guide, of the kind readme, holds each condition good
    When the generator's Cut of its Round refactor-2 is made
    Then it names refactor-doc's folder, the readme template, as the guide keeps its kind's form
    while it's refactored, the stage refactor, and the number 2"""
    got = generator(
        walkthrough(guide_good=True),
        run_of(repo),
        round_at(repo, GUIDE, "refactor", 2),
        KINDS,
        None,
    )
    assert from_top(repo, got["best_practice"]) == os.path.join(rn_files.PRACTICES, "refactor-doc")
    assert from_top(repo, got["template"]) == os.path.join(
        rn_files.PRACTICES, "readme", "template.md"
    )
    assert (got["stage"], got["number"]) == ("refactor", 2)
    assert from_top(repo, got["round"]) == round_at(repo, GUIDE, "refactor", 2).folder


def test_the_generators_cut_refuses_a_round_of_no_open_deliverable(repo: str):
    """Given the walkthrough's tree, its plan done
    When the generator's Cut is made for a Round of the plan
    Then it refuses with Wrong"""
    with pytest.raises(Wrong):
        generator(
            walkthrough(),
            run_of(repo),
            round_at(repo, rn_files.plan_path(NAME)),
            KINDS,
            None,
        )


def test_the_generators_cut_refuses_a_tree_whose_goal_is_open(repo: str):
    """Given the walkthrough's tree whose goal is open, its decided null
    When the generator's Cut of the command's Round content-1 is made
    Then it refuses with Wrong saying that the goal is open and a new pruner writes it"""
    the = walkthrough()
    the["goal"] = {"decided": None}
    with pytest.raises(Wrong, match="goal is open; hand the request to a new pruner"):
        generator(the, run_of(repo), round_at(repo, COMMAND), KINDS, None)


# evaluator


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


def test_the_evaluators_cut_names_each_more_path_of_the_deliverable(repo: str):
    """Given a tree whose guide lies in more paths too
    When the evaluator's Cut of its Round content-2 is made by the readme best practice
    Then its deliverable holds the guide's name, path, and more paths, and it judges by readme, in
    a people's folder named by content-2"""
    the = walkthrough(guide_good=True)
    the["deliverables"][2]["more_paths"] = ["docs/images/"]
    got = evaluator(the, run_of(repo), round_at(repo, GUIDE, "content", 2), found("readme"))
    assert got["deliverable"] == {
        "name": rn_files.GUIDE_NAME,
        "path": GUIDE,
        "more_paths": ["docs/images/"],
    }
    assert got["judges_by"] == rn_files.judged_by("readme")
    trial = trial_of(GUIDE, "content", 2)
    assert os.path.normpath(got["trial"]) == trial


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


# fixer

PROBLEM = {"source": "final-check", "words": "The guide names the command by its old path."}


def fix_at(repo: str, deliverable: str, number: int, problem: Any = PROBLEM) -> Fix:
    """The deliverable's Fix of the number in the walkthrough's run, holding the problem, none
    where it's None."""
    folder = rn_files.round_of(rn_files.folder_of(repo, NAME), deliverable, "fix", number)
    os.makedirs(folder)
    if problem is not None:
        rn_files.write_json(os.path.join(folder, "problem.json"), problem)
    return Fix(folder, deliverable, number)


def test_the_fixers_cut_holds_its_node_paths_problem_and_folders_alone(repo: str):
    """Given the walkthrough's tree, and the command's fix-2 holding its problem
    When the fixer's Cut of fix-2 is made
    Then it holds the command's node as the tree holds it, the run's worktree, the command's path
    in it, the problem, the run's folder, and fix-2's folder, each path from the repository's top,
    and nothing else"""
    the = walkthrough()
    fix = fix_at(repo, COMMAND, 2)
    got = fixer(the, run_of(repo), fix)
    assert sorted(got) == ["deliverable", "fix", "paths", "problem", "run", "worktree"]
    assert got["deliverable"] == the["deliverables"][1]
    assert from_top(repo, got["worktree"]) == rn_files.worktree_of(repo, NAME)
    assert [from_top(repo, each) for each in got["paths"]] == [in_worktree(repo, COMMAND)]
    assert got["problem"] == PROBLEM
    assert from_top(repo, got["run"]) == rn_files.folder_of(repo, NAME)
    assert from_top(repo, got["fix"]) == fix.folder


def test_the_fixers_cut_of_a_done_deliverable_holds_its_node_and_each_more_path(repo: str):
    """Given the walkthrough's tree whose guide is done, keeping its conditions, with a more path
    docs/images/, and the guide's fix-3
    When the fixer's Cut of fix-3 is made
    Then it holds the guide's done node, and the guide's path then docs/images/ in the worktree"""
    the = walkthrough()
    done = rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme")
    done["more_paths"] = ["docs/images/"]
    the["deliverables"][2] = done
    got = fixer(the, run_of(repo), fix_at(repo, GUIDE, 3))
    assert got["deliverable"] == done
    assert [from_top(repo, each) for each in got["paths"]] == [
        in_worktree(repo, GUIDE),
        in_worktree(repo, "docs/images"),
    ]


def test_the_fixers_cut_refuses_a_fix_of_no_deliverable(repo: str):
    """Given the walkthrough's tree, and a Fix of invoicer/cli.py, no deliverable's path
    When the fixer's Cut is made
    Then it refuses with Wrong naming the path"""
    with pytest.raises(Wrong, match="invoicer/cli.py"):
        fixer(walkthrough(), run_of(repo), fix_at(repo, "invoicer/cli.py", 1))


def test_the_fixers_cut_refuses_a_fix_with_no_problem(repo: str):
    """Given the walkthrough's tree, and the command's fix-2 holding no problem
    When the fixer's Cut is made
    Then it refuses with Wrong naming the Fix's folder and saying to write it by tree fix"""
    fix = fix_at(repo, COMMAND, 2, problem=None)
    with pytest.raises(Wrong, match="holds no problem; write the Fix by tree fix"):
        fixer(walkthrough(), run_of(repo), fix)
