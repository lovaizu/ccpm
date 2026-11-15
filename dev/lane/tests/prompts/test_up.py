"""The unit cases of up's prompt, skills/up/SKILL.md with domain/up.md, on the model, as Lane's Test
strategy says: up alone on Opus by `claude -p`, in a throwaway copy of tally with the walkthrough's
changelog, each case run RUNS times, a run a test of its own, and the developer adds runs until one
more changes no case's count. Each case reads by code what up's record shows: the Proposal that
lay.py print kept, its Lanes and Routes, and the Steps' files. They run on the developer's login, so
a case without CLAUDE_CODE_OAUTH_TOKEN is skipped."""

from __future__ import annotations

import glob
import os
import subprocess
from typing import Any

import pytest
import walkthrough as w

pytestmark = [
    pytest.mark.xfail(strict=True, reason="up's steps are empty"),
    pytest.mark.skipif(
        not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"), reason="runs the real Claude Code on Opus"
    ),
]

RUNS = 5
RULE = (
    "Install nothing, and send nothing to a translator, a web API, or any other service outside"
    " this repository's git."
)


def up(tmp: str, prompt: str, files: dict[str, str] | None = None) -> tuple[w.Bench, str]:
    """Runs the prompt on Opus, with Lane and changelog loaded, in a throwaway tally, and gives the
    bench with what Claude Code printed."""
    b = w.bench(tmp, files)
    env = dict(b.env, CLAUDE_CODE_OAUTH_TOKEN=os.environ["CLAUDE_CODE_OAUTH_TOKEN"])
    env["CLAUDE_CONFIG_DIR"] = os.path.join(tmp, "config")
    command = ["claude", "-p", "--model", "opus", "--permission-mode", "bypassPermissions"]
    command += ["--append-system-prompt", RULE, "--plugin-dir", b.lane, "--plugin-dir", b.changelog]
    done = subprocess.run(
        [*command, prompt],
        cwd=b.repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    return b, done.stdout


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
    ("reviewer", "agents/reviewer.md", 2, "ends_by_result"),
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
        "2. Check each entry against its commit.",
    )
    files = dict(w.FILES, **{"agents/reviewer.md": reviewer})
    b, printed = up(str(tmp_path), "/lane:up changelog", files)
    _, routes = lanes_and_routes(kept(b, printed))
    moves = [m for after, each in routes if after.role == "reviewer" for m in each]
    assert {m.kind for m in moves} == {"start", "no_more"}
    assert [m.role for m in moves if m.kind == "start"] == ["writer"]
