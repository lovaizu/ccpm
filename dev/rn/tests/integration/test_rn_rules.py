"""The integration cases of the rules of Solution strategy: for each rule, a case where rn's parts
keep it, which fails where the fixture `broken` takes out the part that holds it, as
integration/conftest.py's RULES names that part."""

from __future__ import annotations

import json
import os
import shutil

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench


@pytest.mark.supports("Drawn out along the design tree", "S1", "Cut", "guard")
def test_a_role_starts_with_only_the_cut_that_tree_py_gave_for_it(b: Bench, broken: None) -> None:
    """Given: the walkthrough's plan signed off, with the user's decision under the command and
    none under the guide.
    When: the orchestrator starts the generator with the design tree whole as its text, then with
    the text that the guard gives due.
    Then: the guard stops the first start, and the Cut of the second holds only the goal, the
    deliverable's name and inputs, its own decisions, and its More kept."""
    walk = w.planned(b)
    whole = json.dumps(w.tree_in(walk))
    stopped, agent = walk.c.start("rn:generator", whole, "generator")
    assert stopped.blocked and agent is None
    _, cut = w.generator_started(walk)
    values = {"record", "deliverable", "kind", "best_practice", "refactor", "made"}
    assert set(cut) == values | {"cut"}, "the Cut holds nothing of the tree beside its part"
    assert set(cut["cut"]) == {"goal", "name", "inputs", "decisions", "more"}
    paths = [each["decision"]["path"] for each in cut["cut"]["decisions"]]
    assert paths and all(p.startswith("deliverables/0/") for p in paths)


@pytest.mark.supports("Drawn out along the design tree", "S1", "Cut", "tree-keeper")
def test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at(
    b: Bench, broken: None
) -> None:
    """Given: the command, which takes pyproject.toml as its input, made, signed off, and marked
    done; then pyproject.toml changed, and the user's decision on how the tax rate is given
    changed, which the tree-keeper writes with the deliverable open again, with no More, as the
    rounds start again from the design.
    When: the orchestrator starts the generator with the text that the guard gives due.
    Then: its Cut holds only its part of the tree and the commit that marked the deliverable done,
    from which git gives the input's change since then."""
    walk, _ = w.sign_off_put_up(b, w.plan(w.command_from_pyproject()))
    done = {"nodes": {"deliverables/0": w.command_done()}, "more": []}
    w.approved(b, walk, "The user signed it off.", done)
    done_at = w.last_tree_commit(walk.run["worktree"], walk.run["folder"])
    w.pyproject_changed(walk.run["worktree"])
    again = w.command_from_pyproject(w.OR_THE_DEFAULT)
    change = {"nodes": {"deliverables/0": again}, "more": []}
    w.keeper_writes(
        b, walk, "The user lets the rate default to pyproject.toml's.", change, w.OR_THE_DEFAULT
    )
    _, cut = w.generator_started(walk)
    values = {"record", "deliverable", "kind", "best_practice", "refactor", "made"}
    assert set(cut) == values | {"cut"}, "the Cut holds nothing of the tree beside its part"
    assert set(cut["cut"]) == {"goal", "name", "inputs", "decisions", "more", "done_at"}
    assert cut["cut"]["done_at"] == done_at
    changed = w.git(walk.run["worktree"], "diff", cut["cut"]["done_at"], "--", "pyproject.toml")
    assert all(f"+{line}" in changed for line in w.RATE_SET.strip().splitlines())


