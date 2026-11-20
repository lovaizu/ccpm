"""The unit cases of check/command.py, check.py's command line as Lane's check at a role's end runs
it: for each role, a result that holds, one with faults, and none written; a generator's guide off
its kind's template, each place on a line, the worktree and the folder taken from the Cut and from
`cwd`, not from the process's own folder; a Cut out of its schema
or missing; a role of neither; and each count of arguments other than two. Each runs from the
user's repository's top, with the Cut's path from there, as Lane runs a check in the folder that the
conversation works in."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from check.command import USAGE, main
from repo_files import write_files

NAME = "20261120-a-command-with-which-the"
COMMAND = rn_files.COMMAND
LINE = "from invoicer.lines import parse_lines"


class Run:
    """The repository's top, the run's worktree holding the command, and the command's Round
    content-1 from the repository's top."""

    def __init__(self, repository: str):
        self.repository = repository
        self.worktree = rn_files.worktree_of(repository, NAME)
        folder = rn_files.run_folder(repository, NAME, rn_files.walkthrough_tree(NAME))
        self.round = os.path.relpath(rn_files.round_of(folder, COMMAND, "content", 1), repository)
        write_files(self.worktree, {COMMAND: f"{LINE}\n"})

    def cut(self, role: str, node: Any = None, kind: str = "light") -> str:
        """Writes the role's Cut in the Round, of the node and its kind for the generator, else
        the command's, and gives its path from the repository's top."""
        if role == "generator":
            node = node or rn_files.walkthrough_tree(NAME)["deliverables"][1]
            cut: dict[str, Any] = {
                "goal": rn_files.GOAL,
                "deliverable": node,
                "worktree": os.path.relpath(self.worktree, self.repository),
                "inputs": [],
                "best_practice": os.path.relpath(
                    os.path.join(rn_files.PRACTICES, kind), self.repository
                ),
                "stage": "content",
                "number": 1,
                "round": self.round,
                "findings": None,
                "last_good": None,
            }
        else:
            cut = {
                "goal": rn_files.GOAL,
                "deliverable": {"name": rn_files.COMMAND_NAME, "path": COMMAND},
                "judges_by": rn_files.judged_by("light"),
                "worktree": os.path.relpath(self.worktree, self.repository),
                "round": self.round,
                "trial": "/tmp/rn-trial-x",
            }
        path = os.path.join(self.round, f"{role}-cut.json")
        rn_files.write_json(os.path.join(self.repository, path), cut)
        return path

    def result(self, role: str, value: Any) -> str:
        """Writes the role's result in the Round, and gives its path from the repository's top."""
        path = os.path.join(self.round, f"{role}.json")
        rn_files.write_json(os.path.join(self.repository, path), value)
        return path


