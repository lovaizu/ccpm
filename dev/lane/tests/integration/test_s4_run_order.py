"""The integration cases of S4, a run in the order the user set: the laid guard, the lane types, the
adapter, and the plugin's command joined through the double of Claude Code, on each path of S4's
sequence, with the rules that S4 keeps and each combination that its Strategies name."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import walkthrough as w
from claude_code import AGENT_UNKNOWN_TYPE, POSTED_FIRST, Conversation

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
WAITING = "0.2.0 waits for your approval"
# An adapter of a start's text that gives no work waits for the role named, and Lane's form of a
# text for each other role.
NONE_ADAPTER = """#!/usr/bin/env python3
import json, sys
json.load(sys.stdin)
if sys.argv[1] == "{role}":
    print(json.dumps({{"none": "{why}"}}))
else:
    print(json.dumps({{"text": "Carry out your steps"}}))
"""


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


@pytest.mark.supports("S4", "Route", "guard")
def test_a_start_that_isnt_due_is_stopped_with_the_moves_due(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and the person typed /changelog:write.
    When: the main conversation starts reviewer first.
    Then: the guard stops the start, with the start of writer due."""
    c = w.laid(b)
    assert not c.type("/changelog:write").blocked
    stopped, agent = w.start(c, "reviewer")
    assert stopped.blocked and agent is None
    assert w.due("writer") in stopped.said


