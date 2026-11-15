"""The unit cases of throwaway.py, which runs a deliverable's command in a throwaway copy, of rn's
two adapters, hooks/adapters/text.py and records.py, which give Lane a start's text and the results
kept, and of fault.py's end. A command tried turns on its exit code, 0 or another, on what it
changes, and on the folder it's tried from; a start's text on the folder, the role, and whether
work waits; the results kept on the words typed and on how many runs are left."""

from __future__ import annotations

import importlib.util
import io
import json
import os
from types import ModuleType
from typing import Any

import pytest
import throwaway
from fault import end
from record import form
from record.form import Entry, Kept
from tree import rounds

from dev.rn.tests.unit import rn_data as d

EMPTY = pytest.mark.xfail(strict=True, reason="throwaway.py and the adapters have empty bodies")


def adapter(name: str) -> ModuleType:
    """rn's adapter of the name, from hooks/adapters/, as Lane runs it."""
    path = os.path.join(d.RN, "hooks", "adapters", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"rn_adapter_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def a_round(tmp: Any) -> Any:
    """A run whose invoicer is doing, in its first round."""
    run = d.run_of(d.repository(str(tmp)))
    d.tree_written(run, d.with_status(d.walkthrough_tree(), "doing", "open"))
    d.write_json(os.path.join(run.worktree, rounds.made_path(run, "invoicer", True)), d.made())
    return run


@EMPTY
@pytest.mark.supports("test_a_command_tried_leaves_the_worktree_as_it_was_and_is_kept")
@pytest.mark.parametrize(("command", "code"), [("echo tried", 0), ("echo failed >&2; exit 3", 3)])
def test_a_command_tried_gives_its_own_exit_code_and_output(
    tmp_path: Any, command: str, code: int
) -> None:
    """Given: a run whose invoicer is in its first round.
    When: a command that gives 0, and one that gives 3 with what it printed to stderr, are tried.
    Then: each gives its own exit code and output, and the round's Try record keeps it."""
    run = a_round(tmp_path)
    given = throwaway.main(["invoicer", command], run.worktree)
    assert given[0] == code and ("tried" in given[1] or "failed" in given[2])
    with open(os.path.join(run.worktree, rounds.try_path(run, "invoicer")), encoding="utf-8") as f:
        assert command in f.read()


@EMPTY
@pytest.mark.supports("test_a_command_tried_leaves_the_worktree_as_it_was_and_is_kept")
def test_a_command_tried_changes_neither_the_worktree_nor_the_home(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run whose invoicer is in its first round, and a home folder.
    When: a command that writes a file in its folder and in $HOME is tried.
    Then: it gives 0, and neither the worktree nor the home holds the file."""
    run = a_round(tmp_path)
    home = os.path.join(tmp_path, "home")
    os.makedirs(home)
    monkeypatch.setenv("HOME", home)
    assert throwaway.main(["invoicer", 'touch here.txt "$HOME/home.txt"'], run.worktree)[0] == 0
    assert not os.path.exists(os.path.join(run.worktree, "here.txt"))
    assert os.listdir(home) == []


@EMPTY
@pytest.mark.supports("test_throwaway_py_refuses_a_folder_in_no_runs_worktree")
def test_a_command_tried_outside_a_runs_worktree_or_with_no_round_gives_1(tmp_path: Any) -> None:
    """Given: a repository's root, and a run whose invoicer/py.typed has no round.
    When: a command is tried from the root, and for invoicer/py.typed in the run.
    Then: each gives 1 with what's wrong, and runs nothing."""
    run = a_round(tmp_path)
    repo = os.path.dirname(os.path.dirname(os.path.dirname(run.worktree)))
    assert throwaway.main(["invoicer", "touch tried.txt"], repo)[0] == 1
    assert throwaway.main(["invoicer/py.typed", "touch tried.txt"], run.worktree)[0] == 1
    assert not os.path.exists(os.path.join(repo, "tried.txt"))


@EMPTY
@pytest.mark.supports("test_throwaway_py_refuses_a_folder_in_no_runs_worktree")
@pytest.mark.parametrize("argv", [[], ["invoicer"], ["invoicer", "echo", "more"]])
def test_a_command_line_out_of_form_gives_2_with_the_usage(tmp_path: Any, argv: list[str]) -> None:
    """Given: a run whose invoicer is in its first round.
    When: throwaway.py runs with no argument, a deliverable alone, or a command in more than one.
    Then: it gives 2 with the usage."""
    code, _, err = throwaway.main(argv, a_round(tmp_path).worktree)
    assert code == 2 and "usage" in err


def text(role: list[str], running: list[dict[str, Any]], cwd: str) -> tuple[int, str, str]:
    return adapter("text").main(role, io.StringIO(json.dumps({"running": running})), cwd)


@EMPTY
@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
def test_a_starts_text_is_its_cut_as_one_json_line_with_its_run_values(tmp_path: Any) -> None:
    """Given: a run whose invoicer is doing.
    When: the text of the generator's start is asked in its worktree, with no start running.
    Then: it gives 0, the text's first line the Cut as JSON, and its run values, its record and
    deliverable among them, as the Cut names them."""
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run, d.with_status(d.walkthrough_tree(), "doing", "open"))
    code, out, _ = text(["generator"], [], run.worktree)
    given = json.loads(out)
    cut = json.loads(given["text"].split("\n", 1)[0])
    assert code == 0 and cut["deliverable"] == "invoicer"
    assert (
        given["values"]["record"] == cut["record"] and given["values"]["deliverable"] == "invoicer"
    )


@EMPTY
@pytest.mark.supports("test_no_generator_start_is_due_while_every_deliverable_doing_waits")
def test_a_start_with_no_work_waiting_gives_why(tmp_path: Any) -> None:
    """Given: a run with no deliverable doing.
    When: the text of the generator's start is asked in its worktree.
    Then: it gives 0 with why no work waits, and no text."""
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run)
    code, out, _ = text(["generator"], [], run.worktree)
    assert code == 0 and set(json.loads(out)) == {"none"} and json.loads(out)["none"]


