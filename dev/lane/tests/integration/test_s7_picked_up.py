"""The integration cases of S7, a run picked up, and of the rules that hold a Run apart from all
else: the laid guard, the run record, and the adapter of the plugin's records joined through the
double of Claude Code, on each path of S7's sequence."""

from __future__ import annotations

import json
import os
import shutil
from typing import Any

import pytest
import walkthrough as w

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")


# An adapter of changelog's records that picks up only where the words typed after the command,
# which it reads on standard input, begin with `--continue`, and else gives no results.
BY_WORDS = """#!/usr/bin/env python3
import json, sys
words = json.load(sys.stdin)["words"]
results = [{"role": "writer", "result": "written"}] if words.startswith("--continue") else []
print(json.dumps({"results": results}))
"""


def records_bench(
    tmp: str, results: list[dict[str, str]] | None, fails: bool = False, program: str = ""
) -> w.Bench:
    """The bench, with an adapter of changelog's records that prints the results, or fails, or
    runs the program given."""
    if fails:
        program = "#!/usr/bin/env python3\nimport sys\nsys.exit('records.jsonl is not JSON')\n"
    else:
        printed = json.dumps({"results": results or []})
        program = program or f"#!/usr/bin/env python3\nprint({printed!r})\n"
    b = w.bench(tmp, dict(w.FILES, **{"hooks/adapters/records.py": program}))
    w.executable(os.path.join(b.changelog, "hooks", "adapters", "records.py"))
    return b


def with_records() -> dict[str, Any]:
    proposal = w.walkthrough_proposal()
    proposal["adapters"] = {"records": "hooks/adapters/records.py"}
    return proposal


@pytest.mark.supports("S7", "The run kept in a file", "Run")
def test_a_run_goes_on_after_compact(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, and writer gave `written` in a run of
    /changelog:write.
    When: the person types /compact, then /changelog:write again.
    Then: the guard gives reviewer's start due, as the run record holds the Run."""
    c, writer = w.writer_started(b)
    w.give(b, writer, "written")
    c.compact()
    assert w.due("reviewer") in c.type("/changelog:write").said


@pytest.mark.supports("S7", "Run")
def test_a_new_conversation_without_an_adapter_starts_over(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid with no adapter, and writer gave `written` in an
    earlier conversation.
    When: the person types /changelog:write in a new conversation.
    Then: the guard gives writer's start due, as a new Run."""
    _, writer = w.writer_started(b)
    w.give(b, writer, "written")
    assert w.due("writer") in w.converse(b).type("/changelog:write").said


@pytest.mark.supports("S7", "adapter", "Kept results")
def test_a_new_conversation_picks_up_from_the_kept_results(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of changelog's records that gives writer's
    `written`.
    When: the person types /changelog:write 0.2.0 in a new conversation.
    Then: the guard says where the run picks up, and gives reviewer's start due."""
    b = records_bench(str(tmp_path), [{"role": "writer", "result": "written"}])
    c = w.laid(b, make=with_records)
    called = c.type("/changelog:write 0.2.0")
    assert not called.blocked
    assert "written" in called.said and w.due("reviewer") in called.said


@pytest.mark.supports("S7", "adapter", "Kept results")
def test_the_words_typed_tell_a_new_request_from_a_pick_up(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of changelog's records that gives writer's
    `written` only where the words it reads on standard input begin with `--continue`.
    When: the person types /changelog:write --continue in a new conversation, and
    /changelog:write 0.3.0 in another.
    Then: the guard gives reviewer's start due for the first, picked up, and writer's for the
    second, a new Run."""
    b = records_bench(str(tmp_path), None, program=BY_WORDS)
    w.lay(b, with_records)
    assert w.due("reviewer") in w.converse(b).type("/changelog:write --continue").said
    assert w.due("writer") in w.converse(b).type("/changelog:write 0.3.0").said


@pytest.mark.supports("S7", "adapter", "Kept results")
def test_kept_results_that_reach_the_end_start_a_new_run(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of changelog's records that gives writer's
    `written` and reviewer's `good`, which reaches a Route that starts no more.
    When: the person types /changelog:write in a new conversation.
    Then: the guard gives writer's start due, as a new Run."""
    results = [{"role": "writer", "result": "written"}, {"role": "reviewer", "result": "good"}]
    c = w.laid(records_bench(str(tmp_path), results), make=with_records)
    assert w.due("writer") in c.type("/changelog:write").said


@pytest.mark.supports("S7", "adapter")
def test_no_kept_results_start_a_new_run(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of changelog's records that gives no results.
    When: the person types /changelog:write in a new conversation.
    Then: the guard gives writer's start due."""
    c = w.laid(records_bench(str(tmp_path), []), make=with_records)
    assert w.due("writer") in c.type("/changelog:write").said


@pytest.mark.supports("S7", "adapter", "Kept results")
def test_kept_results_off_the_routes_stop_the_command(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of changelog's records that gives reviewer's
    `good` first, which no Route leads to.
    When: the person types /changelog:write in a new conversation.
    Then: the guard stops the command, with why and who must fix it."""
    b = records_bench(str(tmp_path), [{"role": "reviewer", "result": "good"}])
    c = w.laid(b, make=with_records)
    stopped = c.type("/changelog:write")
    assert stopped.blocked and "reviewer" in stopped.said


@pytest.mark.supports("S7", "adapter")
def test_an_adapter_of_records_that_fails_stops_the_command(tmp_path: Any) -> None:
    """Given: the Proposal laid with an adapter of changelog's records that exits 1 with
    `records.jsonl is not JSON`.
    When: the person types /changelog:write in a new conversation.
    Then: the guard stops the command, with the adapter's why and who must fix it."""
    c = w.laid(records_bench(str(tmp_path), None, fails=True), make=with_records)
    stopped = c.type("/changelog:write")
    assert stopped.blocked and "records.jsonl is not JSON" in stopped.said


@pytest.mark.supports("The guard checks only the run", "guard")
def test_calls_outside_the_run_go_unchecked(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, and its run of /changelog:write ended by
    result.py write good.
    When: the main conversation starts changelog:writer.
    Then: the guard lets the start through, as it lies outside every Run."""
    c = w.laid(b)
    w.give(b, w.to_reviewer(b, c), "good")
    assert c.bash(b.result("write", "good")).exit_code == 0
    started, _ = w.start(c, "writer")
    assert not started.blocked


@pytest.mark.supports("The laid plugin runs alone", "guard", "result.py")
def test_the_laid_plugin_holds_its_run_without_lane(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, then Lane's folder removed.
    When: in a conversation with changelog alone, the person types /changelog:write, and writer
    runs `git -C <tally> log --oneline`.
    Then: the guard of changelog's own copy stops the call with its step's sentence."""
    w.lay(b)
    shutil.rmtree(b.lane)
    c = w.converse(b, lane=False)
    assert w.due("writer") in c.type("/changelog:write").said
    _, writer = w.start(c, "writer")
    assert writer
    stopped = writer.bash(f"git -C {b.repo} log --oneline")
    assert stopped.blocked and "Run only `git log --oneline`." in stopped.said
