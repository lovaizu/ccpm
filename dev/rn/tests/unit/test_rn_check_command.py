"""The unit cases of check/command.py, check's command line as a role runs it before it ends:
a result that holds for each role, the fixer's in its Fix among them; one with two faults, each on
a line; none written; a result that isn't JSON; a Cut out of its schema or missing, a schema that
can't be read, and a role of none, each of which check couldn't check by; and arguments other than
two. Each runs from the user's repository's top, with the Cut's path from there, as a role runs
rn's scripts from there, while the case's process runs in another folder."""

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
    """The repository's top, the run's worktree holding the command, the command's Round
    content-1, and its Fix fix-2, each from the repository's top."""

    def __init__(self, repository: str):
        self.repository = repository
        self.worktree = rn_files.worktree_of(repository, NAME)
        folder = rn_files.run_folder(repository, NAME, rn_files.walkthrough_tree(NAME))
        self.round = os.path.relpath(rn_files.round_of(folder, COMMAND, "content", 1), repository)
        self.fix = os.path.relpath(rn_files.round_of(folder, COMMAND, "fix", 2), repository)
        self.folder = os.path.relpath(folder, repository)
        write_files(self.worktree, {COMMAND: f"{LINE}\n"})

    def cut(self, role: str) -> str:
        """Writes the role's Cut of the command in the Round, or the fixer's in the Fix, and gives
        its path from the repository's top."""
        if role == "fixer":
            cut: dict[str, Any] = {
                "deliverable": rn_files.walkthrough_tree(NAME)["deliverables"][1],
                "worktree": os.path.relpath(self.worktree, self.repository),
                "paths": [os.path.relpath(os.path.join(self.worktree, COMMAND), self.repository)],
                "problem": {"source": "put-up", "words": "lint: a line ends in a space"},
                "run": self.folder,
                "fix": self.fix,
            }
            path = os.path.join(self.fix, "fixer-cut.json")
            rn_files.write_json(os.path.join(self.repository, path), cut)
            return path
        if role == "generator":
            cut = {
                "goal": rn_files.GOAL,
                "language": rn_files.DELIVERABLES_LANGUAGE,
                "deliverable": rn_files.walkthrough_tree(NAME)["deliverables"][1],
                "worktree": os.path.relpath(self.worktree, self.repository),
                "inputs": [],
                "best_practice": os.path.relpath(
                    os.path.join(rn_files.PRACTICES, "light"), self.repository
                ),
                "template": None,
                "stage": "content",
                "number": 1,
                "round": self.round,
                "trial": "/tmp/rn-trial-x",
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
        """Writes the role's result in the Round, or the fixer's in the Fix, and gives its path
        from the repository's top."""
        path = os.path.join(self.fix if role == "fixer" else self.round, f"{role}.json")
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
    "fixer": {"result": "fixed", "files": [COMMAND]},
}


@pytest.mark.parametrize("role", ["generator", "evaluator", "fixer"])
def test_a_result_that_holds_its_cut_gives_0_printing_nothing(run: Run, role: str):
    """Given the role's Cut and a result that holds it beside it
    When check runs on the role and the Cut
    Then it gives 0, printing nothing"""
    cut = run.cut(role)
    run.result(role, GOOD[role])
    assert main([role, cut], run.repository, rn_files.RN) == (0, "", "")


def test_an_evaluators_result_with_two_faults_gives_1_with_each_a_line(run: Run):
    """Given the evaluator's Cut and its judged answering N1 alone
    When check runs on it
    Then it gives 1, with N2 and N3 each named on a line of its own"""
    cut = run.cut("evaluator")
    run.result("evaluator", rn_files.judged([("N1", [LINE])]))
    code, out, err = main(["evaluator", cut], run.repository, rn_files.RN)
    lines = (out + err).splitlines()
    assert code == 1
    assert any("N2" in each and "N3" not in each for each in lines)
    assert any("N3" in each and "N2" not in each for each in lines)


