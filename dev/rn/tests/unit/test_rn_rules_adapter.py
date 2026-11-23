"""The unit cases of lane/adapters/rules.py, the steps that rn gives Lane: `steps`, one for each
event of the orchestrator's turn, the hearing of /rn:on, first or typed again, the user's words
after it beside no run, a run signed off, one whose worktree isn't here, one done, and a newer one
whose plan waits, the words after /rn:on typed again, an answer, a role's end, and a sign-off in the
run that a conversation of /rn:on made, though another is newer, made the day before, or not made, a
turn after /rn:up typed in it, a pick-up of one run among none, one, and several, newest by its last
commit, its worktree there or gone, a sign-off, a pause, a send-back, an answer, another prompt, a
role's end as Claude Code gives it, and a prompt that nearly names a command, and a turn other than
the hearing and a new request with no run or outside a git repository; each step of a turn, the last
and each other, by whether it ends on `blocked`; one for each class of the generator's Cut, its
inputs at none, one, and several, a folder among them, a deliverable of more than one path, a
refactor Round, and a run's own best practice; one for each class of the evaluator's Cut, with no
other Round and with several; and each refusal, a role of another plugin or one that nearly
matches rn's, and a prompt that names no Cut in its form; and `main`, for each exit it gives.

Each input is in the form of Lane's rules.in.schema.json, read from the JSON of its text, and each
Then holds the whole of the steps, each path exactly as the contract gives it,
`os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))`, so that a folder outside the
repository, such as rn's best practices or the people's folder, comes as `../...`, and the rules of
a step and the paths of a rule taken in any order, as the contract orders neither."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any
from urllib.parse import quote

import pytest
import rn_files
from claude_code import RUN, line
from fault import Wrong
from rn_adapters import adapter
from rn_files import COMMAND, GUIDE, RN, WORDS
from rn_runs import branch_run

ADAPTER = adapter("rules")
NAME = f"{date.today():%Y%m%d}-{rn_files.NAMED}"
# The prompt of a subagent's end in the background, as Claude Code gives the main conversation.
ENDED = line(RUN, "writer's end reaches the main conversation")["payload"]["prompt"]


# rn's commands, each by its skill.
COMMANDS = ("rn:on", "rn:up", "rn:dn", "rn:ty", "rn:gm")


def typed(prompt: str, skill: str) -> str | None:
    """The command that a turn of the prompt called, as Lane gives it where the user types it: the
    skill of the command that the prompt types, the run's skill for the run's first turn, whose
    prompt is empty, and None for words that type none of rn's commands."""
    if not prompt:
        return skill
    first = prompt.partition(" ")[0].lstrip("/")
    return first if prompt.startswith("/") and first in COMMANDS else None


def turn(role: str, prompt: str, skill: str = "rn:on") -> dict[str, Any]:
    """An earlier turn as Lane gives it, with the command that its prompt typed."""
    return {"role": role, "prompt": prompt, "command": typed(prompt, skill)}


def given(
    role: str,
    prompt: str,
    skill: str = "rn:up",
    turns: Sequence[Mapping[str, Any]] = (),
    command: str | None = "",
) -> dict[str, Any]:
    """What Lane gives the adapter, read from the JSON of its text, the run's words empty, as rn's
    commands take none but /rn:gm's, with the earlier turns given, none unless given, and the
    command given, else the one that the prompt typed."""
    run = {"skill": skill, "words": ""}
    called = typed(prompt, skill) if command == "" else command
    text = json.dumps(
        {"run": run, "role": role, "prompt": prompt, "command": called, "turns": list(turns)}
    )
    return json.loads(text)


# The earlier turns of a conversation of /rn:on: its first turn, the hearing, with an empty prompt;
# and that turn and the request, the user's words after it.
HEARD = [turn("rn:on", "")]
ASKED = [*HEARD, turn("rn:on", WORDS)]


def shown(steps: Mapping[str, Any]) -> list[tuple[str, list[str]]]:
    """Each step's name with its rules as the adapter gives them, each rule as sorted JSON with its
    paths sorted, as the contract orders neither."""
    found = []
    for each_step in steps["steps"]:
        rules = []
        for rule in each_step["rules"]:
            each = dict(rule)
            if "paths" in each:
                each["paths"] = sorted(each["paths"])
            rules.append(json.dumps(each, sort_keys=True))
        found.append((each_step["name"], sorted(rules)))
    return found


def rel(path: str, cwd: str) -> str:
    """The path as Lane compares it, and the contract gives it:
    `os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))`, a folder keeping its
    closing `/`."""
    given_path = os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))
    return given_path + "/" if path.endswith("/") else given_path


def relative(expected: list[tuple[str, list[str]]], cwd: str) -> list[tuple[str, list[str]]]:
    """The steps built with absolute paths, each absolute path given as `rel` gives it."""
    found = []
    for name, rules in expected:
        shown_rules = []
        for text in rules:
            rule = json.loads(text)
            if "paths" in rule:
                rule["paths"] = sorted(
                    rel(p, cwd) if os.path.isabs(p) else p for p in rule["paths"]
                )
            shown_rules.append(json.dumps(rule, sort_keys=True))
        found.append((name, sorted(shown_rules)))
    return found


