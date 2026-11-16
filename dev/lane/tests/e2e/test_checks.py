"""The unit cases of the checks by which Lane's E2E cases read their records, as N4 of the test
implementation best practice asks: each check by code gives the right result on the pilot records,
and on a copy of them broken in the way it must catch, before any E2E run relies on it, so that a
failed E2E case points to Lane, not to the test. The fixtures in fixtures/ are an excerpt of the
hook events, the turns, and the changes to the plugin's steps of the pilot run of each E2E test
file, walkthrough.json and ai-approves.json, on Claude Code 2.1.325 and Opus."""

from __future__ import annotations

import json
import os
import shutil
from typing import Any

import measures as m
import pytest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
WALKTHROUGH = os.path.join(FIXTURES, "walkthrough")
AI_APPROVES = os.path.join(FIXTURES, "ai-approves")
# A whole run of write, as the walkthrough's first records show both of its runs.
KEPT = ["writer", ("writer", "written"), "reviewer", ("reviewer", "good"), ("reviewer", "good")]
RESULT = "python3 <run>/clone/changelog/hooks/lane/result.py"


def post(tool: str, tool_input: dict[str, Any], **more: Any) -> dict[str, Any]:
    return {"hook_event_name": "PostToolUse", "tool_name": tool, "tool_input": tool_input, **more}


@pytest.mark.supports("KR1.1")
def test_the_walkthroughs_runs_of_write_are_read_in_order() -> None:
    """Given: the walkthrough's first records, with /changelog:write typed twice.
    When: runs_of_write reads them.
    Then: it gives two runs, each with writer's start, its `written`, reviewer's start, and its
    `good` twice, as reviewer ran result.py inside a longer command first, and each ended by write's
    `good`."""
    runs = m.runs_of_write(WALKTHROUGH)
    assert [r.moves for r in runs] == [KEPT, KEPT]
    assert [r.ended for r in runs] == ["2026-11-16T02:25:42.002249Z", "2026-11-16T02:27:49.329232Z"]


@pytest.mark.supports("KR1.1")
def test_an_ais_runs_of_write_by_the_skill_tool_are_read() -> None:
    """Given: ai-approves's first records, where the AI called changelog:write by the Skill tool
    twice: first before /reload-plugins, where writer gave no Result and write never ended.
    When: runs_of_write reads them.
    Then: it gives both runs, the first with no `written` and no end."""
    runs = m.runs_of_write(AI_APPROVES)
    assert [r.moves for r in runs] == [
        ["writer", "reviewer", ("reviewer", "good")],
        ["writer", ("writer", "written"), "reviewer", ("reviewer", "good")],
    ]
    assert [r.ended for r in runs] == [None, "2026-11-16T02:26:40.285908Z"]


