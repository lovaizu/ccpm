"""The integration cases of S5, a run in the order the user set: the guard starts the Run at the
skill's call, gives the main conversation each move due with the text of each start, lets through
only the starts and resumes the moves open, opens the Route after each Result, a waited command, or
a command typed at any moment, holds the main conversation's stop while a move is due, and ends the
Run where a move starts no more, with the Runs of two skills of the plugin side by side in one
conversation, each moved by its own Routes. The test plays the person, the main conversation, and
each subagent."""

from __future__ import annotations

import os
import stat
from typing import Any

import pytest
from claude_code import Conversation
from lane_example import (
    CARRY_OUT,
    NO_MORE,
    PROPOSAL,
    PROPOSAL_TWO_SKILLS,
    REVIEW,
    WRITE,
    Repo,
    conversation,
    gives,
    lane,
    lay,
    put,
    result_command,
    reviewer_after_written,
    route,
    start,
    starts,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

START_WRITER = "changelog: Start `changelog:writer` with `Carry out your steps`."
START_REVIEWER = "changelog: Start `changelog:reviewer` with `Carry out your steps`."


def adapter(repo: Repo, name: str, body: str) -> None:
    """An adapter of the test's own in the plugin's hooks/adapters/, an executable Python program
    with the body, which reads the role as `sys.argv[1]` and the Starts that run on stdin."""
    path = put(
        repo.plugin, f"hooks/adapters/{name}", "#!/usr/bin/env python3\nimport json, sys\n" + body
    )
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)


def laid_with(repo: Repo, proposal: dict[str, Any]) -> Conversation:
    """`changelog` laid with the Proposal, and a conversation that loads it."""
    lay(repo, proposal)
    return conversation(repo, repo.plugin)


def with_routes(*routes: dict[str, Any], **more: Any) -> dict[str, Any]:
    return {**PROPOSAL, "routes": list(routes), **more}


@pytest.mark.supports("S5", "guard", "Start", "Result", "Route", "Run", "result.py")
def test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more(
    run: Conversation, laid: Repo
):
    """Given `changelog` laid with the walkthrough's Proposal
    When the person types `/changelog:write`, and the main conversation starts each subagent that
    Lane names, writer gives `written`, reviewer `more`, writer `written`, and reviewer `good`
    Then Lane names each start as the walkthrough shows, and `Start no more subagents.` after
    `good`"""
    typed = run.type("/changelog:write")
    assert START_WRITER in typed.said
    _, writer = starts(run, "writer")
    assert writer
    assert gives(laid, writer, "written").said.endswith(
        "changelog: writer gave `written`. " + START_REVIEWER[len("changelog: ") :]
    )
    _, reviewer = starts(run, "reviewer")
    assert reviewer and START_WRITER[len("changelog: ") :] in gives(laid, reviewer, "more").said
    _, writer = starts(run, "writer")
    assert writer and "gave `written`" in gives(laid, writer, "written").said
    _, reviewer = starts(run, "reviewer")
    assert reviewer
    assert (
        "changelog: reviewer gave `good`. Start no more subagents."
        in gives(laid, reviewer, "good").said
    )