def step(name: str, *rules: Mapping[str, Any]) -> tuple[str, list[str]]:
    """A step as `shown` gives it, with `order` and the rules given, its paths absolute until
    `relative` gives each as Lane compares it."""
    each: list[Mapping[str, Any]] = [{"type": "order"}, *rules]
    shown = []
    for given_rule in each:
        rule: dict[str, Any] = dict(given_rule)
        if "paths" in rule:
            rule["paths"] = sorted(rule["paths"])
        shown.append(json.dumps(rule, sort_keys=True))
    return name, sorted(shown)


def writes(*paths: str) -> dict[str, Any]:
    return {"type": "writes", "paths": list(paths)}


# The rule of each step of the orchestrator's turn but its last.
BLOCKED = {"type": "result", "ends": ["blocked"]}


def shared(cwd: str, name: str = NAME) -> list[tuple[str, list[str]]]:
    """The steps that every event but a pause shares, on the run of the name."""
    run = os.path.relpath(rn_files.folder_of(cwd, name), cwd)
    return [
        step("review", BLOCKED),
        step(
            "touched",
            {"type": "checklist", "command": f"python3 {RN}/scripts/tree.py touched {run}"},
            BLOCKED,
        ),
        step("commit", BLOCKED),
        step("move", BLOCKED),
        step("final"),
    ]


def paused_run(cwd: str, name: str = NAME, done: bool = False) -> str:
    """Writes a run of the name under the repository's top, as files alone, its command open, or
    each of its deliverables done; gives its folder."""
    tree = rn_files.walkthrough_tree(name)
    if done:
        tree = rn_files.tree(
            [rn_files.done_node(rn_files.GOAL, rn_files.plan_path(name), "design-tree")]
        )
    return rn_files.run_folder(cwd, name, tree)


def a_run(
    repo: str,
    name: str = NAME,
    tree: Mapping[str, Any] | None = None,
    when: str = "2026-11-20T09:00:00",
    worktree: bool = True,
) -> str:
    """Makes a run of the name in the repository as a run leaves it, its branch and its committed
    design tree, the walkthrough's unless given, its plan done, at the time given; gives its
    folder."""
    return branch_run(repo, name, tree or rn_files.walkthrough_tree(name), when, worktree)


def unsigned(name: str = NAME) -> dict[str, Any]:
    """The design tree of a run whose plan waits for the user's goal and sign-off."""
    return rn_files.tree([rn_files.plan(name, good=False)], goal=rn_files.GOAL, by="reasoning")


def done_tree(name: str) -> dict[str, Any]:
    """The design tree of a run whose every deliverable is done."""
    return rn_files.tree(
        [rn_files.done_node(rn_files.GOAL, rn_files.plan_path(name), "design-tree")]
    )


@pytest.fixture
def cwd(tmp_path: Any) -> str:
    """The top of the user's repository, with no run, as files alone."""
    folder = os.path.join(str(tmp_path), "repo")
    os.makedirs(folder)
    return os.path.realpath(folder)


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The top of the user's git repository, with a commit and no run."""
    return rn_files.repository(os.path.join(str(tmp_path), "git"), {"README.md": "invoicer\n"})


# The orchestrator's turn, by its event.

HEAR = step("hear")
START = step("start", BLOCKED)
FIND = step("find", BLOCKED)
TAKE = step("take", BLOCKED)


@pytest.mark.supports("test_rn_on_asks_what_to_make_letting_its_commands_through")
@pytest.mark.parametrize(
    ("prompt", "turns"), [("", []), ("/rn:on", ASKED)], ids=["first-turn", "typed-again"]
)
def test_the_hearing_takes_hear_alone(repo: str, prompt: str, turns: list[dict[str, str]]):
    """Given a repository with a run whose plan waits, and a turn of /rn:on, the run's first or
    typed again after a request
    When the adapter gives the turn's steps
    Then they are `hear` alone, held in order, with no rule of results, as it's the turn's last"""
    a_run(repo, tree=unsigned())
    steps = ADAPTER.steps(given("rn:on", prompt, skill="rn:on", turns=turns), repo, RN)
    assert shown(steps) == [HEAR]


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@pytest.mark.parametrize(
    "before",
    ["none", "signed", "no-worktree", "done", "waiting"],
)
def test_the_words_after_the_hearing_start_by_repository_py_new_then_the_shared_steps(
    repo: str, before: str
):
    """Given a repository with no run, a run whose plan is signed off, a run with its plan waiting
    whose worktree isn't here, a run whose every deliverable is done, or a paused run here, newest
    by its last commit, whose plan waits on its sign-off; and a turn of rn:on whose prompt is the
    user's words, after the run's first turn, the hearing
    When the adapter gives the turn's steps
    Then they are `start` and the shared steps on the run named from today and the words"""
    other = "20261101-old"
    if before == "signed":
        a_run(repo, other)
    elif before == "no-worktree":
        a_run(repo, other, unsigned(other), worktree=False)
    elif before == "done":
        a_run(repo, other, done_tree(other))
    elif before == "waiting":
        a_run(repo, other, unsigned(other), when="2026-11-21T09:00:00")
    steps = ADAPTER.steps(given("rn:on", WORDS, skill="rn:on", turns=HEARD), repo, RN)
    assert shown(steps) == relative([START, *shared(repo)], repo)


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_the_words_after_the_hearing_typed_again_start_a_new_run(repo: str):
    """Given the run that a conversation of /rn:on made, its plan waiting, and a turn of rn:on whose
    prompt is the user's words for another run, after /rn:on typed again
    When the adapter gives the turn's steps
    Then they are `start` and the shared steps on the run named from today and the new words"""
    a_run(repo, tree=unsigned())
    turns = [*ASKED, turn("rn:on", "/rn:on")]
    steps = ADAPTER.steps(given("rn:on", "Receipts", skill="rn:on", turns=turns), repo, RN)
    other = f"{date.today():%Y%m%d}-receipts"
    assert shown(steps) == relative([START, *shared(repo, other)], repo)