@pytest.mark.supports("KR1.1")
def test_each_run_names_the_subagents_it_started() -> None:
    """Given: the walkthrough's first records.
    When: runs_of_write reads them.
    Then: each run names the agent_id of each subagent it started, writer's and reviewer's, and no
    other run's."""
    runs = m.runs_of_write(WALKTHROUGH)
    assert [len(r.agents) for r in runs] == [2, 2]
    assert not set(runs[0].agents) & set(runs[1].agents)


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize(
    "event, moves",
    [
        (post("Agent", {"subagent_type": "changelog:writer"}), [("writer", "")]),
        (post("Bash", {"command": f"{RESULT} writer written"}), [("writer", "written")]),
        (
            post("Bash", {"command": f": > REVIEW.md && {RESULT} reviewer good"}),
            [("reviewer", "good")],
        ),
        (post("Bash", {"command": "python3 <top>/plugins/lane/hooks/lane/result.py up laid"}), []),
        (post("Bash", {"command": "git log --oneline"}), []),
        (
            {
                **post("Bash", {"command": f"{RESULT} writer written"}),
                "hook_event_name": "PreToolUse",
            },
            [],
        ),
    ],
    ids=[
        "a start",
        "a Result",
        "a Result among commands",
        "up's Result",
        "a command",
        "a PreToolUse",
    ],
)
def test_moves_of_reads_starts_and_changelogs_results(
    event: dict[str, Any], moves: list[tuple[str, str]]
) -> None:
    """Given: one hook event.
    When: moves_of reads it.
    Then: it gives a start of changelog's role, and each Result that changelog's result.py gives,
    alone or among other commands; nothing for up's result.py, another command, or a call not yet
    made."""
    assert m.moves_of(event) == moves


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize(
    "event, starts",
    [
        ({"hook_event_name": "UserPromptExpansion", "command_name": "changelog:write"}, True),
        ({"hook_event_name": "UserPromptExpansion", "command_name": "lane:up"}, False),
        (post("Skill", {"skill": "changelog:write"}), True),
        (post("Skill", {"skill": "lane:up"}), False),
        ({**post("Skill", {"skill": "changelog:write"}), "hook_event_name": "PreToolUse"}, False),
    ],
    ids=["typed", "another typed", "called", "another called", "a call not yet made"],
)
def test_write_starts_by_a_typed_or_called_write(event: dict[str, Any], starts: bool) -> None:
    """Given: one hook event.
    When: write_starts reads it.
    Then: it starts a run for the person's /changelog:write and an AI's Skill call of it, and for
    nothing else."""
    assert m.write_starts(event) is starts


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize(
    "moves, ended, faults",
    [
        (KEPT, "t", 0),
        (KEPT, None, 1),
        (["writer", "reviewer", ("reviewer", "good")], None, 2),
        (["reviewer"], "t", 2),
        (["writer", ("writer", "written")], "t", 1),
        (["writer", ("writer", "written"), "reviewer", ("reviewer", "more"), "writer"], "t", 0),
    ],
    ids=["kept", "no end", "a start not due", "the wrong start", "a start due left", "more"],
)
def test_order_faults_counts_each_start_against_its_route(
    moves: list[Any], ended: str | None, faults: int
) -> None:
    """Given: a run's moves, and whether write ended by its Result.
    When: order_faults counts them.
    Then: it counts each start its routes didn't make due by then, each start due that never came,
    and an end with no Result of write."""
    assert m.order_faults(m.Run(moves, ended, [])) == faults


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize(
    "records, keeps, share",
    [
        (WALKTHROUGH, [True, True], 0.0),
        (WALKTHROUGH, [True, False], 50.0),
        (AI_APPROVES, [True, True], 50.0),
    ],
    ids=["both kept", "one judged off", "one off by order"],
)
def test_kr11_is_the_share_of_runs_off_by_order_or_by_the_judge(
    records: str, keeps: list[bool], share: float
) -> None:
    """Given: the first records, and the judge's verdict on each run of write.
    When: share_off counts KR1.1.
    Then: it gives the percent of runs off by their order or failed by the judge."""
    assert m.share_off(m.runs_of_write(records), keeps) == share


@pytest.mark.supports("KR1.2")
@pytest.mark.parametrize(
    "records, keeps, minutes",
    [
        (WALKTHROUGH, [True, True], 1.98),
        (WALKTHROUGH, [False, True], 4.10),
        (AI_APPROVES, [True, True], 2.83),
    ],
    ids=["the first run", "the second run", "after a run off by order"],
)
def test_kr12_is_the_time_to_the_end_of_the_first_kept_run(
    records: str, keeps: list[bool], minutes: float
) -> None:
    """Given: the first records, and the judge's verdict on each run of write.
    When: minutes_to_kept counts KR1.2.
    Then: it gives the minutes from the person's first turn to the end of the first run that keeps
    its order and that the judge passes."""
    measured = m.minutes_to_kept(records, m.runs_of_write(records), keeps)
    assert measured == pytest.approx(minutes, abs=0.01)


@pytest.mark.supports("KR1.2")
def test_kr12_is_none_where_no_run_is_kept() -> None:
    """Given: the walkthrough's first records, with the judge failing both runs.
    When: minutes_to_kept counts KR1.2.
    Then: it gives None."""
    assert m.minutes_to_kept(WALKTHROUGH, m.runs_of_write(WALKTHROUGH), [False, False]) is None


@pytest.mark.supports("KR1.1")
def test_the_judge_reads_one_run_with_its_own_subagents(tmp_path: Any) -> None:
    """Given: records with the main conversation's transcript, and those of subagents a1 and b2.
    When: judge_prompt writes the judge's prompt for a run that started a1, the second of two.
    Then: it names the run as the second of two, and holds the plugin's steps, what the run
    changed in them but not in Lane's laid code, the main conversation's transcript, and a1's, but
    not b2's."""
    folder = tmp_path / "transcripts" / "session"
    (folder / "subagents").mkdir(parents=True)
    (folder / "main.jsonl").write_text(json.dumps({"said": "main"}) + "\n")
    (folder / "subagents" / "agent-a1.jsonl").write_text(json.dumps({"said": "of a1"}) + "\n")
    (folder / "subagents" / "agent-b2.jsonl").write_text(json.dumps({"said": "of b2"}) + "\n")
    steps = "diff --git a/changelog/agents/writer.md b/changelog/agents/writer.md\n"
    steps += "+3. Write at the top\n"
    code = (
        "diff --git a/changelog/hooks/lane/guard.py b/changelog/hooks/lane/guard.py\n+import os\n"
    )
    (tmp_path / "run.diff").write_text(steps + code)
    prompt = m.judge_prompt(str(tmp_path), m.Run(KEPT, "t", ["a1"]), 2, 2)
    assert "run 2 of 2" in prompt
    assert "<!-- changelog/agents/reviewer.md -->" in prompt and "+3. Write at the top" in prompt
    assert "+import os" not in prompt
    assert "main" in prompt and "of a1" in prompt and "of b2" not in prompt