@pytest.mark.supports("Every step by best practice", "S1", "record.py", "Record", "guard")
def test_an_end_whose_record_lacks_a_practice_is_held_with_it(b: Bench, broken: None) -> None:
    """Given: the generator of the command, which made it and wrote its Made, but recorded every
    practice of the code best practice save N4.1.
    When: it gives done and ends.
    Then: the guard holds its end, and the check its stop names gives code's N4.1, and once the
    generator records N4.1 and carries out again each step after making, as a practice comes
    before the steps it shapes, and ends again, the guard passes the end."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    w.made(b, walk, generator, cut)
    record = os.path.join(walk.run["worktree"], cut["record"])
    with open(record, encoding="utf-8") as f:
        held = json.load(f)
    held["entries"] = [
        e for e in held["entries"] if (e["of"], e.get("practice")) != ("code", "N4.1")
    ]
    with open(record, "w", encoding="utf-8") as f:
        json.dump(held, f)
    ended, _ = w.give(b, generator, "done", "Made.")
    assert "N4.1" in w.lacks_of(generator, ended, "done", cut)
    after = [("code", "N4.1", "Typed each module.")]
    after += [
        ("generator", str(n), "Carried out again after N4.1.")
        for n in w.steps_of(b.rn, w.prompt_file("generator"))[4:]
    ]
    for what, number, words in after:
        assert generator.bash(b.record("add", cut["record"], what, number, words)).exit_code == 0
    again, _ = generator.end("Made.")
    assert not again.blocked, again.said


@pytest.mark.supports("Every item handled", "S1", "Made", "record.py")
def test_a_made_that_leaves_out_a_decision_of_the_cut_is_held_with_it(
    b: Bench, broken: None
) -> None:
    """Given: the generator of the command, which recorded each step and practice and wrote a Made
    that names none of the decisions of its Cut.
    When: it gives done and ends.
    Then: the guard holds its end, and the check its stop names gives the path of the user's
    decision on how the tax rate is given."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    w.made(b, walk, generator, cut, every_item=False)
    ended, _ = w.give(b, generator, "done", "Made.")
    lacking = w.lacks_of(generator, ended, "done", cut)
    assert "deliverables/0/necessary_conditions/0/decisions/0" in lacking


@pytest.mark.supports("Judged by the people it's for", "S1", "evaluator", "Cut")
def test_an_evaluator_starts_with_only_what_the_deliverables_people_have(
    b: Bench, broken: None
) -> None:
    """Given: the generator of the command ended done.
    When: the orchestrator starts each evaluator that the guard gives due.
    Then: each evaluator's Cut holds only its record, the deliverable, its name, its best
    practice, the IDs of its group, and where it writes its Answers: no goal, no decision, and no
    Made."""
    _, _, cuts = w.first_round(b)
    people = {"record", "deliverable", "name", "best_practice", "conditions", "answers"}
    assert cuts and all(set(cut) == people for cut in cuts)
    assert all(cut["name"] == w.COMMAND for cut in cuts)


@pytest.mark.supports("Signed off before it's built on", "S3", "Sign-off", "Deliverable")
def test_work_resting_on_the_plan_waits_until_the_user_signs_it_off(b: Bench, broken: None) -> None:
    """Given: the walkthrough's plan put up for the user's sign-off.
    When: the orchestrator starts a generator, then the user types /rn:ty, the sign-off is
    approved, and the tree-keeper writes it.
    Then: the guard stops the start before /rn:ty, as no deliverable is doing, and after it both
    deliverables are doing and the guard gives the generator's start due."""
    walk = w.plan_put_up(b)
    assert [d["status"] for d in w.tree_in(walk)["deliverables"]] == ["open", "open"]
    stopped, agent = walk.c.start("rn:generator", "Carry out your steps", "generator")
    assert stopped.blocked and agent is None
    wrote = w.approved(b, walk, "The user signed off the plan.")
    assert wrote["doing"] == [w.COMMAND_PATH, w.GUIDE_PATH]
    assert w.cut_of(w.due_text(walk.said, "generator"))["deliverable"] == w.COMMAND_PATH


@pytest.mark.supports("Back to the design tree on a problem", "S1", "More kept", "tree-keeper")
@pytest.mark.parametrize(
    ("nodes", "named"),
    [
        ({}, "deliverables/0/necessary_conditions/0/decisions/0"),
        (
            {"deliverables/1/necessary_conditions/0/decisions/0": w.LINE_NUMBER},
            "deliverables/1/necessary_conditions/0/decisions/0",
        ),
    ],
    ids=["no decision changed", "a decision of another deliverable"],
)
def test_a_more_kept_with_no_decision_changed_is_refused(
    b: Bench, broken: None, nodes: dict[str, object], named: str
) -> None:
    """Given: the first round of the command, with N2 in more.
    When: the tree-keeper writes the more of N2 of code to keep, naming the user's decision under
    the command with nothing changed, or one it adds under the guide, and gives refused.
    Then: tree.py write gives 1, naming the code best practice and N2, writes no decision, keeps no
    more, and the guard passes the tree-keeper's end with refused for the orchestrator to read."""
    walk, _, _ = w.first_round(b, {"N2": w.WRONG_LINE_NAMED})
    change = {"nodes": nodes, "more": [w.n2_more(named)]}
    assert not walk.c.resume(walk.keeper, w.resume_text("Keep the more.", None, change)).blocked
    record = w.cut_of(w.due_text_of(walk.keeper))["record"]
    refused = walk.keeper.bash(b.fed(b.tree("write", record, "Keep the more."), change))
    assert refused.exit_code == 1 and "code" in refused.output and "N2" in refused.output
    assert len(w.tree_in(walk)["deliverables"][1]["necessary_conditions"][0]["decisions"]) == 0
    w.keeps(b, walk.keeper, record, "tree-keeper", ("design-tree",))
    then = w.reached(b, walk.keeper, "refused", "tree.py refused the more of N2 of code.")
    assert "refused" in then.said
    held = w.files_holding(walk.folder("rounds"), w.WRONG_LINE_NAMED)
    assert not [p for p in held if os.path.basename(p) == "more.json"]