@pytest.mark.supports(
    "test_a_point_only_the_user_can_settle_is_kept_open_and_their_answer_written_by_user",
    "test_an_answer_after_the_request_goes_into_the_run_the_request_made",
)
@pytest.mark.parametrize(
    "prompt", ["yes", "with each invoice", ENDED], ids=["goal", "point", "role-end"]
)
def test_an_answer_in_a_conversation_of_rn_on_takes_it_into_the_run_it_made(repo: str, prompt: str):
    """Given the run that a conversation of /rn:on made from the request's words, its plan waiting,
    and another paused run, newer by its last commit, whose plan waits too; and a turn of rn:on
    after the hearing and the request, whose prompt is the user's answer or a role's end
    When the adapter gives the turn's steps
    Then they are `take` and the shared steps on the run made, not a new request"""
    a_run(repo, tree=unsigned(), when="2026-11-20T09:00:00")
    a_run(repo, "20261101-old", unsigned("20261101-old"), when="2026-11-21T09:00:00")
    steps = ADAPTER.steps(given("rn:on", prompt, skill="rn:on", turns=ASKED), repo, RN)
    assert shown(steps) == relative([TAKE, *shared(repo)], repo)


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_an_answer_after_midnight_takes_it_into_the_run_made_the_day_before(repo: str):
    """Given the run that a conversation of /rn:on made from the request's words the day before,
    and a turn of rn:on after the hearing and the request, whose prompt is the user's answer
    When the adapter gives the turn's steps
    Then they are `take` and the shared steps on the run made the day before"""
    name = f"{date.fromordinal(date.today().toordinal() - 1):%Y%m%d}-{rn_files.NAMED}"
    a_run(repo, name, unsigned(name))
    steps = ADAPTER.steps(given("rn:on", "yes", skill="rn:on", turns=ASKED), repo, RN)
    assert shown(steps) == relative([TAKE, *shared(repo, name)], repo)


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_a_signoff_in_a_conversation_of_rn_on_records_it_on_the_run_it_made(repo: str):
    """Given the run that a conversation of /rn:on made, and another run, newer by its last commit;
    and a turn of rn:ty, /rn:ty typed after the hearing, the request, and an answer
    When the adapter gives the turn's steps
    Then they are `record` and the shared steps on the run made"""
    a_run(repo, tree=unsigned(), when="2026-11-20T09:00:00")
    a_run(repo, "20261101-old", when="2026-11-21T09:00:00")
    turns = [*ASKED, turn("rn:on", "yes")]
    steps = ADAPTER.steps(given("rn:ty", "/rn:ty", skill="rn:on", turns=turns), repo, RN)
    assert shown(steps) == relative([step("record", BLOCKED), *shared(repo)], repo)


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
def test_an_answer_after_a_request_that_made_no_run_takes_find_alone(repo: str):
    """Given a repository with another run but none of the request's words, as a refused `new`
    leaves it, and a turn of rn:on after the hearing and the request
    When the adapter gives the turn's steps
    Then they are `find` alone"""
    a_run(repo, "20261101-old")
    steps = ADAPTER.steps(given("rn:on", "yes", skill="rn:on", turns=ASKED), repo, RN)
    assert shown(steps) == [step("find")]


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_turn_after_a_pick_up_in_a_conversation_of_rn_on_takes_the_newest_run(repo: str):
    """Given the run that a conversation of /rn:on made, and another run, newer by its last commit;
    and a turn of rn:up, an answer after the hearing, the request, and /rn:up typed
    When the adapter gives the turn's steps
    Then they are `take` and the shared steps on the newest run, the one that the pick-up found"""
    a_run(repo, tree=unsigned(), when="2026-11-20T09:00:00")
    a_run(repo, "20261101-old", when="2026-11-21T09:00:00")
    turns = [*ASKED, turn("rn:up", "/rn:up")]
    steps = ADAPTER.steps(given("rn:up", "yes", skill="rn:on", turns=turns), repo, RN)
    old = "20261101-old"
    assert shown(steps) == relative([TAKE, *shared(repo, old)], repo)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_pick_up_finds_the_run_then_keeps_the_shared_steps(repo: str):
    """Given a repository with one run whose command is open, and a turn of /rn:up
    When the adapter gives the turn's steps
    Then they are `find` and the shared steps on that run"""
    a_run(repo)
    steps = ADAPTER.steps(given("rn:up", "", skill="rn:up"), repo, RN)
    assert shown(steps) == relative([FIND, *shared(repo)], repo)


