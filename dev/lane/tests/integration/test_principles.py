"""The integration cases of Lane's principles that no story's case holds: each takes the fixture
`broken`, which takes out the part that holds its principle where TRACE_BROKEN is 1, so that
trace.py sees the case fail without that part. A principle that a story's case holds is named by
that case."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from lane_example import (
    LANE,
    PROPOSAL,
    Repo,
    conversation,
    gives,
    lay,
    propose,
    put,
    read,
    reviewer_after_written,
    starts,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

STEP_2_LAID = (
    "2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`."
)


@pytest.mark.supports("The steps are the one source", "Step", "Laid", "up")
def test_up_again_on_unchanged_steps_proposes_each_step_without_the_text_lane_laid(
    broken: bool, laid: Repo
):
    """Given `changelog` laid with the walkthrough's Proposal, its steps unchanged since
    When up proposes the walkthrough's Proposal again
    Then lay.py print shows writer's step 2 with Lane's sentence once, as the steps alone give it"""
    up = conversation(laid, LANE, laid.plugin)
    up.type("/lane:up changelog")
    printed = propose(up, laid, PROPOSAL)
    assert printed.exit_code == 0
    assert printed.output.count("Run only `git log --oneline`. Run only") == 0
    assert STEP_2_LAID in printed.output


@pytest.mark.supports(
    "One type gives the sentence, the check, and the steps it suits", "Lane type", "Lane"
)
def test_the_sentence_a_role_reads_is_the_one_its_check_holds(broken: bool, repo: Repo):
    """Given `changelog` laid with the walkthrough's Proposal
    When writer runs `git status` in a Run
    Then the sentence that the guard gives writer is the one laid in writer's step 2, which names
    word for word the command that the check lets through"""
    lay(repo, PROPOSAL)
    conv = conversation(repo, repo.plugin)
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    stopped = writer.bash("git status")
    sentence = "Run only `git log --oneline`."
    assert stopped.blocked and stopped.said.startswith(f"changelog: {sentence}\n")
    assert STEP_2_LAID in read(os.path.join(repo.plugin, "agents", "writer.md"))
    assert not writer.bash("git log --oneline").blocked


@pytest.mark.supports("A stop gives the step back", "guard", "Call")
def test_each_stop_gives_the_role_the_sentence_of_the_step_it_breaks_and_what_it_may_run(
    broken: bool, run: Conversation
):
    """Given a Run of `changelog` in which writer runs
    When writer runs `git commit -am entries`
    Then the guard stops it, with the sentence of step 2 and the commands writer may run"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    stopped = writer.bash("git commit -am entries")
    assert stopped.blocked
    assert "Run only `git log --oneline`." in stopped.said
    assert "The commands you may run, each word for word:" in stopped.said


@pytest.mark.supports("The guard checks only the run", "guard", "Run")
def test_the_main_conversations_own_work_before_and_after_a_run_goes_unchecked(
    broken: bool, run: Conversation, laid: Repo
):
    """Given `changelog` laid with the walkthrough's Proposal
    When the main conversation starts reviewer before any run, and again after a Run whose
    reviewer gave `good` and whose skill gave `good`
    Then the guard lets both starts through"""
    before, _ = starts(run, "reviewer", "Review the entries.")
    reviewer = reviewer_after_written(run, laid)
    gives(laid, reviewer, "good")
    run.bash(f"python3 {os.path.join(laid.plugin, 'hooks', 'lane', 'result.py')} write good")
    run.stop("Done.")
    after, _ = starts(run, "reviewer", "Review the entries again.")
    assert not before.blocked and not after.blocked


@pytest.mark.supports("The laid plugin runs alone", "lay.py", "guard", "Laid")
def test_the_laid_plugin_runs_on_its_own_copy_of_lanes_code(broken: bool, repo: Repo):
    """Given `changelog` laid with the walkthrough's Proposal
    When the person types `/changelog:write` in a conversation that loads only `changelog`
    Then each hook entry that ran is the plugin's own hooks/lane/hook.py, and Lane names writer's
    start"""
    lay(repo, PROPOSAL)
    hooks = json.loads(read(os.path.join(repo.plugin, "hooks", "hooks.json")))["hooks"]
    commands = [
        " ".join([entry["command"], *entry.get("args", [])])
        for groups in hooks.values()
        for group in groups
        for entry in group["hooks"]
    ]
    assert commands and all("${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py" in c for c in commands)
    conv = conversation(repo, repo.plugin)
    typed = conv.type("/changelog:write")
    own = os.path.join(repo.plugin, "hooks", "lane", "hook.py")
    assert typed.ran and all(own in each for each in typed.ran)
    assert "changelog:writer" in typed.said


@pytest.mark.supports("Lane's part replaced whole", "lay.py", "Laid")
def test_laying_again_leaves_no_rule_of_a_step_that_no_longer_holds_it(broken: bool, repo: Repo):
    """Given `changelog` laid with the walkthrough's Proposal
    When the user takes writer's step 2 out, and Lane lays a Proposal without its Lane
    Then writer.md holds no `Run only `git log --oneline`.`, and lanes.json no run_only Lane"""
    lay(repo, PROPOSAL)
    writer = os.path.join(repo.plugin, "agents", "writer.md")
    text = read(writer).replace(STEP_2_LAID + "\n", "")
    put(
        repo.plugin,
        "agents/writer.md",
        text.replace("3. Write", "2. Write").replace("4. Reply", "3. Reply"),
    )
    lanes = [
        {**each, "step": each["step"] - 1} if each["role"] == "writer" else each
        for each in PROPOSAL["lanes"]
        if each["type"] != "run_only"
    ]
    lay(repo, {**PROPOSAL, "lanes": lanes})
    assert "Run only `git log --oneline`." not in read(writer)
    laid = json.loads(read(os.path.join(repo.plugin, "hooks", "lanes.json")))
    assert all(each["type"] != "run_only" for each in laid["lanes"])
