"""The unit cases of up's prompt, skills/up/SKILL.md with domain/up.md, on the model, as Lane's Test
strategy says: up alone on Opus by `claude -p`, in a throwaway copy of tally with the walkthrough's
changelog, each case run RUNS times, a run a test of its own, and the developer adds runs until one
more changes no case's count. Each case reads by code what up's record shows: the Proposal that
lay.py print kept, its Lanes and Routes, and the Steps' files. They run on the developer's login, so
a case without it is skipped, as opus.NEEDS_LOGIN says."""

from __future__ import annotations

import glob
import json
import os
from typing import Any

import opus
import pytest
import walkthrough as w

pytestmark = opus.NEEDS_LOGIN

RUNS = 5


def up(tmp: str, prompt: str, files: dict[str, str] | None = None) -> tuple[w.Bench, str]:
    """Runs the prompt on Opus, with Lane and changelog loaded, in a throwaway tally, and gives the
    bench with the run's last message. The run's record, each event as Claude Code streamed it, is
    kept in the case's folder as record.jsonl, and its path printed, which pytest shows where the
    case fails, so that the maintainer reads what the AI did and tells a fault of up from one of
    the case."""
    b = w.bench(tmp, files)
    env = dict(b.env, CLAUDE_CONFIG_DIR=os.path.join(tmp, "config"))
    flags = ["--plugin-dir", b.lane, "--plugin-dir", b.changelog]
    record = opus.prompted(
        prompt, b.repo, env, [*flags, "--output-format", "stream-json", "--verbose"], 900
    )
    path = os.path.join(tmp, "record.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(record)
    print(f"record: {path}")
    ended = last_result(record)
    assert ended.get("terminal_reason") != "api_error", f"the run reached no model: {path}"
    return b, str(ended.get("result", ""))


def last_result(record: str) -> dict[str, Any]:
    """The record's last result event, which holds the run's last message, or an empty one where
    the run gave none."""
    events = [json.loads(line) for line in record.splitlines() if line.startswith("{")]
    return next((e for e in reversed(events) if e.get("type") == "result"), {})


def kept(b: w.Bench, printed: str) -> Any:
    """The Proposal that lay.py print kept, by the ID that up showed."""
    from lay.proposals import find

    found = w.in_temp(b, find, b.changelog, w.proposal_id(printed))
    assert found, "no Proposal is kept by the ID up showed"
    return found.proposal


def laid(b: w.Bench) -> Any:
    """The Proposal that lay.py write laid in changelog's lanes.json."""
    from form import read_lanes

    return read_lanes(os.path.join(b.changelog, "hooks", "lanes.json")).proposal


def none_kept(b: w.Bench) -> bool:
    """Whether lay.py print kept no Proposal of changelog."""
    return not glob.glob(os.path.join(b.env["TMPDIR"], "lane", "*-changelog"))


def lanes_and_routes(proposal: Any) -> tuple[set[Any], set[Any]]:
    """The Proposal's Lanes, by role, file, step, and type, and its Routes, by what each goes
    after and its moves."""
    lanes = {(x.role, x.file, x.step, x.type) for x in proposal.lanes}
    routes = {(r.after, r.moves) for r in proposal.routes}
    return lanes, routes


WALKTHROUGH_LANES = {
    ("write", "skills/write/SKILL.md", 1, "routes"),
    ("write", "skills/write/SKILL.md", 1, "ends_by_result"),
    ("writer", "agents/writer.md", 2, "run_only"),
    ("writer", "agents/writer.md", 3, "write_only"),
    ("writer", "agents/writer.md", 4, "ends_by_result"),
    ("reviewer", "agents/reviewer.md", 2, "write_only"),
    ("reviewer", "agents/reviewer.md", 3, "ends_by_result"),
}


def walkthrough_routes() -> set[Any]:
    """The walkthrough's Routes, as lanes_and_routes gives them."""
    from form import After, Move

    return {
        (After("first"), (Move("start", role="writer"),)),
        (After("result", role="writer", result="written"), (Move("start", role="reviewer"),)),
        (After("result", role="reviewer", result="more"), (Move("start", role="writer"),)),
        (After("result", role="reviewer", result="good"), (Move("no_more", result="good"),)),
    }


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
@pytest.mark.parametrize("run", range(RUNS))
def test_a_typed_up_proposes_the_walkthroughs_lanes_and_routes(tmp_path: Any, run: int) -> None:
    """Given: tally with the walkthrough's changelog, and Lane loaded.
    When: the person types /lane:up changelog.
    Then: up's kept Proposal holds the walkthrough's Lanes and Routes, it shows what lay.py print
    showed, and lays nothing before a reply."""
    b, printed = up(str(tmp_path), "/lane:up changelog")
    assert lanes_and_routes(kept(b, printed)) == (WALKTHROUGH_LANES, walkthrough_routes())
    assert "Reply yes to lay these into changelog" in printed
    assert not os.path.exists(os.path.join(b.changelog, "hooks", "lanes.json"))


@pytest.mark.supports("test_an_ai_lays_by_its_own_run_of_lay")
@pytest.mark.parametrize("run", range(RUNS))
def test_an_ais_ask_calls_up_and_lays_by_its_own_act(tmp_path: Any, run: int) -> None:
    """Given: tally with the walkthrough's changelog, and Lane loaded.
    When: the main conversation is asked to have Lane hold changelog to its steps itself, without
    waiting for anyone.
    Then: up is called, its Proposal holds the walkthrough's Lanes and Routes, and lay.py write
    lays it."""
    ask = "Have Lane hold the plugin in changelog/ to its steps. Approve Lane's proposal yourself."
    b, _ = up(str(tmp_path), ask)
    assert lanes_and_routes(laid(b)) == (WALKTHROUGH_LANES, walkthrough_routes())


# The words of S3's first E2E stand-in, whose run went on to write's work before /reload-plugins.
S3_ASK = (
    "I'm working on the Claude Code plugin in changelog/. Please have Lane keep the plugin on its"
    " steps without me. When Lane makes a proposal, approve it yourself and don't stop to ask me."
    " After that, do the work of /changelog:write and keep going until the entries pass review."
)


def plugin_calls(tmp: str) -> list[dict[str, Any]]:
    """Each call that the run's record shows of changelog's skill, its roles, or its result.py."""
    with open(os.path.join(tmp, "record.jsonl"), encoding="utf-8") as f:
        events = [json.loads(line) for line in f if line.startswith("{")]
    uses = [
        block["input"]
        for e in events
        if e.get("type") == "assistant"
        for block in e["message"].get("content", [])
        if isinstance(block, dict) and block.get("type") == "tool_use"
    ]
    named = ("changelog:", "changelog/hooks/lane/result.py")
    return [u for u in uses if any(n in json.dumps(u) for n in named)]


@pytest.mark.supports("test_an_ai_lays_by_its_own_run_of_lay")
@pytest.mark.parametrize("run", range(RUNS))
def test_an_ai_asks_for_reload_plugins_before_the_plugins_work(tmp_path: Any, run: int) -> None:
    """Given: tally with the walkthrough's changelog, and Lane loaded.
    When: the main conversation is asked to have Lane hold changelog to its steps, approving the
    Proposal itself, and then to do /changelog:write's work.
    Then: lay.py write lays the Proposal, the run calls no skill, role, or result.py of changelog,
    and its last message asks for /reload-plugins, as the rules hold only after it."""
    b, said = up(str(tmp_path), S3_ASK)
    assert os.path.exists(os.path.join(b.changelog, "hooks", "lanes.json"))
    assert plugin_calls(str(tmp_path)) == []
    assert "/reload-plugins" in said


def ups_results(b: w.Bench) -> list[str]:
    """Each Result of up that Lane's run record of the run holds, as the guard took it."""
    results = []
    for path in glob.glob(os.path.join(b.env["TMPDIR"], "lane", "*", "record.jsonl")):
        with open(path, encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        results += [x["result"] for x in lines if x["kind"] == "Gave" and x["role"] == "up"]
    return results


@pytest.mark.supports("test_an_ai_lays_by_its_own_run_of_lay")
@pytest.mark.parametrize("run", range(RUNS))
def test_an_ais_up_ends_its_run_by_its_result(tmp_path: Any, run: int) -> None:
    """Given: tally with the walkthrough's changelog, and Lane loaded.
    When: the main conversation is asked to have Lane hold changelog to its steps, approving the
    Proposal itself, and then to do /changelog:write's work.
    Then: lay.py write lays the Proposal, and the guard takes up's Result `laid`, which ends up's
    Run, as it takes one only from result.py run as a command of its own, by its path."""
    # The words of S3's second E2E stand-in, whose AI ran up's result.py after `cd`.
    ask = (
        "I'm working on the changelog plugin in changelog/. Could you have Lane keep the plugin on"
        " its steps by itself? Approve Lane's proposal yourself so you don't have to check with"
        " me, then run what /changelog:write does until the entries pass review."
    )
    b, _ = up(str(tmp_path), ask)
    assert os.path.exists(os.path.join(b.changelog, "hooks", "lanes.json"))
    assert ups_results(b) == ["laid"], "up's Result is taken once, as `laid`"


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
@pytest.mark.parametrize("run", range(RUNS))
def test_an_ask_up_isnt_for_leaves_up_uncalled(tmp_path: Any, run: int) -> None:
    """Given: tally with the walkthrough's changelog, and Lane loaded.
    When: the main conversation is asked to write the CHANGELOG.md entries.
    Then: up isn't called: no Proposal is kept."""
    b, _ = up(str(tmp_path), "Write the CHANGELOG.md entries for the commits since 0.1.0.")
    assert none_kept(b)


@pytest.mark.supports("test_a_file_that_cant_carry_the_proposal_goes_to_the_user")
@pytest.mark.parametrize("run", range(RUNS))
def test_up_tells_what_to_fix_in_a_file_that_cant_carry_it(tmp_path: Any, run: int) -> None:
    """Given: changelog whose agents/reviewer.md doesn't set `background: true`.
    When: the person types /lane:up changelog.
    Then: up names agents/reviewer.md and `background: true`, and keeps no Proposal."""
    files = dict(w.FILES, **{"agents/reviewer.md": w.REVIEWER.replace("background: true\n", "")})
    b, printed = up(str(tmp_path), "/lane:up changelog", files)
    assert "agents/reviewer.md" in printed and "background: true" in printed
    assert none_kept(b)


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
@pytest.mark.parametrize("run", range(RUNS))
def test_up_proposes_from_the_steps_alone_and_names_a_missing_result(
    tmp_path: Any, run: int
) -> None:
    """Given: changelog whose reviewer's last step names no Result: `Check each entry against its
    commit.`.
    When: the person types /lane:up changelog.
    Then: up's Proposal still routes reviewer's Results back to writer or to no more, each by a
    Result's name it proposes."""
    reviewer = w.REVIEWER.replace(
        w.REVIEWER.splitlines()[-1],
        "3. Check each entry against its commit.",
    )
    files = dict(w.FILES, **{"agents/reviewer.md": reviewer})
    b, printed = up(str(tmp_path), "/lane:up changelog", files)
    _, routes = lanes_and_routes(kept(b, printed))
    moves = [m for after, each in routes if after.role == "reviewer" for m in each]
    assert {m.kind for m in moves} == {"start", "no_more"}
    assert [m.role for m in moves if m.kind == "start"] == ["writer"]


# writer's Steps as Lane's page of steps, routes, and adapters writes each kind that the lane types
# of Steps hold: a file read whole, a path never read, a checklist of the plugin's, and Steps done
# in order.
STEPS_WRITER = w.MARKED_WRITER.replace(
    "4. Reply with the entries you wrote.",
    "4. Reply with the entries you wrote. Do these steps in order, each one done before the next.",
)


@pytest.mark.supports("test_a_proposal_of_the_lane_types_of_steps_shows_each_steps_sentence")
@pytest.mark.parametrize("run", range(RUNS))
def test_up_proposes_the_lane_types_of_steps_where_the_steps_say_them(
    tmp_path: Any, run: int
) -> None:
    """Given: changelog whose writer reads CHANGELOG.md whole, never reads tally.py, keeps the
    changelog's checklist on its step 3, and does its steps in order, with an adapter of a step's
    items in hooks/adapters/.
    When: the person types /lane:up changelog.
    Then: up's kept Proposal lays reads_whole on writer's step 1 for `CHANGELOG.md`, reads_none on
    its step 2 for `tally.py`, keeps_items on its step 3, and keeps_steps on its step 4, and names
    the adapter as that of a step's items, while reviewer, whose steps say none of them, gets
    none."""
    files = dict(w.FILES, **{"agents/writer.md": STEPS_WRITER, w.ITEMS: w.ITEMS_ADAPTER})
    b, printed = up(str(tmp_path), "/lane:up changelog", files)
    proposal = kept(b, printed)
    lanes, _ = lanes_and_routes(proposal)
    steps_kinds = {"reads_whole", "reads_none", "keeps_items", "keeps_steps"}
    assert {x for x in lanes if x[3] in steps_kinds} == {
        ("writer", "agents/writer.md", 1, "reads_whole"),
        ("writer", "agents/writer.md", 2, "reads_none"),
        ("writer", "agents/writer.md", 3, "keeps_items"),
        ("writer", "agents/writer.md", 4, "keeps_steps"),
    }
    paths = {x.type: x.args.get("paths") for x in proposal.lanes if x.type.startswith("reads")}
    assert paths == {"reads_whole": ["CHANGELOG.md"], "reads_none": ["tally.py"]}
    assert proposal.adapters.items == w.ITEMS