@pytest.mark.supports("test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again")
def test_a_pick_up_of_a_run_whose_worktree_is_gone_names_its_paths_before_find_makes_it(
    repo: str,
):
    """Given a repository with one run whose worktree was removed, and a turn of /rn:up
    When the adapter gives the turn's steps
    Then they are `find` and the shared steps on that run's paths, as find makes its worktree"""
    a_run(repo, worktree=False)
    steps = ADAPTER.steps(given("rn:up", "/rn:up"), repo, RN)
    assert shown(steps) == relative([FIND, *shared(repo)], repo)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_pick_up_among_several_runs_takes_the_newest_by_its_last_commit(repo: str):
    """Given runs 20261120-new and 20261101-old with work left, 20261101-old's last commit the
    newer, and 20261121-done with each deliverable done, newest of all
    When the adapter gives the steps of a pick-up
    Then the shared steps are on 20261101-old"""
    a_run(repo, "20261120-new", when="2026-11-10T09:00:00")
    a_run(repo, "20261101-old", when="2026-11-15T09:00:00")
    a_run(repo, "20261121-done", done_tree("20261121-done"), "2026-11-21T09:00:00")
    steps = ADAPTER.steps(given("rn:up", "/rn:up"), repo, RN)
    assert shown(steps) == relative([FIND, *shared(repo, "20261101-old")], repo)


@pytest.mark.supports(
    "test_each_event_in_a_run_loads_the_orchestrator_and_holds_its_turn_to_its_steps"
)
def test_a_signoff_records_it_then_keeps_the_shared_steps(repo: str):
    """Given a repository with one run, and a turn of rn:ty whose prompt is /rn:ty
    When the adapter gives the turn's steps
    Then they are `record` and the shared steps"""
    a_run(repo)
    steps = ADAPTER.steps(given("rn:ty", "/rn:ty"), repo, RN)
    assert shown(steps) == relative([step("record", BLOCKED), *shared(repo)], repo)


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
def test_a_pause_stops_the_roles_then_pauses_with_no_shared_step(repo: str):
    """Given a repository with one run, and a turn of rn:dn whose prompt is /rn:dn
    When the adapter gives the turn's steps
    Then they are `stop` and `pause` alone"""
    a_run(repo)
    steps = ADAPTER.steps(given("rn:dn", "/rn:dn"), repo, RN)
    assert shown(steps) == [
        step("stop", BLOCKED),
        step("pause"),
    ]


@pytest.mark.supports(
    "test_a_command_called_by_the_skill_tool_in_a_standing_run_takes_the_typed_commands_steps"
)
def test_a_command_called_by_the_skill_tool_takes_the_steps_of_the_command_typed(repo: str):
    """Given a repository with one run, and a turn of the user's `Go on.` in which an AI called
    rn:dn, or rn:up, by the Skill tool
    When the adapter gives the turn's steps
    Then they are those of the typed command: `stop` and `pause`, or `find` and the shared steps"""
    a_run(repo)
    paused = ADAPTER.steps(given("rn:dn", "Go on.", command="rn:dn"), repo, RN)
    assert shown(paused) == [step("stop", BLOCKED), step("pause")]
    found = ADAPTER.steps(given("rn:up", "Go on.", command="rn:up"), repo, RN)
    assert shown(found) == relative([FIND, *shared(repo)], repo)


@pytest.mark.supports("test_an_orchestrators_turn_ended_before_its_review_is_stopped")
@pytest.mark.parametrize(
    ("role", "prompt"),
    [
        ("rn:gm", "/rn:gm the guide first"),
        ("rn:gm", "/rn:gm"),
        ("rn:up", "with each invoice"),
        ("rn:ty", "What's left?"),
        ("rn:up", ENDED),
        ("rn:up", "/rn:onx"),
    ],
    ids=[
        "send-back",
        "send-back-alone",
        "answer",
        "other-prompt",
        "role-end",
        "near-command",
    ],
)
def test_each_other_event_takes_it_then_keeps_the_shared_steps(repo: str, role: str, prompt: str):
    """Given a repository with one run, and a turn of a send-back, an answer, another prompt, a
    role's end as Claude Code's task-notification, or a prompt that nearly names a command
    When the adapter gives the turn's steps
    Then they are `take` and the shared steps, on that run"""
    a_run(repo)
    assert shown(ADAPTER.steps(given(role, prompt), repo, RN)) == relative(
        [TAKE, *shared(repo)], repo
    )


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
@pytest.mark.parametrize("before", ["no-run", "only-done", "no-repository"])
@pytest.mark.parametrize(
    ("role", "prompt"),
    [("rn:up", "/rn:up"), ("rn:ty", "/rn:ty"), ("rn:dn", "/rn:dn"), ("rn:up", "yes")],
    ids=["pick-up", "sign-off", "pause", "answer"],
)
def test_a_turn_other_than_a_new_request_with_no_run_takes_find_alone(
    repo: str, cwd: str, role: str, prompt: str, before: str
):
    """Given a repository with no run, or only a run whose deliverables are each done, or a folder
    that isn't a git repository, holding a run's files
    When the adapter gives the steps of a turn other than the hearing and a new request
    Then they are `find` alone, with no rule that ends it on blocked, as it's the turn's last"""
    top = cwd if before == "no-repository" else repo
    if before == "only-done":
        a_run(repo, "20261121-done", done_tree("20261121-done"))
    if before == "no-repository":
        paused_run(cwd)
    steps = ADAPTER.steps(given(role, prompt), top, RN)
    assert shown(steps) == [step("find")]