@pytest.mark.supports(
    "S4",
    "Start",
    "A resume let through where the Routes open none, moving no Run, its Start running again",
)
def test_a_resume_where_the_routes_open_none_moves_no_run(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid; writer gave `written` and ended.
    When: the main conversation resumes writer by SendMessage, which no Route opens, ends its turn
    while writer works, and ends it again once writer's end reaches it.
    Then: the guard lets the resume through, lets the first end go as writer runs, and stops the
    second with the start of reviewer still due."""
    c, writer = w.writer_started(b)
    w.give(b, writer, "written")
    assert not c.resume(writer, "Which version did you write?").blocked
    assert not c.stop("Asked writer.").blocked
    ended, reached = writer.end("I wrote 0.2.0.")
    assert not ended.blocked and reached is not None
    stopped = c.stop("Writer answered.")
    assert stopped.blocked and w.due("reviewer") in stopped.said


@pytest.mark.supports(
    "S4", "Start", "A start of a subagent not the plugin's let through with no Start"
)
def test_a_helper_the_main_conversation_starts_is_let_through(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and the person typed /changelog:write.
    When: the main conversation starts Explore, which isn't changelog's, then ends its turn once
    Explore's end reaches it.
    Then: the guard lets the start through, adds no Start, and stops the end with writer's start
    still due."""
    c = w.laid(b)
    assert not c.type("/changelog:write").blocked
    started, helper = c.start("Explore", "Find the last version", "Find")
    assert not started.blocked and helper is not None, started.said
    ended, reached = helper.end("0.1.0.")
    assert not ended.blocked and reached is not None
    stopped = c.stop("Found it.")
    assert stopped.blocked and w.due("writer") in stopped.said


@pytest.mark.supports(
    "S4", "Result", "A turn's end stopped by a move due while no subagent runs, before any Lane"
)
def test_the_turns_end_with_no_more_due_names_the_skills_result_script(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid; writer gave `written`, and reviewer gave `good`.
    When: the main conversation ends its turn without giving the skill's Result.
    Then: the guard stops it with the sentence of the Lane on write's last Step, which names
    `result.py write good`."""
    c = w.laid(b)
    reviewer = w.to_reviewer(b, c)
    w.give(b, reviewer, "good")
    stopped = c.stop("The entries are good.")
    assert stopped.blocked and b.result("write", "good") in stopped.said


def resumes_writer_after_more() -> dict[str, Any]:
    """The walkthrough's Proposal, with the Route after reviewer's `more` resuming writer."""
    proposal = w.walkthrough_proposal()
    proposal["routes"][2]["moves"] = [{"resume": "writer"}]
    return proposal


@pytest.mark.supports("S4", "Start", "Route")
def test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid with the Route after reviewer's `more` resuming
    writer; writer gave `written`, and reviewer gave `more`.
    When: the main conversation resumes writer by SendMessage, and writer gives `written`.
    Then: the guard tells the main conversation to resume writer, lets the SendMessage through,
    adding a Start of writer marked resumed, and gives reviewer's start due once writer's Result
    reaches it."""
    c, writer = w.writer_started(b, make=resumes_writer_after_more)
    w.give(b, writer, "written")
    _, reviewer = w.start(c, "reviewer")
    assert reviewer
    reached = w.give(b, reviewer, "more")
    assert "Resume `changelog:writer` by SendMessage." in reached.said
    assert not c.resume(writer, "Mend the entries reviewer named.").blocked
    (run,) = w.where(b.changelog, b, c.session_id).runs
    resumed = run.starts[-1]
    assert (resumed.role, resumed.resumed, resumed.agent_id) == ("writer", True, writer.id)
    reached = w.give(b, writer, "written")
    assert reached.said == (
        "changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out your steps`."
    )


@pytest.mark.supports("S4", "Start", "guard")
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


@pytest.mark.supports(
    "S4",
    "adapter",
    "Start",
    "A start judged by the Lane of the Routes, with the adapter of a start's text",
)
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


@pytest.mark.supports("S4", "adapter", "Start", "guard")
def test_a_start_no_work_waits_for_is_left_out_and_the_turn_ends(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of a start's text that gives, for writer, that no
    work waits for it, as `0.2.0 waits for your approval`.
    When: the person types /changelog:write, the main conversation starts writer, and then ends
    its turn.
    Then: the guard lets the call run and gives why in place of writer's start, stops the start of
    writer, and lets the turn end, as no move is due."""
    b = adapter_bench(str(tmp_path), NONE_ADAPTER.format(role="writer", why=WAITING))
    c = w.laid(b, make=with_adapter)
    called = c.type("/changelog:write")
    assert not called.blocked
    assert WAITING in called.said and "changelog:writer" in called.said
    assert "Start `changelog:writer`" not in called.said
    stopped, agent = w.start(c, "writer")
    assert stopped.blocked and agent is None
    assert not c.stop("0.2.0 waits for your approval.").blocked


@pytest.mark.supports("S4", "adapter", "Result")
def test_a_start_no_work_waits_for_after_a_result_is_said_with_why(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of a start's text that gives writer Lane's text,
    and, for reviewer, that no work waits for it, as `0.2.0 waits for your approval`.
    When: writer gives `written`, and its end reaches the main conversation.
    Then: the guard gives writer's Result, with why in place of reviewer's start."""
    b = adapter_bench(str(tmp_path), NONE_ADAPTER.format(role="reviewer", why=WAITING))
    c = w.laid(b, make=with_adapter)
    assert not c.type("/changelog:write").blocked
    _, writer = w.start(c, "writer")
    assert writer
    reached = w.give(b, writer, "written")
    assert "writer gave `written`" in reached.said
    assert WAITING in reached.said and "changelog:reviewer" in reached.said
    assert "Start `changelog:reviewer`" not in reached.said


@pytest.mark.supports("S4", "adapter")
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


# An adapter of a start's text that reads the run's worktree, so that it fails until the
# conversation works in one, where `.git` is a file and not a folder.
WORKTREE_ADAPTER = """#!/usr/bin/env python3
import json, os, sys
json.load(sys.stdin)
if os.path.isdir(".git"):
    sys.exit("enter the run's worktree first")
print(json.dumps({"text": "Write the entries in the run's worktree"}))
"""


@pytest.mark.supports(
    "S4",
    "adapter",
    "Start",
    "Run",
    "The adapter of a start's text failing at the skill's call, asked again after each later call",
)
def test_a_start_whose_adapter_failed_at_the_call_is_given_once_it_gives_its_text(
    tmp_path: Any,
) -> None:
    """Given: the Proposal laid with an adapter of a start's text that fails with `enter the run's
    worktree first` until the conversation works in a worktree, and then gives writer `Write the
    entries in the run's worktree`.
    When: the person types /changelog:write; the main conversation enters a worktree by
    EnterWorktree, as the skill's own steps make what the adapter reads, then runs `git status`,
    then starts writer with the adapter's text.
    Then: the guard gives writer's start with why at the call; gives the start with the adapter's
    text after EnterWorktree; says nothing more after `git status`, as it gave the start once; and
    lets the start through."""
    b = adapter_bench(str(tmp_path), WORKTREE_ADAPTER)
    c = w.laid(b, make=with_adapter)
    called = c.type("/changelog:write")
    assert not called.blocked
    assert "enter the run's worktree first" in called.said and "changelog:writer" in called.said
    text = "Write the entries in the run's worktree"
    entered = c.enter_worktree(name="run")
    assert not entered.blocked
    assert f"changelog: Start `changelog:writer` with `{text}`." in entered.said
    ran = c.bash("git status")
    assert (ran.blocked, ran.said) == (False, ""), "the start is given once"
    started, writer = c.start("changelog:writer", text, "writer")
    assert not started.blocked and writer


@pytest.mark.supports("S4", "adapter", "guard", "user")
def test_the_turns_end_goes_while_the_adapter_cant_give_a_starts_text_yet(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of a start's text that fails with `enter the run's
    worktree first` until the conversation works in a worktree, and then gives writer `Write the
    entries in the run's worktree`.
    When: the person types /changelog:write; the main conversation ends its turn to ask which
    worktree; the person replies `run`; the main conversation enters the worktree run by
    EnterWorktree, and ends its turn again.
    Then: the guard lets the first end go, as no move is due with its text; gives writer's start
    with the adapter's text after EnterWorktree; and stops the second end with that start due."""
    b = adapter_bench(str(tmp_path), WORKTREE_ADAPTER)
    c = w.laid(b, make=with_adapter)
    assert not c.type("/changelog:write").blocked
    assert not c.stop("Which worktree shall the entries go in?").blocked
    assert not c.type("run").blocked
    due = "changelog: Start `changelog:writer` with `Write the entries in the run's worktree`."
    assert due in c.enter_worktree(name="run").said
    stopped = c.stop("Entered the worktree.")
    assert stopped.blocked and due in stopped.said


def picking_up_bench(tmp: str) -> w.Bench:
    """The bench with an adapter of changelog's records that gives writer's `written`, and
    WORKTREE_ADAPTER as the adapter of a start's text."""
    written = json.dumps({"results": [{"role": "writer", "result": "written"}]})
    records = f"#!/usr/bin/env python3\nprint({written!r})\n"
    adapters = {"hooks/adapters/text.py": WORKTREE_ADAPTER, "hooks/adapters/records.py": records}
    b = w.bench(tmp, dict(w.FILES, **adapters))
    for name in adapters:
        w.executable(os.path.join(b.changelog, name))
    return b


def with_both_adapters() -> dict[str, Any]:
    proposal = w.walkthrough_proposal()
    proposal["adapters"] = {
        "text": "hooks/adapters/text.py",
        "records": "hooks/adapters/records.py",
    }
    return proposal


@pytest.mark.supports("S4", "S6", "adapter", "Kept results", "Start")
def test_a_pick_up_whose_adapter_fails_at_the_call_lets_the_call_run(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of changelog's records that gives writer's
    `written`, and an adapter of a start's text that fails with `enter the run's worktree first`
    until the conversation works in a worktree, and then gives `Write the entries in the run's
    worktree`.
    When: the person types /changelog:write in a new conversation; the main conversation ends its
    turn, then enters the worktree run by EnterWorktree, and starts reviewer with the adapter's
    text.
    Then: the guard lets the call run, saying where the run picks up and giving reviewer's start
    with why; lets the turn end; gives reviewer's start with the adapter's text after
    EnterWorktree; and lets the start through."""
    b = picking_up_bench(str(tmp_path))
    c = w.laid(b, make=with_both_adapters)
    called = c.type("/changelog:write")
    assert not called.blocked
    assert "written" in called.said and "changelog:reviewer" in called.said
    assert "enter the run's worktree first" in called.said
    assert not c.stop("Which worktree shall the review go in?").blocked
    text = "Write the entries in the run's worktree"
    entered = c.enter_worktree(name="run")
    assert f"changelog: Start `changelog:reviewer` with `{text}`." in entered.said
    started, reviewer = c.start("changelog:reviewer", text, "reviewer")
    assert not started.blocked and reviewer


# An adapter of a start's text that gives writer a text for each version that no Start that runs
# holds, and that no work waits for writer once each has its Start.
SIDE_BY_SIDE_ADAPTER = """#!/usr/bin/env python3
import json, sys
held = {s["values"].get("version") for s in json.load(sys.stdin)["running"]}
waiting = [v for v in ("0.2.0", "0.3.0") if v not in held]
if waiting:
    print(json.dumps({"text": f"Write the entries for {waiting[0]}",
                      "values": {"version": waiting[0]}}))
else:
    print(json.dumps({"none": "each version has its writer"}))
"""


@pytest.mark.supports(
    "S4",
    "adapter",
    "Start",
    "Route",
    "A start due beside each Start of its role that runs, while the adapter gives another text",
)
def test_a_start_stays_due_beside_a_start_of_its_role_with_another_text(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of a start's text that gives writer `Write the
    entries for <version>` and the value version for 0.2.0, then 0.3.0, each while no Start that
    runs holds it, and that no work waits for writer once both run.
    When: the person types /changelog:write; the main conversation starts writer for 0.2.0, starts
    it for 0.2.0 again, starts it for 0.3.0, starts it for 0.2.0 once more, and ends its turn.
    Then: the guard gives writer's start for 0.2.0 at the call; lets the first start through, and
    gives writer's start for 0.3.0 beside it at the PostToolUse of its Agent call; stops the start
    for 0.2.0 again with the start for 0.3.0 due; lets the start for 0.3.0 through; stops the last
    start, as no work waits for writer; lets the turn end; and the Run holds both Starts of
    writer, each with its own version."""
    b = adapter_bench(str(tmp_path), SIDE_BY_SIDE_ADAPTER)
    c = w.laid(b, make=with_adapter)
    first, second = "Write the entries for 0.2.0", "Write the entries for 0.3.0"
    assert f"Start `changelog:writer` with `{first}`." in c.type("/changelog:write").said
    started, writer = c.start("changelog:writer", first, "writer")
    assert not started.blocked and writer
    assert started.posted == f"changelog: Start `changelog:writer` with `{second}`."
    again, _ = c.start("changelog:writer", first, "writer")
    assert again.blocked and f"Start `changelog:writer` with `{second}`." in again.said
    beside, other = c.start("changelog:writer", second, "writer")
    assert not beside.blocked and other
    last, _ = c.start("changelog:writer", first, "writer")
    assert last.blocked
    assert not c.stop("Both writers are working.").blocked
    (run,) = w.where(b.changelog, b, c.session_id).runs
    held = [(s.role, s.text, dict(s.values)) for s in run.starts]
    assert held == [
        ("writer", first, {"version": "0.2.0"}),
        ("writer", second, {"version": "0.3.0"}),
    ]


@pytest.mark.supports("S4", "adapter")
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


def other_plugin(tmp: str, name: str, skill: str) -> str:
    """The folder of another plugin, with one skill, which a person may type and the model call."""
    folder = os.path.join(tmp, name)
    front = f"---\nname: {skill}\ndescription: Does {skill}.\n---\n\nDo {skill}.\n"
    w.write_files(
        folder,
        {
            ".claude-plugin/plugin.json": f'{{"name": "{name}"}}\n',
            f"skills/{skill}/SKILL.md": front,
        },
    )
    return folder


def aside_bench(tmp: str) -> tuple[w.Bench, w.Conversation]:
    """The Proposal laid with reviewer's `good` calling lint's skill check, and a Route after
    lint's run hands back that starts writer or starts no more, in a conversation with lint
    loaded."""
    b = w.bench(tmp)
    lint = other_plugin(tmp, "lint", "check")
    call = with_route({"role": "reviewer", "result": "good"}, [{"call": "lint:check"}])

    def make() -> dict[str, Any]:
        proposal = call()
        after = {"returned": "lint:check"}
        moves = [{"start": "writer"}, {"no_more": "good"}]
        proposal["routes"].append({"skill": "write", "after": after, "moves": moves})
        return proposal

    w.lay(b, make)
    return b, w.Conversation(b.repo, [b.lane, b.changelog, lint], b.env, b.temp)


@pytest.mark.supports("S4", "lane types", "Call")
def test_another_plugins_skill_no_move_names_is_checked_as_a_call(tmp_path: Any) -> None:
    """Given: the Proposal laid with a write_only Lane on write's step 1 for `CHANGELOG.md`, lint
    loaded, and the person typed /changelog:write.
    When: the main conversation calls lint:check, which no move names, by the Skill tool, then
    writes notes.md.
    Then: the guard lets the Skill call through, as no Lane of write judges it, and stops the write
    with write's step sentence, as the Run doesn't stand aside."""
    b = w.bench(str(tmp_path))
    lint = other_plugin(str(tmp_path), "lint", "check")
    w.lay(b, with_skill_lane("write_only", paths=["CHANGELOG.md"]))
    c = w.Conversation(b.repo, [b.lane, b.changelog, lint], b.env, b.temp)
    assert not c.type("/changelog:write").blocked
    assert not c.skill("lint:check", "").blocked
    stopped = c.write(None, os.path.join(b.repo, "notes.md"), "notes\n")
    assert stopped.blocked and "Write only `CHANGELOG.md`." in stopped.said


@pytest.mark.supports("S4", "Run", "user")
def test_a_command_of_another_plugin_starts_no_run(tmp_path: Any) -> None:
    """Given: the walkthrough's Proposal laid, and another plugin, other, with its skill write.
    When: the person types /other:write.
    Then: the guard starts no Run of changelog."""
    b = w.bench(str(tmp_path))
    other = other_plugin(str(tmp_path), "other", "write")
    w.lay(b)
    c = w.Conversation(b.repo, [b.lane, b.changelog, other], b.env, b.temp)
    assert not c.type("/other:write").blocked
    assert w.where(b.changelog, b, c.session_id).runs == ()


@pytest.mark.supports("S4", "Route", "Run")
def test_a_command_of_another_plugin_leaves_the_moves_due(tmp_path: Any) -> None:
    """Given: the Proposal laid with a Route after /changelog:pause that starts no more, another
    plugin, other, with its skill pause, and writer gave `written`, so reviewer's start is due.
    When: the person types /other:pause, and the main conversation starts reviewer.
    Then: the guard lets the start through, as only changelog's pause goes after the Route."""
    b = w.bench(str(tmp_path), dict(w.FILES, **{"skills/pause/SKILL.md": PAUSE}))
    other = other_plugin(str(tmp_path), "other", "pause")
    w.lay(b, with_route({"command": "pause"}, [{"no_more": "paused"}]))
    c = w.Conversation(b.repo, [b.lane, b.changelog, other], b.env, b.temp)
    assert not c.type("/changelog:write").blocked
    _, writer = w.start(c, "writer")
    assert writer
    w.give(b, writer, "written")
    assert not c.type("/other:pause").blocked
    started, _ = w.start(c, "reviewer")
    assert not started.blocked


@pytest.mark.supports("S4", "lane types", "Call")
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


@pytest.mark.supports("S4", "lane types", "result.py")
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


@pytest.mark.supports("S4", "Route", "Run", "user")
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


@pytest.mark.supports(
    "S4",
    "Route",
    "Run",
    "A typed command that a Route goes after, its moves due in place of those before",
)
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


@pytest.mark.supports(
    "S4",
    "Start",
    "Result",
    "An end that ends the Start of the call it names, and each Start of its subagent before it",
)
def test_an_end_that_reaches_after_a_resume_ends_only_the_pass_it_names(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started, which gave `written` and ended,
    and the main conversation resumed it before that end reached it.
    When: that end reaches the main conversation, and writer gives `written` again and ends.
    Then: the main conversation reads that writer gave `written`, never that it ended with no
    Result, and the resumed writer's Result and end go through."""
    c, writer = w.writer_started(b)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    ended, _ = writer.end("Gave written.", reach=False)
    assert not ended.blocked, ended.said
    assert not c.resume(writer, "Write it again.").blocked
    reached = writer.reach()
    assert "writer gave `written`" in reached.said, reached.said
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    again, _ = writer.end("Gave written again.")
    assert not again.blocked, again.said


@pytest.mark.supports(
    "S4", "Start", "Result", "A subagent that ends with no Result, its start due again"
)
def test_a_subagent_stopped_by_task_stop_is_due_again(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started by /changelog:write.
    When: the main conversation stops writer by TaskStop.
    Then: the guard says writer ended with no Result, and gives writer's start due again."""
    c, writer = w.writer_started(b)
    told = c.task_stop(writer)
    assert "writer" in told.said and w.due("writer") in told.said


@pytest.mark.supports(
    "S4",
    "guard",
    "A turn's end stopped by a move due while no subagent runs, before any Lane",
)
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


@pytest.mark.supports("S4", "guard", "Start")
def test_the_turns_end_while_the_runs_subagent_runs_goes(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started in the background.
    When: the main conversation ends its turn while writer runs.
    Then: the guard lets the turn end."""
    c, _ = w.writer_started(b)
    assert not c.stop("writer is working.").blocked


@pytest.mark.supports("S4", "lane types", "Result")
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


@pytest.mark.supports(
    "S4", "Run", "Route", "The main conversation's call judged by each Lane of each Run's skill"
)
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
    reached = w.give(b, writer, "written")
    gave = (
        "changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out your steps`."
    )
    assert gave in reached.said


@pytest.mark.supports("S1", "up", "user", "Proposal")
def test_up_shows_the_walkthroughs_proposal(b: w.Bench) -> None:
    """Given: changelog as the walkthrough gives it, with no Lane laid.
    When: the person types /lane:up changelog, and up hands the walkthrough's Proposal to lay.py
    print.
    Then: lay.py print exits 0 and shows the Routes, each Step as it'll read, and the ID, word for
    word as the README shows them."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    assert printed.exit_code == 0
    assert printed.output.rstrip("\n") == w.shown(pid)


@pytest.mark.supports("S4", "Route", "Start", "Result", "Run", "guard")
def test_the_walkthroughs_run_moves_in_the_order_the_user_set(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and Claude Code's plugins reloaded.
    When: the person types /changelog:write, and the main conversation starts each subagent it's
    told to, writer giving `written`, reviewer `more`, writer `written`, and reviewer `good`.
    Then: Lane gives each start due and each Result with its moves, word for word as the README
    shows, and the skill's result.py write good ends the Run."""
    c = w.laid(b)
    assert w.due("writer") in c.type("/changelog:write").said
    for role, result, then in (
        ("writer", "written", w.due("reviewer")),
        ("reviewer", "more", w.due("writer")),
        ("writer", "written", w.due("reviewer")),
        ("reviewer", "good", "changelog: reviewer gave `good`. Start no more subagents."),
    ):
        started, agent = w.start(c, role)
        assert not started.blocked and agent
        reached = w.give(b, agent, result)
        assert f"changelog: {role} gave `{result}`." in reached.said
        assert then.split(": ", 1)[-1] in reached.said
    assert c.bash(b.result("write", "good")).exit_code == 0
    assert all(r.ended for r in w.where(b.changelog, b, c.session_id).runs)


@pytest.mark.supports("S5", "A stop gives the step back", "Lane")
def test_a_call_that_breaks_a_lane_gets_its_steps_sentence(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, and writer started.
    When: writer runs `git -C <tally> log --oneline`.
    Then: the guard stops it with the step's sentence and each command writer may run, word for
    word as the README shows."""
    _, writer = w.writer_started(b)
    stopped = writer.bash(f"git -C {b.repo} log --oneline")
    assert stopped.blocked
    assert stopped.said == (
        "changelog: Run only `git log --oneline`.\n"
        "The commands you may run, each word for word: `git log --oneline`,"
        f" `{b.result('writer', 'written')}`."
    )


@pytest.mark.supports("S4", "Start", "Result", "guard")
def test_a_start_after_a_result_goes_while_the_subagent_that_gave_it_still_runs(
    b: w.Bench,
) -> None:
    """Given: the walkthrough's Proposal laid, and writer started, which gave `written` and runs on
    before its end.
    When: the main conversation starts reviewer, as the guard gives it due, then writer ends, and
    its end reaches the main conversation, and the main conversation ends its turn.
    Then: reviewer's start goes, the main conversation reads that writer gave `written` with no
    start of reviewer due again, and the turn's end goes while reviewer runs."""
    c, writer = w.writer_started(b)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    started, reviewer = w.start(c, "reviewer")
    assert reviewer, started.said
    ended, reached = writer.end("Gave written.")
    assert not ended.blocked, ended.said
    assert reached is not None
    assert "writer gave `written`" in reached.said, reached.said
    assert w.due("reviewer") not in reached.said, reached.said
    assert not c.stop("Reviewer is checking the entries.").blocked


# A plugin beside changelog whose PreToolUse hook denies each Agent call, as a second plugin denied
# one in dev/tests/recorded/claude-code-2.1.327-agent-denied-by-hook.jsonl.
DENIER = {
    ".claude-plugin/plugin.json": json.dumps({"name": "denier"}),
    "hooks/hooks.json": json.dumps(
        {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Agent",
                        "hooks": [
                            {"type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/deny.py"}
                        ],
                    }
                ]
            }
        }
    ),
    "deny.py": (
        "import json, sys\njson.load(sys.stdin)\n"
        'print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",'
        ' "permissionDecision": "deny", "permissionDecisionReason": "No subagents here."}}))\n'
    ),
}


@pytest.mark.supports(
    "S4",
    "Start",
    "guard",
    "A Start dropped at its call's PostToolUseFailure, or untied at the turn's end",
)
def test_a_start_whose_agent_call_fails_is_due_again(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and the person typed /changelog:write.
    When: the main conversation starts writer, as the guard gives it due, and the Agent call fails
    with PostToolUseFailure, as one naming no subagent type that exists does; then it starts writer
    again.
    Then: the second start goes, as the guard dropped the Start of the failed call."""
    c = w.laid(b)
    assert not c.type("/changelog:write").blocked
    failed = c.start_failing("changelog:writer", w.TEXT, "writer", AGENT_UNKNOWN_TYPE)
    assert failed.blocked, failed.said
    again, writer = w.start(c, "writer")
    assert writer, again.said


@pytest.mark.supports(
    "S4",
    "Start",
    "guard",
    "A Start dropped at its call's PostToolUseFailure, or untied at the turn's end",
)
def test_a_start_whose_call_another_plugin_denies_is_due_again_at_the_turns_end(
    b: w.Bench,
) -> None:
    """Given: the walkthrough's Proposal laid beside a plugin whose PreToolUse hook denies each
    Agent call, and the person typed /changelog:write.
    When: the main conversation starts writer, which Lane lets through and the other plugin
    denies, and then ends its turn.
    Then: the turn's end is stopped with writer's start due, as the guard dropped the untied Start
    at the Stop."""
    w.lay(b)
    denier = os.path.join(b.temp, "denier")
    w.write_files(denier, DENIER)
    c = Conversation(b.repo, [b.lane, b.changelog, denier], b.env, b.temp)
    assert not c.type("/changelog:write").blocked
    denied, agent = w.start(c, "writer")
    assert denied.blocked and agent is None
    stopped = c.stop("The subagent was denied.")
    assert stopped.blocked and w.due("writer") in stopped.said, stopped.said


@pytest.mark.supports(
    "S4",
    "S5",
    "Start",
    "Result",
    "A resume queued to a running subagent, its Start held back until that subagent's"
    " SubagentStart",
)
def test_a_resume_queued_while_its_subagent_runs_starts_at_its_subagentstart(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid with the Route after reviewer's `more` resuming
    writer; writer gave `written` and runs on, and reviewer gave `more`.
    When: the main conversation resumes writer by SendMessage, which Claude Code queues, then
    writer's pass ends, it starts again on the message, gives `written`, and ends.
    Then: the end of the pass that gave `written` goes, and so do the resumed writer's Result and
    end."""
    c, writer = w.writer_started(b, make=resumes_writer_after_more)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    _, reviewer = w.start(c, "reviewer")
    assert reviewer
    reached = w.give(b, reviewer, "more")
    assert "Resume `changelog:writer` by SendMessage." in reached.said
    assert not c.resume(writer, "Mend the entries reviewer named.").blocked
    ended, _ = writer.end("Gave written.", reach=False)
    assert not ended.blocked, ended.said
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    again, _ = writer.end("Gave written again.")
    assert not again.blocked, again.said
