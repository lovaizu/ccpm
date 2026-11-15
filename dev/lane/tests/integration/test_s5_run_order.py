"""The integration cases of S5, a run in the order the user set: the laid guard, the lane types, the
adapter, and the plugin's command joined through the double of Claude Code, on each path of S5's
sequence, with the rules and strategies that S5 keeps."""

from __future__ import annotations

import os
from typing import Any

import pytest
import walkthrough as w
from claude_code import POSTED_FIRST

COMMAND = "---\nname: {name}\ndescription: {what}\ndisable-model-invocation: true\n---\n\n"
APPROVE = COMMAND.format(name="approve", what="Approves the entries.") + "## Steps\n\n1. Go on.\n"
PAUSE = COMMAND.format(name="pause", what="Pauses the run.") + "## Steps\n\n1. Stop here.\n"
TEXT_ADAPTER = """#!/usr/bin/env python3
import json, sys
running = json.load(sys.stdin)["running"]
print(json.dumps({"text": f"Write the entries for 0.2.0 as {sys.argv[1]}",
                  "values": {"version": "0.2.0"}}))
"""
FAILING_ADAPTER = "#!/usr/bin/env python3\nimport sys\nsys.exit('no version to write yet')\n"


def with_route(after: dict[str, Any], moves: list[dict[str, Any]]) -> w.Make:
    """The walkthrough's Proposal, with a Route of write after `after` making the moves, in place
    of any Route after the same."""

    def make() -> dict[str, Any]:
        proposal = w.walkthrough_proposal()
        routes = [r for r in proposal["routes"] if r["after"] != after]
        proposal["routes"] = [*routes, {"skill": "write", "after": after, "moves": moves}]
        return proposal

    return make


def with_skill_lane(kind: str, **args: Any) -> w.Make:
    """The walkthrough's Proposal, with a Lane of the type on write's step 1, with the values."""

    def make() -> dict[str, Any]:
        proposal = w.walkthrough_proposal()
        proposal["lanes"].append(w.lane("write", "skills/write/SKILL.md", 1, kind, **args))
        return proposal

    return make


def with_adapter() -> dict[str, Any]:
    proposal = w.walkthrough_proposal()
    proposal["adapters"] = {"text": "hooks/adapters/text.py"}
    return proposal