TURNS = {
    "new request": ("rn:on", WORDS, "rn:on", HEARD),
    "pick-up": ("rn:up", "/rn:up", "rn:up", []),
    "sign-off": ("rn:ty", "/rn:ty", "rn:up", []),
    "pause": ("rn:dn", "/rn:dn", "rn:up", []),
    "send-back": ("rn:gm", "/rn:gm the guide first", "rn:up", []),
    "answer": ("rn:up", "yes", "rn:up", []),
    "role-end": ("rn:up", ENDED, "rn:up", []),
}


@pytest.mark.supports("test_a_new_request_with_no_origin_ends_its_turn_on_blocked")
@pytest.mark.parametrize("event", list(TURNS))
def test_each_step_of_a_turn_but_its_last_ends_on_blocked(repo: str, event: str):
    """Given a repository with one run whose plan is signed off, and a turn of each event
    When the adapter gives the turn's steps
    Then each step but the last holds the rule that ends the turn on blocked, and the last holds
    no rule of results, as Lane judges it at each end with every step done"""
    a_run(repo)
    role, prompt, skill, turns = TURNS[event]
    each = ADAPTER.steps(given(role, prompt, skill=skill, turns=turns), repo, RN)["steps"]
    assert [BLOCKED in s["rules"] for s in each] == [True] * (len(each) - 1) + [False]
    assert not [r for r in each[-1]["rules"] if r["type"] == "result"]


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
@pytest.mark.parametrize("role", ["log:up", "rn:upx", "rn:evaluate", "rnx:generator", "rn:"])
def test_a_role_that_isnt_rns_is_refused(cwd: str, role: str):
    """Given a role of another plugin, or one that nearly matches one of rn's
    When the adapter gives its steps
    Then it raises Wrong, naming the role"""
    paused_run(cwd)
    with pytest.raises(Wrong, match=role):
        ADAPTER.steps(given(role, "Make it."), cwd, RN)


# The generator's start, by its Cut.


def trial_of(path: str, stage: str = "content", number: int = 1) -> str:
    """The people's folder of the deliverable's Round of the stage and number, as
    repository.trial.folder names it."""
    return os.path.join(
        tempfile.gettempdir(), f"rn-trial-{NAME}-{quote(path, safe='')}-{stage}-{number}"
    )


def generator_cut(
    cwd: str,
    node: Mapping[str, Any],
    inputs: Sequence[str] = (),
    practice: str = os.path.join(rn_files.PRACTICES, "light"),
    stage: str = "content",
) -> tuple[str, str]:
    """Writes the generator's Cut of the deliverable's Round 1 of the stage in the run, each input
    given from the worktree's top and named from cwd; gives the Cut's path from cwd and the Round's
    folder, absolute."""
    folder = paused_run(cwd)
    round_ = rn_files.round_of(folder, node["path"], stage, 1)
    worktree = rn_files.worktree_of(cwd, NAME)
    cut = {
        "goal": rn_files.GOAL,
        "language": rn_files.DELIVERABLES_LANGUAGE,
        "deliverable": dict(node),
        "worktree": os.path.relpath(worktree, cwd),
        "inputs": [os.path.relpath(os.path.join(worktree, each), cwd) for each in inputs],
        "best_practice": practice,
        "stage": stage,
        "number": 1,
        "round": os.path.relpath(round_, cwd),
        "trial": trial_of(node["path"], stage),
        "findings": None,
        "last_good": None,
    }
    path = os.path.join(round_, "generator-cut.json")
    rn_files.write_json(path, cut)
    return os.path.relpath(path, cwd), round_


def generator_steps(
    cwd: str, cut: str, kind: str, reads: Sequence[str]
) -> list[tuple[str, list[str]]]:
    """The generator's steps for the Cut, its best practice of the kind, the files it reads whole
    beside the Cut, each absolute, as `relative` then gives them."""
    return [
        step("read", {"type": "reads_whole", "paths": [os.path.join(cwd, cut), *reads]}),
        step(
            "decide",
            {"type": "checklist", "items": rn_files.items_at(kind, "decide")},
            {"type": "result", "ends": ["point"]},
        ),
        step("make", {"type": "checklist", "items": rn_files.items_at(kind, "make")}),
        step("try"),
        step(
            "check",
            {"type": "check", "check": f"python3 {RN}/scripts/check.py generator {cut}"},
            {"type": "result", "results": ["made"], "ends": ["point"]},
        ),
    ]


def in_worktree(cwd: str, *paths: str) -> list[str]:
    """Each path of the run's worktree, absolute, its folder made and each file written."""
    worktree = rn_files.worktree_of(cwd, NAME)
    found = []
    for each in paths:
        whole = os.path.join(worktree, each)
        if each.endswith("/"):
            os.makedirs(whole, exist_ok=True)
            found.append(whole)
        else:
            os.makedirs(os.path.dirname(whole), exist_ok=True)
            with open(whole, "w", encoding="utf-8") as f:
                f.write("x\n")
            found.append(whole)
    return found


LIGHT_MD = os.path.join(rn_files.PRACTICES, "light", "best-practice.md")


@pytest.mark.supports("test_a_generator_marking_make_before_decide_is_stopped")
def test_a_generators_start_with_one_input_takes_its_five_steps(cwd: str):
    """Given the command's generator Cut, of the kind light, whose one input is invoicer's lines
    When the adapter gives the start's steps
    Then they are read, decide, make, try, and check, each in order: read reading whole the Cut,
    light's best-practice.md, and the lines; decide with light's decide items, ending on point;
    make with its make items; try; and check with check.py generator on the Cut, made or, ending,
    point"""
    (lines,) = in_worktree(cwd, "invoicer/lines.py")
    node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"])
    cut, _ = generator_cut(cwd, node, ["invoicer/lines.py"])
    expected = generator_steps(cwd, cut, "light", [LIGHT_MD, lines])
    assert shown(ADAPTER.steps(given("rn:generator", cut), cwd, RN)) == relative(expected, cwd)