def test_a_fixer_that_wrote_no_result_gives_1_with_where_it_writes_one_in_its_fix(run: Run):
    """Given the fixer's Cut, and no result beside it
    When check runs on it
    Then it gives 1, naming the path of <fix>/fixer.json"""
    cut = run.cut("fixer")
    written = os.path.join(run.fix, "fixer.json")
    assert main(["fixer", cut], run.repository, rn_files.RN) == (
        1,
        f"{written}: no result is written there; write it before you end\n",
        "",
    )


def test_a_result_that_isnt_json_gives_1_naming_it(run: Run):
    """Given the generator's Cut, and a result beside it that isn't JSON
    When check runs on it
    Then it gives 1, its output starting `check: ` and naming the result's path, as the role
    mends what it wrote"""
    cut = run.cut("generator")
    written = os.path.join(run.round, "generator.json")
    write_files(run.repository, {written: "{made"})
    code, out, err = main(["generator", cut], run.repository, rn_files.RN)
    assert code == 1
    assert (out + err).startswith(f"check: {written}: ")


def test_a_cut_out_of_its_schema_gives_2_saying_what_check_py_couldnt_check(run: Run):
    """Given a generator's Cut with no goal, and a result that would hold it
    When check runs on it
    Then it gives 2, saying that it couldn't check the generator's result, as its Cut leaves its
    form at goal"""
    cut = run.cut("generator")
    given = rn_files.read_json(os.path.join(run.repository, cut))
    del given["goal"]
    rn_files.write_json(os.path.join(run.repository, cut), given)
    run.result("generator", GOOD["generator"])
    code, out, err = main(["generator", cut], run.repository, rn_files.RN)
    assert code == 2
    assert (out + err).startswith(
        f"check: couldn't check the generator's result, as its Cut {cut} leaves the form of"
        " a generator's Cut at "
    )
    assert "goal" in out + err


def test_a_cut_that_isnt_there_gives_2_saying_what_check_py_couldnt_check(run: Run):
    """Given no Cut at the path given
    When check runs on it
    Then it gives 2, saying that it couldn't check the generator's result, as its Cut, by its
    path, can't be read"""
    missing = os.path.join(run.round, "generator-cut.json")
    code, out, err = main(["generator", missing], run.repository, rn_files.RN)
    assert code == 2
    assert (out + err).startswith(
        f"check: couldn't check the generator's result, as its Cut {missing} can't be read"
        " as JSON: "
    )


def test_a_schema_that_cant_be_read_gives_2_saying_what_check_py_couldnt_check(
    run: Run, tmp_path: Any
):
    """Given the generator's Cut and its result, and an rn folder that holds no schema
    When check runs on it
    Then it gives 2, saying that the schema can't be read, by its path"""
    cut = run.cut("generator")
    run.result("generator", GOOD["generator"])
    bare = os.path.join(str(tmp_path), "rn")
    os.makedirs(bare)
    code, out, err = main(["generator", cut], run.repository, bare)
    assert code == 2
    assert (out + err).startswith("check: ")
    assert "generator-cut.schema.json: the schema can't be read: " in out + err


def test_a_role_of_neither_gives_2_saying_what_check_py_couldnt_check(run: Run):
    """Given the generator's Cut and its result
    When check runs on the role orchestrator, none of generator, evaluator, and fixer
    Then it gives 2, saying that it couldn't check a result of the role, as it checks only the
    generator's, the evaluator's, and the fixer's"""
    cut = run.cut("generator")
    run.result("generator", GOOD["generator"])
    code, out, err = main(["orchestrator", cut], run.repository, rn_files.RN)
    assert code == 2
    assert out + err == (
        "check: couldn't check a result of 'orchestrator', as it checks only the generator's, the"
        " evaluator's, and the fixer's\n"
    )


def test_arguments_other_than_a_role_and_a_cut_give_2_with_the_usage(run: Run):
    """Given the run
    When check runs on three arguments
    Then it gives 2 with the usage"""
    code, out, err = main(["generator", "a.json", "b.json"], run.repository, rn_files.RN)
    assert code == 2
    assert USAGE in out + err