def adapter_bench(tmp: str, program: str) -> w.Bench:
    b = w.bench(tmp, dict(w.FILES, **{"hooks/adapters/text.py": program}))
    w.executable(os.path.join(b.changelog, "hooks", "adapters", "text.py"))
    return b


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "Route", "guard")
def test_a_start_that_isnt_due_is_stopped_with_the_moves_due(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and the person typed /changelog:write.
    When: the main conversation starts reviewer first.
    Then: the guard stops the start, with the start of writer due."""
    c = w.laid(b)
    assert not c.type("/changelog:write").blocked
    stopped, agent = w.start(c, "reviewer")
    assert stopped.blocked and agent is None
    assert w.due("writer") in stopped.said


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "Start")
def test_a_resume_where_the_routes_open_none_moves_no_run(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid; writer gave `written` and ended.
    When: the main conversation resumes writer by SendMessage, which no Route opens.
    Then: the guard lets it through, and the start of reviewer is still due."""
    c, writer = w.writer_started(b)
    w.give(b, writer, "written")
    assert not c.resume(writer, "Which version did you write?").blocked
    stopped = c.stop("Asked writer.")
    assert stopped.blocked and w.due("reviewer") in stopped.said


@pytest.mark.supports("S5", "Start", "guard")
def test_a_start_whose_subagent_starts_after_its_post_tool_use_is_held(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and the person typed /changelog:write.
    When: the main conversation starts writer, whose SubagentStart comes after the PostToolUse of
    its Agent call, and writer runs `git status`.
    Then: the guard stops writer's call with its step's sentence, as the Start is tied to writer."""
    c = w.laid(b)
    assert not c.type("/changelog:write").blocked
    started, writer = c.start("changelog:writer", w.TEXT, "writer", how=POSTED_FIRST)
    assert not started.blocked and writer
    stopped = writer.bash("git status")
    assert stopped.blocked and "Run only `git log --oneline`." in stopped.said


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "adapter", "Start")
def test_an_adapter_gives_each_start_its_text_and_values(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of a start's text that gives writer `Write the
    entries for 0.2.0 as writer` and the value version 0.2.0.
    When: the person types /changelog:write, and the main conversation starts writer with that
    text.
    Then: Lane gives the start of writer with the adapter's text, and lets that start through."""
    b = adapter_bench(str(tmp_path), TEXT_ADAPTER)
    c = w.laid(b, make=with_adapter)
    text = "Write the entries for 0.2.0 as writer"
    assert f"changelog: Start `changelog:writer` with `{text}`." in c.type("/changelog:write").said
    started, writer = c.start("changelog:writer", text, "writer")
    assert not started.blocked and writer


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "adapter")
def test_an_adapter_that_fails_at_the_skills_call_lets_the_call_run(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of a start's text that exits 1 with `no version to
    write yet`.
    When: the person types /changelog:write.
    Then: the guard lets the call run, and gives the start of writer with why."""
    b = adapter_bench(str(tmp_path), FAILING_ADAPTER)
    c = w.laid(b, make=with_adapter)
    called = c.type("/changelog:write")
    assert not called.blocked
    assert "changelog:writer" in called.said and "no version to write yet" in called.said


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "adapter")
def test_an_adapter_that_fails_at_a_later_move_gives_why_and_who(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of a start's text, which gives writer's text, then
    fails as writer gives `written`.
    When: writer's end reaches the main conversation.
    Then: the guard gives why the adapter failed and that the plugin's developer must fix it, in
    place of reviewer's start."""
    b = adapter_bench(str(tmp_path), TEXT_ADAPTER)
    c = w.laid(b, make=with_adapter)
    text = "Write the entries for 0.2.0 as writer"
    assert not c.type("/changelog:write").blocked
    _, writer = c.start("changelog:writer", text, "writer")
    assert writer
    w.write_files(b.changelog, {"hooks/adapters/text.py": FAILING_ADAPTER})
    reached = w.give(b, writer, "written")
    assert "no version to write yet" in reached.said
    assert "Start `changelog:reviewer`" not in reached.said


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "guard", "Run")
def test_the_run_stands_aside_while_another_plugins_skill_runs(tmp_path: Any) -> None:
    """Given: the Proposal laid with reviewer's `good` calling the skill check of another plugin,
    lint, and a Route after lint's run hands back.
    When: reviewer gives `good`, and the main conversation calls lint:check by the Skill tool, then
    runs `git status`, then starts writer.
    Then: the guard lets each call through while lint's run holds the main conversation."""
    b = w.bench(str(tmp_path))
    lint = os.path.join(str(tmp_path), "lint")
    w.write_files(
        lint,
        {
            ".claude-plugin/plugin.json": '{"name": "lint"}\n',
            "skills/check/SKILL.md": "---\nname: check\ndescription: Checks.\n---\n\nCheck.\n",
        },
    )
    call = with_route({"role": "reviewer", "result": "good"}, [{"call": "lint:check"}])

    def make() -> dict[str, Any]:
        proposal = call()
        after = {"returned": "lint:check"}
        moves = [{"start": "writer"}]
        proposal["routes"].append({"skill": "write", "after": after, "moves": moves})
        return proposal

    w.lay(b, make)
    c = w.Conversation(b.repo, [b.lane, b.changelog, lint], b.env, b.temp)
    reviewer = w.to_reviewer(b, c)
    assert "lint:check" in w.give(b, reviewer, "good").said
    assert not c.skill("lint:check", "").blocked
    assert not c.bash("git status").blocked
    started, _ = w.start(c, "writer")
    assert not started.blocked


@pytest.mark.supports("S5", "lane types", "Call")
def test_a_call_of_the_main_conversation_that_breaks_a_lane_is_stopped(tmp_path: Any) -> None:
    """Given: the Proposal laid with a write_only Lane on write's step 1 for `CHANGELOG.md`, and the
    person typed /changelog:write.
    When: the main conversation writes notes.md, then runs `git status`.
    Then: the guard stops the write with write's step sentence, and lets `git status` through."""
    b = w.bench(str(tmp_path))
    c = w.laid(b, make=with_skill_lane("write_only", paths=["CHANGELOG.md"]))
    assert not c.type("/changelog:write").blocked
    stopped = c.write(None, os.path.join(b.repo, "notes.md"), "notes\n")
    assert stopped.blocked and "Write only `CHANGELOG.md`." in stopped.said
    assert not c.bash("git status").blocked


@pytest.mark.supports("S5", "lane types", "result.py")
def test_the_skills_result_script_goes_beside_a_lane_that_allows_other_calls(tmp_path: Any) -> None:
    """Given: the Proposal laid with a write_only Lane on write's step 1 for `CHANGELOG.md`, and
    reviewer gave `good`.
    When: the main conversation runs result.py write good.
    Then: the guard lets it through, as the end's result script stands for every lane type, and
    result.py gives 0 and ends the Run."""
    b = w.bench(str(tmp_path))
    c = w.laid(b, make=with_skill_lane("write_only", paths=["CHANGELOG.md"]))
    w.give(b, w.to_reviewer(b, c), "good")
    ran = c.bash(b.result("write", "good"))
    assert not ran.blocked and ran.exit_code == 0
    assert all(r.ended for r in w.where(b.changelog, b, c.session_id).runs)


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "Route", "Run", "user")
def test_a_move_that_waits_for_the_person_lets_the_turn_end(tmp_path: Any) -> None:
    """Given: the Proposal laid with reviewer's `good` waiting for /changelog:approve, and a Route
    after approve that starts no more.
    When: reviewer gives `good`, the main conversation ends its turn, and the person types
    /changelog:approve.
    Then: the guard lets the turn end, and gives the moves after approve."""
    b = w.bench(str(tmp_path), dict(w.FILES, **{"skills/approve/SKILL.md": APPROVE}))

    def make() -> dict[str, Any]:
        good = {"role": "reviewer", "result": "good"}
        proposal = with_route(good, [{"wait": "approve"}])()
        after = {"skill": "write", "after": {"command": "approve"}, "moves": [{"no_more": "good"}]}
        proposal["routes"].append(after)
        return proposal

    c = w.laid(b, make=make)
    reviewer = w.to_reviewer(b, c)
    w.give(b, reviewer, "good")
    assert not c.stop("Waiting for your approval.").blocked
    assert "Start no more subagents." in c.type("/changelog:approve").said


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "Route", "Run")
def test_a_command_a_route_goes_after_takes_the_place_of_the_moves_due(tmp_path: Any) -> None:
    """Given: the Proposal laid with a Route after /changelog:pause that starts no more, and
    writer gave `written`, so reviewer's start is due.
    When: the person types /changelog:pause, and the main conversation starts reviewer.
    Then: the guard stops the start, as pause's moves take the place of reviewer's."""
    b = w.bench(str(tmp_path), dict(w.FILES, **{"skills/pause/SKILL.md": PAUSE}))
    c = w.laid(b, make=with_route({"command": "pause"}, [{"no_more": "paused"}]))
    assert not c.type("/changelog:write").blocked
    _, writer = w.start(c, "writer")
    assert writer
    w.give(b, writer, "written")
    assert not c.type("/changelog:pause").blocked
    stopped, _ = w.start(c, "reviewer")
    assert stopped.blocked


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "Start", "Result")
def test_a_subagent_stopped_by_task_stop_is_due_again(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started by /changelog:write.
    When: the main conversation stops writer by TaskStop.
    Then: the guard says writer ended with no Result, and gives writer's start due again."""
    c, writer = w.writer_started(b)
    told = c.task_stop(writer)
    assert "writer" in told.said and w.due("writer") in told.said


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "guard")
def test_the_turns_end_while_a_start_is_due_is_stopped(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid; reviewer gave `more`, and writer gave `written`
    again.
    When: the main conversation ends its turn to ask the person.
    Then: the guard stops the end with reviewer's start due, as the README shows."""
    c = w.laid(b)
    reviewer = w.to_reviewer(b, c)
    w.give(b, reviewer, "more")
    _, writer = w.start(c, "writer")
    assert writer
    w.give(b, writer, "written")
    stopped = c.stop("Shall I go on?")
    assert stopped.blocked
    assert w.due("reviewer") in stopped.said


@pytest.mark.supports("S5", "guard", "Start")
def test_the_turns_end_while_the_runs_subagent_runs_goes(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started in the background.
    When: the main conversation ends its turn while writer runs.
    Then: the guard lets the turn end."""
    c, _ = w.writer_started(b)
    assert not c.stop("writer is working.").blocked


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "lane types", "Result")
def test_the_skills_end_held_to_its_command_goes_once_it_gives_0(tmp_path: Any) -> None:
    """Given: the Proposal laid with an ends_checked Lane on write's step 1 whose command passes
    only where the Result is `good` and CHANGELOG.md names 0.2.0.
    When: reviewer gives `good`, the skill runs result.py write good, and ends its turn, first
    before CHANGELOG.md names 0.2.0, then after.
    Then: the guard stops the first end with the Lane's sentence, and lets the second end."""
    b = w.bench(str(tmp_path))
    check = 'test "{result}" = good && grep -q 0.2.0 CHANGELOG.md'
    c = w.laid(b, make=with_skill_lane("ends_checked", command=check))
    w.give(b, w.to_reviewer(b, c), "good")
    assert c.bash(b.result("write", "good")).exit_code == 0
    stopped = c.stop("Done.")
    assert stopped.blocked and check in stopped.said
    w.write_files(b.repo, {"CHANGELOG.md": "# Changelog\n\n## 0.2.0\n\n- Counts.\n"})
    assert not c.stop("Done.").blocked


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S5", "Run", "Route")
def test_a_second_skills_run_beside_the_first_keeps_its_own_routes(tmp_path: Any) -> None:
    """Given: the Proposal laid with a second skill, check, whose Route starts reviewer first, and
    writer started by /changelog:write.
    When: the person types /changelog:check while writer runs, the main conversation starts
    reviewer, and writer gives `written`.
    Then: Lane lets reviewer's start through for check's Run, and gives write's reviewer due after
    writer's Result, each by its own Routes."""
    check = "---\nname: check\ndescription: Checks the entries.\n---\n\n## Steps\n\n1. Check.\n"
    b = w.bench(str(tmp_path), dict(w.FILES, **{"skills/check/SKILL.md": check}))

    def make() -> dict[str, Any]:
        proposal = w.walkthrough_proposal()
        proposal["lanes"] += [
            w.lane("check", "skills/check/SKILL.md", 1, "routes"),
            w.lane("check", "skills/check/SKILL.md", 1, "ends_by_result"),
        ]
        proposal["routes"] += [
            {"skill": "check", "after": {"first": True}, "moves": [{"start": "reviewer"}]},
            {
                "skill": "check",
                "after": {"role": "reviewer", "result": "good"},
                "moves": [{"no_more": "good"}],
            },
        ]
        return proposal

    c = w.laid(b, make=make)
    assert not c.type("/changelog:write").blocked
    _, writer = w.start(c, "writer")
    assert writer
    assert w.due("reviewer") in c.type("/changelog:check").said
    started, _ = w.start(c, "reviewer")
    assert not started.blocked
    assert w.due("reviewer") in w.give(b, writer, "written").said