@pytest.mark.supports("The design tree reviewed each turn", "S1", "Best practice")
def test_a_best_practice_made_on_the_run_is_taken_over_rns_own(b: Bench, broken: None) -> None:
    """Given: the walkthrough's plan signed off, and a code best practice made on the run in
    .rn/best-practices/code/ of the run's worktree, committed.
    When: the orchestrator starts the generator with the text that the guard gave before the best
    practice was made, then with the text that the guard gives due.
    Then: the guard stops the first start, and the Cut of the second names the best practice made
    on the run, not rn's own."""
    walk = w.planned(b)
    made = os.path.join(walk.run["worktree"], ".rn", "best-practices", "code")
    shutil.copytree(os.path.join(b.rn, "domain", "best-practices", "code"), made)
    w.git(walk.run["worktree"], "add", "-A")
    w.git(walk.run["worktree"], "commit", "-q", "-m", "The code best practice made on the run")
    stopped, agent = walk.c.start("rn:generator", w.due_text(walk.said, "generator"), "generator")
    assert stopped.blocked and agent is None
    walk.said = stopped.said
    _, cut = w.generator_started(walk)
    assert cut["best_practice"].rstrip("/").endswith(".rn/best-practices/code")


@pytest.mark.supports("Tried in a throwaway copy", "S1", "throwaway.py", "Try record")
def test_a_command_tried_leaves_the_worktree_as_it_was_and_is_kept(b: Bench, broken: None) -> None:
    """Given: the generator of the command running, at the end of its step 1, committed, as S1 has
    a role try a command after a step's commit.
    When: it tries a command that writes a file by throwaway.py.
    Then: throwaway.py gives the command's own exit code and output, the worktree holds no file it
    wrote, and the round's Try record keeps the command."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    assert generator.bash(b.tree("commit", cut["record"], "1")).exit_code == 0
    command = "touch tried.txt && echo tried"
    tried = generator.bash(b.throwaway(cut["deliverable"], command))
    assert tried.exit_code == 0 and "tried" in tried.output
    assert not os.path.exists(os.path.join(walk.run["worktree"], "tried.txt"))
    outside = ("--", ".", ":(exclude).rn")
    assert w.git(walk.run["worktree"], "status", "--porcelain", "-uall", *outside) == ""
    assert w.files_holding(walk.folder("rounds"), command)


@pytest.mark.supports("Tried in a throwaway copy", "S1", "guard")
def test_a_command_run_by_itself_is_stopped(b: Bench, broken: None) -> None:
    """Given: the generator of the command running.
    When: it runs a command of the deliverable by itself, not by throwaway.py.
    Then: the guard stops it."""
    walk = w.planned(b)
    generator, _ = w.generator_started(walk)
    assert generator.bash("touch tried.txt && echo tried").blocked


@pytest.mark.supports("The repository holds the work", "S1", "Place", "repository", "tree.py")
def test_each_steps_end_commits_the_work_with_its_place(b: Bench, broken: None) -> None:
    """Given: the generator of the command running, which wrote invoicer/__main__.py.
    When: it runs tree.py commit with its record and step 1.
    Then: the work's branch holds invoicer/__main__.py at its last commit, with a Place in the run's
    rounds/ that names the generator's record and step 1."""
    walk = w.planned(b)
    generator, cut = w.generator_started(walk)
    assert not generator.write(os.path.join(walk.run["worktree"], w.COMMAND_PATH), "").blocked
    assert generator.bash(b.tree("commit", cut["record"], "1")).exit_code == 0
    held = w.git(walk.run["worktree"], "ls-tree", "-r", "--name-only", "HEAD").split()
    assert w.COMMAND_PATH in held
    rounds = [p for p in held if p.startswith(f"{walk.run['folder']}/rounds/")]
    places = [json.loads(w.git(walk.run["worktree"], "show", f"HEAD:{p}")) for p in rounds]
    assert {"record": cut["record"], "step": 1} in [
        {"record": p.get("record"), "step": p.get("step")} for p in places if isinstance(p, dict)
    ]