@pytest.mark.supports("test_a_generators_read_marked_before_its_cut_is_read_whole_is_stopped")
def test_a_generators_start_with_no_input_reads_the_cut_and_its_best_practice_alone(cwd: str):
    """Given a generator's Cut with no input
    When the adapter gives the start's steps
    Then read reads whole the Cut and the best practice's best-practice.md alone"""
    node = rn_files.open_node("The changes of 1.5.0", "CHANGELOG.md", "light")
    cut, _ = generator_cut(cwd, node)
    expected = generator_steps(cwd, cut, "light", [LIGHT_MD])
    assert shown(ADAPTER.steps(given("rn:generator", cut), cwd, RN)) == relative(expected, cwd)


@pytest.mark.supports("test_a_generators_read_marked_before_its_cut_is_read_whole_is_stopped")
def test_a_generators_inputs_read_whole_are_its_files_and_never_a_folder(cwd: str):
    """Given a generator's Cut whose inputs are two files and a folder
    When the adapter gives the start's steps
    Then read reads whole the Cut, the best practice, and each of the two files, and not the
    folder"""
    lines, tax = in_worktree(cwd, "invoicer/lines.py", "invoicer/tax.py")
    in_worktree(cwd, "docs/")
    inputs = ["invoicer/lines.py", "invoicer/tax.py", "docs/"]
    node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", inputs)
    cut, _ = generator_cut(cwd, node, inputs)
    expected = generator_steps(cwd, cut, "light", [LIGHT_MD, lines, tax])
    assert shown(ADAPTER.steps(given("rn:generator", cut), cwd, RN)) == relative(expected, cwd)


@pytest.mark.supports("test_a_generators_read_marked_before_its_cut_is_read_whole_is_stopped")
def test_a_generators_read_reads_whole_each_file_of_its_deliverable_that_stands(cwd: str):
    """Given a generator's Cut of a guide that the repository holds before the run, with its
    pictures' folder beside it
    When the adapter gives the start's steps
    Then read reads whole the Cut, the best practice, and the guide, and not the folder"""
    (guide,) = in_worktree(cwd, "docs/guide.md")
    in_worktree(cwd, "docs/images/")
    node = rn_files.open_node("The guide", "docs/guide.md", "light")
    node["more_paths"] = ["docs/images/"]
    cut, _ = generator_cut(cwd, node)
    expected = generator_steps(cwd, cut, "light", [LIGHT_MD, guide])
    assert shown(ADAPTER.steps(given("rn:generator", cut), cwd, RN)) == relative(expected, cwd)


@pytest.mark.supports("test_the_generators_make_is_held_to_its_best_practices_make_items")
def test_a_refactor_rounds_items_are_those_of_the_refactor_best_practice(cwd: str):
    """Given a generator's Cut of the guide, of the kind readme, in Round refactor-1, whose best
    practice is refactor-doc
    When the adapter gives the start's steps
    Then decide and make take refactor-doc's items, and read reads its best-practice.md"""
    node = rn_files.open_node(rn_files.GUIDE_NAME, GUIDE, "readme", good=True)
    practice = os.path.join(rn_files.PRACTICES, "refactor-doc")
    cut, _ = generator_cut(cwd, node, practice=practice, stage="refactor")
    md = os.path.join(practice, "best-practice.md")
    expected = generator_steps(cwd, cut, "refactor-doc", [md])
    assert shown(ADAPTER.steps(given("rn:generator", cut), cwd, RN)) == relative(expected, cwd)


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_a_runs_own_best_practice_gives_its_own_items(cwd: str):
    """Given a run's own best practice of the kind light in its worktree, holding only the first
    condition of rn's, and a generator's Cut that names it
    When the adapter gives the start's steps
    Then decide and make take that condition's items alone, and read reads its own
    best-practice.md"""
    own = os.path.join(rn_files.worktree_of(cwd, NAME), ".rn", "best-practices", "light")
    kept = rn_files.practice("light")
    kept["goal"]["critical_success_factors"][0]["necessary_conditions"] = kept["goal"][
        "critical_success_factors"
    ][0]["necessary_conditions"][:1]
    kept["goal"]["critical_success_factors"] = kept["goal"]["critical_success_factors"][:1]
    rn_files.write_json(os.path.join(own, "best-practice.json"), kept)
    with open(os.path.join(own, "best-practice.md"), "w", encoding="utf-8") as f:
        f.write("# light\n")
    node = rn_files.open_node("The changes of 1.5.0", "CHANGELOG.md", "light")
    cut, _ = generator_cut(cwd, node, practice=os.path.relpath(own, cwd))
    steps = shown(ADAPTER.steps(given("rn:generator", cut), cwd, RN))
    items = rn_files.practice("light")["goal"]["critical_success_factors"][0]
    first = items["necessary_conditions"][0]
    decide = [f"N1.{n}" for n, i in enumerate(first["items"], 1) if i["at"] == "decide"]
    make = [f"N1.{n}" for n, i in enumerate(first["items"], 1) if i["at"] == "make"]
    expected = generator_steps(cwd, cut, "light", [os.path.join(own, "best-practice.md")])
    expected[1] = step(
        "decide", {"type": "checklist", "items": decide}, {"type": "result", "ends": ["point"]}
    )
    expected[2] = step("make", {"type": "checklist", "items": make})
    assert steps == relative(expected, cwd)