@pytest.mark.supports("KR1.1")
def test_the_judge_rules_whether_the_run_keeps_its_steps() -> None:
    """Given: the judge's prompt.
    When: it is read.
    Then: it asks for one pass or fail point, whether the run keeps its steps, counting what went
    through off a step and each stop of a call that the step allows, and not a stop of a call that
    the step doesn't allow."""
    assert '{"keeps": true or false' in m.JUDGE
    assert "went through" in m.JUDGE and "allows" in m.JUDGE and "doesn't allow" in m.JUDGE


def file_of(records: str) -> str:
    """The E2E test file whose pilot records lie in the fixture's folder, which is named by it."""
    return os.path.basename(records) + ".json"


def broken(tmp: Any, records: str, name: str, change: Any) -> str:
    """A copy of the records in the folder, with the file of the name changed by `change`, which
    takes its lines and gives them back."""
    copy = os.path.join(str(tmp), os.path.basename(records))
    shutil.copytree(records, copy)
    path = os.path.join(copy, name)
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(change(lines))
    return copy


def without(*words: str) -> Any:
    """A change that leaves out each line holding every one of the words."""
    return lambda lines: [x for x in lines if not all(w in x for w in words)]


def second_without(*words: str) -> Any:
    """A change that leaves out the second line holding every one of the words."""

    def change(lines: list[str]) -> list[str]:
        found = [i for i, x in enumerate(lines) if all(w in x for w in words)]
        return [x for i, x in enumerate(lines) if i != found[1]]

    return change


@pytest.mark.supports("KR1.1", "KR1.2")
@pytest.mark.parametrize("records", [WALKTHROUGH, AI_APPROVES])
def test_the_pilot_runs_ran_as_their_cases_mean(records: str) -> None:
    """Given: the pilot records of the E2E test file.
    When: otherwise checks them.
    Then: it finds nothing that went otherwise than the case means."""
    assert m.otherwise(records, file_of(records)) == []


@pytest.mark.supports("KR1.1", "KR1.2")
@pytest.mark.parametrize(
    "records, name, change, said",
    [
        (
            WALKTHROUGH,
            "turns.jsonl",
            lambda lines: [*lines[:-1], lines[-1].replace('"exit": 0', '"exit": 1')],
            "turn 8 exited 1",
        ),
        (
            WALKTHROUGH,
            "turns.jsonl",
            second_without("/reload-plugins"),
            "no /reload-plugins after lay.py write at 2026-11-16T02:26:35.346500Z",
        ),
        (
            WALKTHROUGH,
            "hooks.jsonl",
            second_without("UserPromptExpansion", "changelog:write"),
            "the person typed /changelog:write 1 time, not 2",
        ),
        (
            WALKTHROUGH,
            "hooks.jsonl",
            second_without("lay.py write"),
            "lay.py write ran 1 time, not 2",
        ),
        (
            WALKTHROUGH,
            "run.diff",
            lambda lines: [x.replace(" at the top of ", " into ") for x in lines],
            "writer's step 3 is as the walkthrough gives it",
        ),
        (
            AI_APPROVES,
            "hooks.jsonl",
            without('"skill": "lane:up"'),
            "the AI called no lane:up",
        ),
        (
            AI_APPROVES,
            "hooks.jsonl",
            lambda lines: [
                json.dumps(
                    {
                        "time": "t",
                        "payload": {
                            "hook_event_name": "UserPromptExpansion",
                            "command_name": "lane:up",
                        },
                    }
                )
                + "\n",
                *lines,
            ],
            "the person typed /lane:up, where the AI calls up",
        ),
    ],
    ids=[
        "a turn that failed",
        "no reload",
        "one typed write",
        "laid once",
        "the step unchanged",
        "up uncalled",
        "up typed",
    ],
)
def test_a_run_that_went_otherwise_is_named_where(
    tmp_path: Any, records: str, name: str, change: Any, said: str
) -> None:
    """Given: a copy of the pilot records, broken in one way that the case doesn't mean: a turn that
    failed, such as at the usage limit; no /reload-plugins after a lay; the walkthrough's
    /changelog:write typed once, or Lane laid once, or writer's step 3 left as it was; or, for S3,
    up never called by the AI, or typed by the person.
    When: otherwise checks it.
    Then: it names where the run went otherwise."""
    assert m.otherwise(broken(tmp_path, records, name, change), file_of(records)) == [said]