@pytest.fixture
def run(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Run:
    """The run of the case, the case's process in a folder beside the repository, so that only
    `cwd` gives the folder that the Cut's paths are from."""
    repository = os.path.join(os.path.realpath(str(tmp_path)), "invoicer")
    elsewhere = os.path.join(os.path.realpath(str(tmp_path)), "elsewhere")
    os.makedirs(elsewhere)
    monkeypatch.chdir(elsewhere)
    return Run(repository)


GOOD = {
    "generator": rn_files.made([("N1", [LINE])], [COMMAND]),
    "evaluator": rn_files.judged([("N1", [LINE]), ("N2", [LINE])], [("N3", "They print it.")]),
}


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
@pytest.mark.parametrize("role", ["generator", "evaluator"])
def test_a_result_that_holds_its_cut_gives_0_printing_nothing(run: Run, role: str):
    """Given the role's Cut and a result that holds it beside it
    When check.py runs on the role and the Cut
    Then it gives 0, printing nothing"""
    cut = run.cut(role)
    run.result(role, GOOD[role])
    assert main([role, cut], run.repository, rn_files.RN) == (0, "", "")


@pytest.mark.supports("test_a_generators_good_of_a_condition_its_deliverable_lacks_is_stopped")
def test_a_generators_result_with_a_fault_gives_1_with_the_fault(run: Run):
    """Given the generator's Cut and its made naming N9 good, which light doesn't hold
    When check.py runs on it
    Then it gives 1, its output naming N9 on a line"""
    cut = run.cut("generator")
    run.result("generator", rn_files.made([("N1", [LINE]), ("N9", [LINE])], [COMMAND]))
    code, out, err = main(["generator", cut], run.repository, rn_files.RN)
    assert code == 1
    assert any("N9" in each for each in (out + err).splitlines())


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
def test_an_evaluators_result_with_two_faults_gives_1_with_each_a_line(run: Run):
    """Given the evaluator's Cut and its judged answering N1 alone
    When check.py runs on it
    Then it gives 1, with N2 and N3 each named on a line of its own"""
    cut = run.cut("evaluator")
    run.result("evaluator", rn_files.judged([("N1", [LINE])]))
    code, out, err = main(["evaluator", cut], run.repository, rn_files.RN)
    lines = (out + err).splitlines()
    assert code == 1
    assert any("N2" in each and "N3" not in each for each in lines)
    assert any("N3" in each and "N2" not in each for each in lines)


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
@pytest.mark.parametrize("role", ["generator", "evaluator"])
def test_a_role_that_wrote_no_result_gives_1_with_where_it_writes_one(run: Run, role: str):
    """Given the role's Cut, and no result beside it
    When check.py runs on it
    Then it gives 1, naming the path of <round>/<role>.json"""
    cut = run.cut(role)
    code, out, err = main([role, cut], run.repository, rn_files.RN)
    assert code == 1
    assert os.path.join(run.round, f"{role}.json") in out + err


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
def test_a_cut_out_of_its_schema_gives_1_saying_whats_wrong(run: Run):
    """Given a generator's Cut with no goal, and a result that would hold it
    When check.py runs on it
    Then it gives 1, its output starting `check.py: ` and naming goal"""
    cut = run.cut("generator")
    given = rn_files.read_json(os.path.join(run.repository, cut))
    del given["goal"]
    rn_files.write_json(os.path.join(run.repository, cut), given)
    run.result("generator", GOOD["generator"])
    code, out, err = main(["generator", cut], run.repository, rn_files.RN)
    assert code == 1
    assert (out + err).startswith("check.py: ")
    assert "goal" in out + err


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
def test_a_cut_that_isnt_there_gives_1_naming_it(run: Run):
    """Given no Cut at the path given
    When check.py runs on it
    Then it gives 1, its output starting `check.py: ` and naming the path"""
    missing = os.path.join(run.round, "generator-cut.json")
    code, out, err = main(["generator", missing], run.repository, rn_files.RN)
    assert code == 1
    assert (out + err).startswith("check.py: ")
    assert missing in out + err


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
@pytest.mark.parametrize("role", ["orchestrator", "Generator"])
def test_a_role_of_neither_gives_1_saying_whats_wrong(run: Run, role: str):
    """Given the generator's Cut and its result
    When check.py runs on a role that is neither generator nor evaluator
    Then it gives 1, its output starting `check.py: `"""
    cut = run.cut("generator")
    run.result("generator", GOOD["generator"])
    code, out, err = main([role, cut], run.repository, rn_files.RN)
    assert code == 1
    assert (out + err).startswith("check.py: ")


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
@pytest.mark.parametrize("argv", [[], ["generator"], ["generator", "a.json", "b.json"]])
def test_arguments_other_than_a_role_and_a_cut_give_2_with_the_usage(run: Run, argv: list[str]):
    """Given the run
    When check.py runs on no argument, one, or three
    Then it gives 2 with the usage"""
    code, out, err = main(argv, run.repository, rn_files.RN)
    assert code == 2
    assert USAGE in out + err


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_a_generators_guide_off_its_template_gives_1_with_each_place_a_line(run: Run):
    """Given the guide's generator's Cut, of the kind readme, and its made naming the guide,
    which holds a heading and a paragraph alone, in the run's worktree that the Cut names
    When check.py runs on it from the repository's top
    Then it gives 1, with lines `docs/guide.md:<line>: <what>`, one for each place"""
    guide = rn_files.open_node(rn_files.GUIDE_NAME, rn_files.GUIDE, "readme", [COMMAND])
    write_files(run.worktree, {rn_files.GUIDE: "# Print an invoice\n\nType the command.\n"})
    cut = run.cut("generator", guide, "readme")
    run.result("generator", rn_files.made([], [rn_files.GUIDE]))
    code, out, err = main(["generator", cut], run.repository, rn_files.RN)
    places = [each for each in (out + err).splitlines() if each.startswith(f"{rn_files.GUIDE}:")]
    assert code == 1
    assert places
    assert all(each.split(":")[1].isdigit() for each in places)