@pytest.mark.supports("test_a_generators_read_marked_before_its_cut_is_read_whole_is_stopped")
@pytest.mark.parametrize("form", ["missing", "not JSON", "no round", "prose"])
def test_a_generators_prompt_that_names_no_cut_in_its_form_is_refused(cwd: str, form: str):
    """Given a generator's prompt naming no file, a file that isn't JSON, a Cut without its round,
    or a sentence in place of a path
    When the adapter gives the start's steps
    Then it raises Wrong"""
    node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light")
    cut, _ = generator_cut(cwd, node)
    whole = os.path.join(cwd, cut)
    if form == "missing":
        os.remove(whole)
    elif form == "not JSON":
        with open(whole, "w", encoding="utf-8") as f:
            f.write("{goal: the invoice\n")
    elif form == "no round":
        kept = rn_files.read_json(whole)
        del kept["round"]
        rn_files.write_json(whole, kept)
    else:
        cut = "Make the command that prints an invoice."
    with pytest.raises(Wrong):
        ADAPTER.steps(given("rn:generator", cut), cwd, RN)


# The evaluator's start, by its Cut.


def evaluator_cut(cwd: str, number: int = 1) -> tuple[str, str, str]:
    """Writes the evaluator's Cut of the command's content Round of the number; gives the Cut's
    path from cwd, the Round's folder, and the people's folder, each absolute but the first."""
    folder = paused_run(cwd)
    round_ = rn_files.round_of(folder, COMMAND, "content", number)
    trial = trial_of(COMMAND, "content", number)
    cut = {
        "goal": rn_files.GOAL,
        "deliverable": {"name": rn_files.COMMAND_NAME, "path": COMMAND},
        "judges_by": rn_files.judged_by("light"),
        "worktree": os.path.relpath(rn_files.worktree_of(cwd, NAME), cwd),
        "round": os.path.relpath(round_, cwd),
        "trial": trial,
    }
    path = os.path.join(round_, "evaluator-cut.json")
    rn_files.write_json(path, cut)
    return os.path.relpath(path, cwd), round_, trial


def evaluator_steps(
    cwd: str, cut: str, round_: str, trial: str, others: Sequence[str] = ()
) -> list[tuple[str, list[str]]]:
    """The evaluator's steps for the Cut, its Round, the people's folder, and each other Round's
    folder, each absolute."""
    tree = os.path.join(rn_files.folder_of(cwd, NAME), "design-tree.json")
    never = {
        "type": "reads_none",
        "paths": [
            tree,
            os.path.join(round_, "generator-cut.json"),
            os.path.join(round_, "generator.json"),
            *[each + "/" for each in others],
        ],
    }
    return [
        step(
            "read",
            never,
            {"type": "reads_whole", "paths": [os.path.join(cwd, cut)]},
            writes(),
        ),
        step("start", never, writes()),
        step("try", never, writes(trial + "/")),
        step(
            "judge",
            never,
            {"type": "checklist", "items": rn_files.conditions("light")},
            writes(round_ + "/"),
            {"type": "check", "check": f"python3 {RN}/scripts/check.py evaluator {cut}"},
            {"type": "result", "results": ["judged"]},
        ),
    ]


@pytest.mark.supports("test_the_evaluator_reading_the_design_tree_is_stopped")
def test_an_evaluators_start_with_no_other_round_takes_its_four_steps(cwd: str):
    """Given the command's evaluator Cut in Round content-1, the run's only Round
    When the adapter gives the start's steps
    Then they are read, start, try, and judge, each in order, each never reading the design tree,
    the generator's Cut, or its result: read reading whole the Cut and writing nothing; start
    writing nothing; try writing only the people's folder; judge with light's conditions as
    its checklist, writing only the Round's folder, with check.py evaluator and judged"""
    cut, round_, trial = evaluator_cut(cwd)
    expected = evaluator_steps(cwd, cut, round_, trial)
    assert shown(ADAPTER.steps(given("rn:evaluator", cut), cwd, RN)) == relative(expected, cwd)


@pytest.mark.supports("test_the_evaluator_reading_the_generators_result_is_stopped")
def test_an_evaluators_steps_never_read_another_round(cwd: str):
    """Given the command's evaluator Cut in Round content-2, beside the command's content-1 and
    the guide's content-1
    When the adapter gives the start's steps
    Then each step never reads either other Round's folder, beside the design tree and the
    generator's Cut and result"""
    folder = paused_run(cwd)
    others = [
        rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.made()}),
        rn_files.a_round(folder, GUIDE, "content", 1),
    ]
    cut, round_, trial = evaluator_cut(cwd, 2)
    expected = evaluator_steps(cwd, cut, round_, trial, others)
    assert shown(ADAPTER.steps(given("rn:evaluator", cut), cwd, RN)) == relative(expected, cwd)