# The lines of the transcripts that tell how each hook ran, out of the second pilot run of each E2E
# test file, on Claude Code 2.1.325 and Opus: in ai-approves's, Lane's guard failed with a
# traceback where the AI started writer; in the walkthrough's, it only stopped calls by its rules.
HOOKS = os.path.join(FIXTURES, "hooks")
CRASH = (
    "transcripts/a241dfc0-806e-49cd-ac45-99a4f1ba8b2d.jsonl: PreToolUse:Agent hook error: "
    "[python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py]: failed; blocking because onFailure is "
    '"block"'
)


def attachment(**fields: Any) -> str:
    """A transcript's line of an attachment with the fields."""
    return json.dumps({"type": "attachment", "attachment": fields}) + "\n"


def summary(*errors: str) -> str:
    """A transcript's line of the summary of the Stop hooks, with the errors they gave."""
    return (
        json.dumps({"type": "system", "subtype": "stop_hook_summary", "hookErrors": errors}) + "\n"
    )


LANE = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py"
SESSION = "transcripts/7128c6cc-8ab4-4c58-a92d-9705a35a869d.jsonl"


@pytest.mark.supports("KR1.1")
def test_a_lane_hook_that_failed_is_named_where() -> None:
    """Given: the hook lines of ai-approves's second pilot run, where Lane's guard failed with a
    traceback, and Claude Code blocked the start of writer as the hook's onFailure says.
    When: hook_faults reads them.
    Then: it names the transcript and the failure, and nothing else."""
    assert m.hook_faults(os.path.join(HOOKS, "ai-approves")) == [CRASH]


@pytest.mark.supports("KR1.1")
def test_a_lane_hook_that_stops_a_call_by_its_rules_is_no_fault() -> None:
    """Given: the hook lines of the walkthrough's second pilot run, where Lane's guard only stopped
    calls and ends by its rules, each shown as a hook error with the rule's words.
    When: hook_faults reads them.
    Then: it names nothing."""
    assert m.hook_faults(os.path.join(HOOKS, "walkthrough")) == []


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize(
    "line, said",
    [
        (
            attachment(
                type="hook_non_blocking_error",
                hookEvent="PostToolUse",
                command=LANE,
                exitCode=1,
                stderr="Traceback (most recent call last):",
            ),
            f"{SESSION}: PostToolUse hook_non_blocking_error of [{LANE}], exit 1",
        ),
        (
            attachment(type="hook_error_during_execution", hookEvent="Stop", command=LANE),
            f"{SESSION}: Stop hook_error_during_execution of [{LANE}]",
        ),
        (
            attachment(type="hook_cancelled", hookEvent="SubagentStop", command=LANE),
            f"{SESSION}: SubagentStop hook_cancelled of [{LANE}]",
        ),
        (
            summary(f'[{LANE}]: failed; blocking because onFailure is "block"\nTraceback'),
            f'{SESSION}: [{LANE}]: failed; blocking because onFailure is "block"',
        ),
        (
            summary(
                "changelog: End by running `python3 <run>/clone/changelog/hooks/lane/result.py`"
            ),
            None,
        ),
        (
            attachment(
                type="hook_blocking_error",
                hookEvent="SubagentStop",
                blockingError={"blockingError": f"[{LANE}]: failed\nTraceback", "command": LANE},
            ),
            f"{SESSION}: [{LANE}]: failed",
        ),
        (
            attachment(type="hook_non_blocking_error", hookEvent="Stop", command=LANE, exitCode=2),
            None,
        ),
        (
            attachment(
                type="hook_non_blocking_error",
                hookEvent="PostToolUse",
                command="python3 <top>/dev/scripts/e2e.py hook <run>/hooks.jsonl",
                exitCode=1,
            ),
            None,
        ),
    ],
    ids=[
        "exit 1",
        "not run",
        "cancelled",
        "at stop",
        "a stop at Stop by its rules",
        "blocking at SubagentStop",
        "a stop by its rules",
        "not Lane's",
    ],
)
def test_each_way_a_lane_hook_fails_is_named(tmp_path: Any, line: str, said: str | None) -> None:
    """Given: a copy of the walkthrough's hook lines, with one more line where a hook ran: Lane's
    exited 1, couldn't run, was cancelled, or failed at Stop or SubagentStop, where its onFailure
    blocks; or Lane's stopped an end or a call by its rules, or another hook than Lane's failed.
    When: hook_faults reads it.
    Then: it names Lane's failure, and nothing for a stop by Lane's rules or another's hook."""
    copy = broken(tmp_path, os.path.join(HOOKS, "walkthrough"), SESSION, lambda x: [*x, line])
    assert m.hook_faults(copy) == ([said] if said else [])