@EMPTY
@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_a_starts_text_outside_a_runs_worktree_gives_1_with_why(tmp_path: Any) -> None:
    """Given: a repository's root with no run.
    When: the text of the tree-keeper's start is asked there.
    Then: it gives 1 with why."""
    code, out, err = text(["tree-keeper"], [], d.repository(str(tmp_path)))
    assert (code, out) == (1, "") and err


@EMPTY
@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
@pytest.mark.parametrize("role", [[], ["generator", "evaluator"]])
def test_a_starts_text_without_one_role_gives_2(tmp_path: Any, role: list[str]) -> None:
    """Given: a run.
    When: the text of a start is asked with no role, or with two.
    Then: it gives 2 with the usage."""
    run = d.run_of(d.repository(str(tmp_path)))
    assert text(role, [], run.worktree)[0] == 2


def kept(words: str, cwd: str) -> tuple[int, str, str]:
    return adapter("records").main(io.StringIO(json.dumps({"words": words})), cwd)


def run_with_results(repo: str, name: str = d.NAME) -> Any:
    """A run of the name whose tree-keeper's start kept done, and whose generator's kept none."""
    run = d.run_of(repo, name)
    from tree import records

    keeper = records.new_record(run, "tree-keeper", [])
    form.add(os.path.join(run.worktree, keeper), Entry("tree-keeper", 1, None, "Read it."))
    form.keep(os.path.join(run.worktree, keeper), Kept("tree-keeper", "done"))
    generator = records.new_record(run, "generator", [])
    form.add(os.path.join(run.worktree, generator), Entry("generator", 1, None, "Read it."))
    return run


@EMPTY
@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_the_results_kept_of_the_run_of_the_worktree_are_given_in_order(tmp_path: Any) -> None:
    """Given: a run whose tree-keeper kept done and whose generator kept none.
    When: the results kept are asked in its worktree, with no words typed.
    Then: it gives 0 with the tree-keeper's done alone."""
    run = run_with_results(d.repository(str(tmp_path)))
    code, out, _ = kept("", run.worktree)
    assert code == 0 and json.loads(out) == {"results": [{"role": "tree-keeper", "result": "done"}]}


@EMPTY
@pytest.mark.supports("test_up_alone_at_the_root_picks_up_the_one_run_left")
@pytest.mark.parametrize(
    ("runs", "results"), [(0, []), (1, [{"role": "tree-keeper", "result": "done"}]), (2, [])]
)
def test_the_results_kept_at_the_root_are_the_one_run_lefts(
    tmp_path: Any, runs: int, results: list[Any]
) -> None:
    """Given: a repository with no run left, one, or two.
    When: the results kept are asked at its root, with no words typed.
    Then: it gives 0 with none, the one run's, and none."""
    repo = d.repository(str(tmp_path))
    for number in range(runs):
        run_with_results(repo, f"{d.TODAY}-run-{number}")
    code, out, _ = kept("", repo)
    assert code == 0 and json.loads(out) == {"results": results}


@EMPTY
@pytest.mark.supports("test_words_after_up_start_a_new_run_beside_a_run_left")
def test_words_typed_give_no_results_whatever_runs_are_left(tmp_path: Any) -> None:
    """Given: a run with results kept.
    When: the results kept are asked in its worktree with words typed after /rn:up.
    Then: it gives 0 with none, as the words are a request."""
    run = run_with_results(d.repository(str(tmp_path)))
    code, out, _ = kept("a README for invoicer", run.worktree)
    assert code == 0 and json.loads(out) == {"results": []}


@EMPTY
@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
@pytest.mark.parametrize("given", ["not JSON", "{}", '{"words": 1}'])
def test_input_out_of_form_gives_1_with_why(tmp_path: Any, given: str) -> None:
    """Given: a run with results kept.
    When: the results kept are asked with input that isn't JSON, lacks the words, or gives words
    that aren't text.
    Then: it gives 1 with why."""
    run = run_with_results(d.repository(str(tmp_path)))
    code, out, err = adapter("records").main(io.StringIO(given), run.worktree)
    assert (code, out) == (1, "") and err


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
def test_a_command_ends_with_what_its_main_gave(capsys: pytest.CaptureFixture[str]) -> None:
    """Given: what a command's main gave: exit 1, a line on stdout, and a line on stderr.
    When: the command ends with it.
    Then: it writes each line where it goes, and exits 1."""
    with pytest.raises(SystemExit) as ended:
        end((1, "printed\n", "said\n"))
    assert ended.value.code == 1
    assert capsys.readouterr() == ("printed\n", "said\n")