@pytest.mark.supports("S5", "guard", "Run", "result.py")
def test_the_skills_own_result_where_a_move_starts_no_more_ends_the_run(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` whose reviewer gave `good`, so that the move starts no more
    When the main conversation runs `result.py write good` and ends its turn, and then starts
    writer on its own
    Then the turn ends unheld, and the start passes unchecked, as the Run ended"""
    reviewer = reviewer_after_written(run, laid)
    gives(laid, reviewer, "good")
    assert run.bash(result_command(laid, "write", "good")).exit_code == 0
    assert not run.stop("The entries are written.").blocked
    after, _ = starts(run, "writer", "Write the entries again.")
    assert not after.blocked


@pytest.mark.supports("S5", "adapter", "Start")
def test_the_adapter_gives_a_start_its_text_and_run_values(repo: Repo):
    """Given `changelog` laid with an adapter of a start's text that gives writer
    `Write 0.2.0` and the value `version` `0.2.0`
    When the person types `/changelog:write`
    Then Lane names writer's start with `Write 0.2.0`, and lets that start through"""
    adapter(
        repo, "text", 'print(json.dumps({"text": "Write 0.2.0", "values": {"version": "0.2.0"}}))\n'
    )
    conv = laid_with(repo, {**PROPOSAL, "text_adapter": "text"})
    typed = conv.type("/changelog:write")
    assert "changelog: Start `changelog:writer` with `Write 0.2.0`." in typed.said
    started, writer = starts(conv, "writer", "Write 0.2.0")
    assert writer and not started.blocked


@pytest.mark.supports("S5", "adapter", "guard")
def test_an_adapter_failing_at_the_skills_call_gives_the_start_with_why_and_lets_the_call_run(
    repo: Repo,
):
    """Given `changelog` laid with an adapter of a start's text that exits 1, saying `no plan yet`
    When the person types `/changelog:write`
    Then the command runs unstopped, and Lane gives writer's start with `no plan yet`"""
    adapter(repo, "text", 'print("no plan yet", file=sys.stderr)\nsys.exit(1)\n')
    conv = laid_with(repo, {**PROPOSAL, "text_adapter": "text"})
    typed = conv.type("/changelog:write")
    assert not typed.blocked
    assert "changelog:writer" in typed.said and "no plan yet" in typed.said


@pytest.mark.supports("S5", "adapter", "guard")
def test_an_adapter_failing_at_a_later_single_move_gives_why_and_who_must_fix_it_in_its_place(
    repo: Repo,
):
    """Given `changelog` laid with an adapter of a start's text that gives writer its text and
    exits 1 for reviewer, saying `no entries`
    When writer gives `written`
    Then Lane gives the main conversation `no entries` and that the plugin's maker must fix it, in
    place of reviewer's start"""
    adapter(
        repo,
        "text",
        'if sys.argv[1] == "reviewer":\n    print("no entries", file=sys.stderr)\n    sys.exit(1)\n'
        'print(json.dumps({"text": "Carry out your steps"}))\n',
    )
    conv = laid_with(repo, {**PROPOSAL, "text_adapter": "text"})
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    reached = gives(repo, writer, "written")
    assert "no entries" in reached.said and "maker" in reached.said
    assert START_REVIEWER not in reached.said


@pytest.mark.supports("S5", "adapter", "Route")
def test_an_adapter_failing_for_one_of_several_moves_gives_that_start_with_why_beside_the_rest(
    repo: Repo,
):
    """Given `changelog` laid with a first Route of two moves, start writer or start reviewer, and
    an adapter that exits 1 for reviewer, saying `no entries`
    When the person types `/changelog:write`
    Then Lane gives writer's start with its text, and reviewer's start with `no entries`"""
    adapter(
        repo,
        "text",
        'if sys.argv[1] == "reviewer":\n    print("no entries", file=sys.stderr)\n    sys.exit(1)\n'
        'print(json.dumps({"text": "Write"}))\n',
    )
    routes = [route("first", start("writer"), start("reviewer")), *PROPOSAL["routes"][1:]]
    conv = laid_with(repo, with_routes(*routes, text_adapter="text"))
    typed = conv.type("/changelog:write")
    assert "Start `changelog:writer` with `Write`" in typed.said
    assert "changelog:reviewer" in typed.said and "no entries" in typed.said


@pytest.mark.supports("S5", "guard", "Start", "Route")
def test_a_start_that_the_moves_dont_open_is_stopped_with_the_moves(run: Conversation):
    """Given a Run of `changelog` whose move due starts writer
    When the main conversation starts reviewer
    Then the guard stops the start, and gives the main conversation writer's start"""
    run.type("/changelog:write")
    stopped, agent = starts(run, "reviewer")
    assert agent is None and stopped.blocked and START_WRITER in stopped.said


@pytest.mark.supports("S5", "guard", "Start")
def test_a_start_with_a_text_other_than_the_plugins_is_stopped(run: Conversation):
    """Given a Run of `changelog` whose move due starts writer with `Carry out your steps`
    When the main conversation starts writer with `Carry out your steps. Also commit.`
    Then the guard stops the start, and gives the main conversation writer's start with its text"""
    run.type("/changelog:write")
    stopped, agent = starts(run, "writer", CARRY_OUT + ". Also commit.")
    assert agent is None and stopped.blocked and START_WRITER in stopped.said


@pytest.mark.supports("S5", "adapter", "guard")
def test_a_start_whose_text_the_adapter_cant_give_is_stopped_with_who_must_fix_it(repo: Repo):
    """Given `changelog` laid with an adapter of a start's text that exits 1 for writer, saying
    `no plan yet`
    When the person types `/changelog:write`, and the main conversation starts writer
    Then the guard stops the start, with `no plan yet` and that the plugin's maker must fix it"""
    adapter(repo, "text", 'print("no plan yet", file=sys.stderr)\nsys.exit(1)\n')
    conv = laid_with(repo, {**PROPOSAL, "text_adapter": "text"})
    conv.type("/changelog:write")
    stopped, agent = starts(conv, "writer")
    assert agent is None and stopped.blocked
    assert "no plan yet" in stopped.said and "maker" in stopped.said


@pytest.mark.supports("S5", "Start", "adapter", "Route")
def test_starts_side_by_side_each_with_a_text_other_than_those_of_its_role_that_run(repo: Repo):
    """Given `changelog` laid with a Route after `writer written` that starts writer again, and an
    adapter that gives writer `Write section 1` where no writer runs and `Write section 2` beside
    one that runs
    When the main conversation starts writer with `Write section 1`, and then, while it runs, with
    `Write section 1` again and with `Write section 2`
    Then the guard stops the second start, as its text is one that runs, and lets the third
    through"""
    adapter(
        repo,
        "text",
        "running = json.load(sys.stdin)['running']\n"
        "print(json.dumps({'text': f'Write section {len(running) + 1}'}))\n",
    )
    routes = [route("first", start("writer"), start("writer")), *PROPOSAL["routes"][1:]]
    conv = laid_with(repo, with_routes(*routes, text_adapter="text"))
    conv.type("/changelog:write")
    first, one = starts(conv, "writer", "Write section 1")
    again, _ = starts(conv, "writer", "Write section 1")
    other, two = starts(conv, "writer", "Write section 2")
    assert one and not first.blocked
    assert again.blocked
    assert two and not other.blocked


@pytest.mark.supports("S5", "Start", "Route", "guard")
def test_a_resume_that_a_route_lists_counts_as_a_start_of_the_subagent_it_resumes(repo: Repo):
    """Given `changelog` laid with a Route after `reviewer more` that resumes writer
    When writer gives `written`, reviewer `more`, the main conversation resumes writer by
    SendMessage, and writer gives `written` again
    Then the guard lets the resume through, and Lane names reviewer's start after writer's second
    `written`"""
    routes = [
        route("first", start("writer")),
        route("writer written", start("reviewer")),
        route("reviewer more", {"kind": "resume", "role": "writer"}),
        route("reviewer good", NO_MORE),
    ]
    conv = laid_with(repo, with_routes(*routes))
    reviewer = reviewer_after_written(conv, repo)
    writer = conv.agents[0]
    gives(repo, reviewer, "more")
    resumed = conv.resume(writer, "Carry out your steps")
    assert not resumed.blocked
    assert START_REVIEWER[len("changelog: ") :] in gives(repo, writer, "written").said


@pytest.mark.supports("S5", "guard", "Run")
def test_a_resume_in_a_plugin_whose_routes_list_none_passes_and_moves_no_run(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog`, laid with the walkthrough's Proposal, which lists no resume,
    and writer gave `written`
    When the main conversation resumes writer by SendMessage to ask about an entry
    Then the guard lets the resume through, and reviewer's start is still the move due"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    gives(laid, writer, "written")
    resumed = run.resume(writer, "Why this entry?")
    assert not resumed.blocked
    stopped = run.stop("Waiting.")
    assert stopped.blocked and START_REVIEWER in stopped.said


@pytest.mark.supports("S5", "guard", "Route")
def test_a_resume_that_the_moves_dont_open_is_stopped_with_the_moves(repo: Repo):
    """Given `changelog` laid with a Route after `reviewer more` that resumes writer, and a Run
    whose move due starts reviewer
    When the main conversation resumes writer by SendMessage
    Then the guard stops the resume, and gives the main conversation reviewer's start"""
    routes = [
        route("first", start("writer")),
        route("writer written", start("reviewer")),
        route("reviewer more", {"kind": "resume", "role": "writer"}),
        route("reviewer good", NO_MORE),
    ]
    conv = laid_with(repo, with_routes(*routes))
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    gives(repo, writer, "written")
    resumed = conv.resume(writer, "Carry out your steps")
    assert resumed.blocked and START_REVIEWER in resumed.said


@pytest.mark.supports("S5", "Route", "guard")
def test_a_move_that_waits_for_a_command_is_due_once_the_person_types_it(repo: Repo):
    """Given `changelog` laid with a command `approve` that sets `disable-model-invocation: true`,
    and a Route after `reviewer good` that starts writer once the person types `/changelog:approve`
    When reviewer gives `good`, the main conversation ends its turn, and the person types
    `/changelog:approve`
    Then the turn ends unheld, and Lane names writer's start as the person types the command"""
    put(
        repo.plugin,
        "skills/approve/SKILL.md",
        "---\nname: approve\ndisable-model-invocation: true\n---\n\n## Steps\n\n1. Go on.\n",
    )
    routes = [
        *PROPOSAL["routes"][:3],
        route("reviewer good", start("writer", "/changelog:approve")),
    ]
    conv = laid_with(repo, with_routes(*routes))
    reviewer = reviewer_after_written(conv, repo)
    gives(repo, reviewer, "good")
    assert not conv.stop("Approve the entries with /changelog:approve.").blocked
    assert START_WRITER in conv.type("/changelog:approve").said


@pytest.mark.supports("S5", "Route", "guard")
def test_a_command_that_a_route_goes_after_opens_its_moves_while_each_subagent_runs_on(repo: Repo):
    """Given `changelog` laid with a command `pause` and a Route after `/changelog:pause` whose move
    starts no more, and a Run in which writer runs
    When the person types `/changelog:pause`, and writer then gives `written`
    Then Lane gives the main conversation `Start no more subagents.`, and writer's result opens no
    start of reviewer"""
    put(
        repo.plugin,
        "skills/pause/SKILL.md",
        "---\nname: pause\ndisable-model-invocation: true\n---\n\n## Steps\n\n1. Stop.\n",
    )
    conv = laid_with(repo, with_routes(*PROPOSAL["routes"], route("/changelog:pause", NO_MORE)))
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    paused = conv.type("/changelog:pause")
    assert "Start no more subagents." in paused.said
    reached = gives(repo, writer, "written")
    assert START_REVIEWER not in reached.said


@pytest.mark.supports("S5", "guard", "Start", "Result")
def test_a_subagent_that_ends_with_no_result_as_task_stop_stopped_it_opens_no_route(
    run: Conversation,
):
    """Given a Run of `changelog` in which writer runs
    When the main conversation stops writer by TaskStop
    Then Lane tells the main conversation that writer ended with no Result, and writer's start is
    due again"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    stopped = run.task_stop(writer)
    assert "writer" in stopped.said and "no result" in stopped.said.lower()
    held = run.stop("Writer stopped.")
    assert held.blocked and START_WRITER in held.said


@pytest.mark.supports("S5", "guard", "Run")
def test_the_main_conversation_stopping_while_a_start_is_due_and_none_runs_is_held(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` whose writer gave `written`, so that reviewer's start is due, and
    no subagent runs
    When the main conversation ends its turn to ask the person what to do
    Then the guard holds the stop, with reviewer's start, as the walkthrough shows"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    gives(laid, writer, "written")
    held = run.stop("Should I go on?")
    assert held.blocked and held.said == START_REVIEWER


@pytest.mark.supports("S5", "guard", "Run")
def test_the_main_conversation_may_stop_while_a_subagent_runs(run: Conversation):
    """Given a Run of `changelog` in which writer runs
    When the main conversation ends its turn
    Then the guard lets it stop, as writer's end will reach it"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    assert not run.stop("Writer is at work.").blocked


@pytest.mark.supports("S5", "guard", "Route")
def test_the_main_conversation_may_stop_where_a_move_waits_for_the_persons_reply(repo: Repo):
    """Given `changelog` laid with a Route after `reviewer good` that waits for the person's reply
    When reviewer gives `good`, and the main conversation ends its turn
    Then the guard lets it stop"""
    routes = [*PROPOSAL["routes"][:3], route("reviewer good", {"kind": "wait"})]
    conv = laid_with(repo, with_routes(*routes))
    reviewer = reviewer_after_written(conv, repo)
    gives(repo, reviewer, "good")
    assert not conv.stop("The entries are good. Shall I go on?").blocked


@pytest.mark.supports("S5", "Route", "guard")
def test_several_moves_let_the_skills_steps_choose_among_them_and_stop_any_other(repo: Repo):
    """Given `changelog` laid with a Route after `reviewer more` of two moves, start writer or
    start no more
    When reviewer gives `more`
    Then Lane gives both moves, lets writer's start through, and stops reviewer's"""
    routes = [
        *PROPOSAL["routes"][:2],
        route("reviewer more", start("writer"), NO_MORE),
        PROPOSAL["routes"][3],
    ]
    conv = laid_with(repo, with_routes(*routes))
    reviewer = reviewer_after_written(conv, repo)
    reached = gives(repo, reviewer, "more")
    assert "changelog:writer" in reached.said and "Start no more subagents." in reached.said
    other, _ = starts(conv, "reviewer")
    assert other.blocked
    chosen, _ = starts(conv, "writer")
    assert not chosen.blocked


@pytest.mark.supports("S5", "lane types", "Lane", "guard")
def test_a_lane_of_the_skill_holds_its_turns_end_until_the_plugins_command_gives_0(repo: Repo):
    """Given `changelog` laid with an ends_checked Lane on the skill's step 1 that runs
    `python3 check.py`, which exits 1 printing `CHANGELOG.md lacks [Unreleased]` until the file
    holds it, and a Run whose reviewer gave `good`
    When the main conversation ends its turn, and again once CHANGELOG.md holds `[Unreleased]`
    Then the guard holds the first end with the Lane's sentence and what the command printed, and
    lets the second end"""
    put(
        repo.root,
        "check.py",
        "import sys\nif '[Unreleased]' not in open('CHANGELOG.md').read():\n"
        "    print('CHANGELOG.md lacks [Unreleased]')\n    sys.exit(1)\n",
    )
    lanes = [*PROPOSAL["lanes"], lane("write", 1, "ends_checked", "python3 check.py")]
    conv = laid_with(repo, {**PROPOSAL, "lanes": lanes})
    reviewer = reviewer_after_written(conv, repo)
    gives(repo, reviewer, "good")
    conv.bash(result_command(repo, "write", "good"))
    held = conv.stop("Done.")
    assert held.blocked and "CHANGELOG.md lacks [Unreleased]" in held.said
    put(repo.root, "CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n")
    assert not conv.stop("Done.").blocked


START_NO_MORE = "Start no more subagents."


def two_skills(repo: Repo, proposal: dict[str, Any] = PROPOSAL_TWO_SKILLS) -> Conversation:
    """`changelog` with its second skill `review` beside `write`, laid with the Proposal, and a
    conversation that loads it."""
    put(repo.plugin, "skills/review/SKILL.md", REVIEW)
    return laid_with(repo, proposal)


@pytest.mark.supports("S5", "guard", "Run", "Start", "Result", "Route")
def test_runs_of_two_skills_go_on_side_by_side_each_moved_by_its_own_results(repo: Repo):
    """Given `changelog` laid with the skills `write` and `review`, and a Run of `write` in which
    writer runs in the background
    When the person types `/changelog:review`, the main conversation starts reviewer, which gives
    `more`, and writer then gives `written`
    Then Lane names reviewer's start for `review`, lets it through, names no more starts after
    reviewer's `more`, as the Routes of `review` say, and names reviewer's start after writer's
    `written`, as those of `write` say"""
    conv = two_skills(repo)
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    conv.stop("writer runs.")
    assert START_REVIEWER in conv.type("/changelog:review").said
    answer, reviewer = starts(conv, "reviewer")
    assert not answer.blocked and reviewer
    after_more = gives(repo, reviewer, "more").said
    assert START_NO_MORE in after_more and START_WRITER not in after_more
    assert START_REVIEWER in gives(repo, writer, "written").said


@pytest.mark.supports("S5", "guard", "Run", "Result", "result.py")
def test_the_skills_own_result_ends_only_the_run_of_the_skill_it_names(repo: Repo):
    """Given the Runs of `write` and `review` in one conversation, writer of `write` having given
    `written`, and reviewer of `review` having given `good`
    When the main conversation runs `result.py review good`, and ends its turn
    Then the guard lets the result through, and holds the stop with reviewer's start, as the Run of
    `write` goes on with that start due"""
    conv = two_skills(repo)
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    gives(repo, writer, "written")
    conv.type("/changelog:review")
    _, reviewer = starts(conv, "reviewer")
    assert reviewer
    gives(repo, reviewer, "good")
    assert not conv.bash(result_command(repo, "review", "good")).blocked
    stopped = conv.stop("Done.")
    assert stopped.blocked and START_REVIEWER in stopped.said


@pytest.mark.supports("S5", "guard", "Run")
def test_the_stop_is_held_while_one_runs_start_is_due_though_another_runs_subagent_runs(
    repo: Repo,
):
    """Given the Runs of `write` and `review` in one conversation, writer of `write` having given
    `written`, and reviewer of `review` running in the background
    When the main conversation ends its turn
    Then the guard holds the stop with reviewer's start of `write`, as no subagent of that Run
    runs"""
    conv = two_skills(repo)
    conv.type("/changelog:review")
    _, reviewer = starts(conv, "reviewer")
    assert reviewer
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    gives(repo, writer, "written")
    stopped = conv.stop("Waiting for reviewer.")
    assert stopped.blocked and START_REVIEWER in stopped.said


@pytest.mark.supports("S5", "guard", "Start", "Run")
def test_a_start_that_the_moves_of_two_runs_open_goes_to_the_run_that_began_first(repo: Repo):
    """Given a Run of `write` whose move due starts reviewer, and then a Run of `review`, whose
    first move starts reviewer too
    When the main conversation starts reviewer, which gives `more`, and starts reviewer again,
    which gives `more`
    Then Lane names writer's start after the first `more`, as the start went to the Run of `write`,
    which began first, and no more starts after the second, as it went to the Run of `review`"""
    conv = two_skills(repo)
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    gives(repo, writer, "written")
    conv.type("/changelog:review")
    _, first = starts(conv, "reviewer")
    assert first and START_WRITER in gives(repo, first, "more").said
    _, second = starts(conv, "reviewer")
    assert second and START_NO_MORE in gives(repo, second, "more").said


@pytest.mark.supports("S5", "guard", "Run", "Lane", "lane types", "Call")
def test_the_main_conversation_is_held_to_the_lanes_of_each_skill_whose_run_goes_on(repo: Repo):
    """Given `changelog` laid with `write`, whose step runs only `git log --oneline`, and
    `review`, whose step runs only `git diff`, and a Run of each going on
    When the main conversation runs `git diff`, then `git status`, and, once the Run of `review`
    ended, `git diff` again
    Then the guard lets the first through, as the steps of `review` allow it, stops the second
    with the sentence of each skill's step, and stops the third, as only `write` goes on"""
    put(
        repo.plugin,
        "skills/write/SKILL.md",
        WRITE.replace("1. Have", "1. Read the last version with `git log --oneline`, and have"),
    )
    put(
        repo.plugin,
        "skills/review/SKILL.md",
        REVIEW.replace("1. Have", "1. Read the changes with `git diff`, and have"),
    )
    proposal = {
        **PROPOSAL_TWO_SKILLS,
        "lanes": [
            *PROPOSAL_TWO_SKILLS["lanes"],
            lane("write", 1, "run_only", "git log --oneline"),
            lane("review", 1, "run_only", "git diff"),
        ],
    }
    conv = laid_with(repo, proposal)
    conv.type("/changelog:write")
    conv.type("/changelog:review")
    assert not conv.bash("git diff").blocked
    stopped = conv.bash("git status")
    assert stopped.blocked
    assert "Run only `git log --oneline`." in stopped.said
    assert "Run only `git diff`." in stopped.said
    _, reviewer = starts(conv, "reviewer")
    assert reviewer
    gives(repo, reviewer, "good")
    conv.bash(result_command(repo, "review", "good"))
    assert conv.bash("git diff").blocked