@pytest.mark.supports("test_the_evaluators_try_writes_only_in_the_peoples_folder")
@pytest.mark.parametrize("form", ["missing", "generator's Cut", "prose"])
def test_an_evaluators_prompt_that_names_no_cut_in_its_form_is_refused(cwd: str, form: str):
    """Given an evaluator's prompt naming no file, a generator's Cut, or a sentence
    When the adapter gives the start's steps
    Then it raises Wrong"""
    cut, _, _ = evaluator_cut(cwd)
    if form == "missing":
        os.remove(os.path.join(cwd, cut))
    elif form == "generator's Cut":
        node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light")
        cut, _ = generator_cut(cwd, node)
    else:
        cut = "Try the command as the accounting team would."
    with pytest.raises(Wrong):
        ADAPTER.steps(given("rn:evaluator", cut), cwd, RN)


# main, as Lane runs it.


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_main_gives_0_with_the_steps_as_one_line_of_json(repo: str):
    """Given Lane's input of a new request's turn as JSON on standard input
    When main runs
    Then it gives 0, the steps that `steps` gives as one line of JSON, and nothing on stderr"""
    text = json.dumps(given("rn:on", WORDS, skill="rn:on", turns=HEARD))
    code, out, err = ADAPTER.main(text, repo, RN)
    assert (code, err) == (0, "")
    assert out.endswith("\n") and out.count("\n") == 1
    assert json.loads(out) == ADAPTER.steps(json.loads(text), repo, RN)


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
@pytest.mark.parametrize(
    "stdin",
    [
        "",
        "{run",
        "[]",
        '{"run": {"skill": "rn:up", "words": ""}, "role": "rn:up", "prompt": "", "turns": []}',
    ],
)
def test_main_gives_1_where_its_input_isnt_lanes_json(cwd: str, stdin: str):
    """Given standard input that's empty, not JSON, JSON of another form, or a turn with no
    `command`
    When main runs
    Then it gives 1, nothing on stdout, and `rules.py: ` with what's wrong on stderr"""
    code, out, err = ADAPTER.main(stdin, cwd, RN)
    assert (code, out) == (1, "")
    assert err.startswith("rules.py: ")


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
def test_main_gives_1_where_steps_refuses_the_start(cwd: str):
    """Given a start of log:up, a role of another plugin
    When main runs
    Then it gives 1, nothing on stdout, and `rules.py: ` with the refusal naming the role on
    stderr"""
    code, out, err = ADAPTER.main(json.dumps(given("log:up", "Make it.")), cwd, RN)
    assert (code, out) == (1, "")
    assert err.startswith("rules.py: ") and "log:up" in err


# Each path as Lane compares it.


def rules_of(steps: Mapping[str, Any], name: str, kind: str) -> list[str]:
    """The paths of each rule of the kind at the step of the name."""
    return [
        p
        for each in steps["steps"]
        if each["name"] == name
        for rule in each["rules"]
        if rule["type"] == kind
        for p in rule.get("paths", [])
    ]


@pytest.mark.supports("test_a_generators_read_marked_before_its_cut_is_read_whole_is_stopped")
def test_a_best_practice_outside_the_repository_comes_as_a_path_up_from_it(cwd: str):
    """Given a generator's Cut whose best practice is rn's light, outside the repository
    When the adapter gives the start's steps
    Then read reads whole light's best-practice.md by a path that starts `../`, which leads from
    the repository's top to that file, and the Cut by its path inside the repository"""
    node = rn_files.open_node("The changes of 1.5.0", "CHANGELOG.md", "light")
    cut, _ = generator_cut(cwd, node)
    reads = rules_of(ADAPTER.steps(given("rn:generator", cut), cwd, RN), "read", "reads_whole")
    md = os.path.relpath(os.path.realpath(LIGHT_MD), cwd)
    assert md.startswith("../")
    assert sorted(reads) == sorted([cut, md])


@pytest.mark.supports("test_the_evaluators_try_writes_only_in_the_peoples_folder")
def test_the_peoples_folder_outside_the_repository_comes_as_a_path_up_from_it(cwd: str):
    """Given the command's evaluator Cut, whose people's folder lies in the system's temporary
    folder, outside the repository
    When the adapter gives the start's steps
    Then try writes only the people's folder, by a path that starts `../` and closes with `/`"""
    cut, _, trial = evaluator_cut(cwd)
    writes_ = rules_of(ADAPTER.steps(given("rn:evaluator", cut), cwd, RN), "try", "writes")
    expected = os.path.relpath(os.path.realpath(trial), cwd) + "/"
    assert expected.startswith("../")
    assert writes_ == [expected]


@pytest.mark.supports("test_a_generators_read_marked_before_its_cut_is_read_whole_is_stopped")
def test_a_cwd_reached_through_a_link_gives_the_same_paths_as_its_real_folder(cwd: str):
    """Given the command's generator Cut, and the repository reached through a symbolic link
    When the adapter gives the start's steps from the link and from the real folder
    Then both give the same steps, each path from the real folder, none through the link"""
    (lines,) = in_worktree(cwd, "invoicer/lines.py")
    node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"])
    cut, _ = generator_cut(cwd, node, ["invoicer/lines.py"])
    link = os.path.join(os.path.dirname(cwd), "link")
    os.symlink(cwd, link)
    expected = relative(generator_steps(cwd, cut, "light", [LIGHT_MD, lines]), cwd)
    assert shown(ADAPTER.steps(given("rn:generator", cut), link, RN)) == expected
    assert shown(ADAPTER.steps(given("rn:generator", cut), cwd, RN)) == expected
