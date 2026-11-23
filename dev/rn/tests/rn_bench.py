"""What rn's integration cases share: a bench that holds a copy of rn, the user's repository,
invoicer, with a remote `origin` of its own, and the double of gh first on the PATH; and the moves
of a run as rn's architecture draws them under Sequences, each a handoff between rn's scripts.

Each move runs rn's scripts as a role runs them, from the repository's top, each in a process of
its own, and feeds what one prints to the next, as the orchestrator and each role do. A double
stands in for each prompt's work, as rn's Test strategy says under Integration testing: it writes
the design tree, a deliverable's files, and each role's result where the prompt's result form
says. Each helper plays one move, and says nothing of how rn's parts carry it."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any, NamedTuple

import rn_files
from gh import gh_double
from repo_files import environment, git
from rn_files import GOAL, LANGUAGES, TOP, WORDS

RN = os.path.join(TOP, "plugins", "rn")


class Ran(NamedTuple):
    """What a script gave: its exit code, its stdout, and its stderr."""

    code: int
    out: str
    err: str


@dataclass(frozen=True)
class Bench:
    """A copy of rn, the user's repository and its remote, the folder of the double of gh's state,
    and the environment of each script."""

    rn: str
    repo: str
    origin: str
    gh: str
    env: dict[str, str]

    def at(self, path: str) -> str:
        """The path in the user's repository."""
        return os.path.join(self.repo, path)

    def name(self, words: str = WORDS) -> str:
        """The name of the run of the words started today, `<yyyymmdd>-<slug>`."""
        assert words == WORDS, "the bench names only the walkthrough's run"
        return f"{date.today():%Y%m%d}-{rn_files.NAMED}"

    @property
    def worktree(self) -> str:
        """The walkthrough's run's worktree."""
        return rn_files.worktree_of(self.repo, self.name())

    @property
    def folder(self) -> str:
        """The walkthrough's run's folder, absolute."""
        return rn_files.folder_of(self.repo, self.name())

    @property
    def run(self) -> str:
        """The walkthrough's run's folder from the repository's top, as scripts take `<run>`."""
        return os.path.relpath(self.folder, self.repo)

    @property
    def tree_path(self) -> str:
        """The walkthrough's run's design tree."""
        return os.path.join(self.folder, "design-tree.json")

    def tree(self) -> dict[str, Any]:
        """The walkthrough's run's design tree as it stands."""
        return rn_files.read_json(self.tree_path)

    def write_tree(self, design_tree: Mapping[str, Any]) -> None:
        """Writes the run's design tree whole, as the orchestrator edits it in its review."""
        with open(self.tree_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(design_tree, indent=1) + "\n")

    def script(self, name: str, *args: str) -> Ran:
        """Runs rn's script with the arguments from the repository's top, as a role runs it."""
        done = subprocess.run(
            [sys.executable, os.path.join(self.rn, "scripts", f"{name}.py"), *args],
            cwd=self.repo,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        return Ran(done.returncode, done.stdout, done.stderr)

    def ran(self, name: str, *args: str) -> str:
        """Runs rn's script, which must give 0, and gives what it printed."""
        done = self.script(name, *args)
        assert done.code == 0, done.err + done.out
        return done.out

    def branch_files(self, branch: str) -> list[str]:
        """Each file that the remote's branch holds."""
        return git(self.origin, "ls-tree", "-r", "--name-only", branch).split()

    def asked_gh(self) -> list[list[str]]:
        """Each gh command that the double of gh was asked."""
        return gh_double.state(self.gh)["asked"]


def bench(tmp: str) -> Bench:
    """A copy of rn, and invoicer's repository with a remote `origin` holding `main`, the double of
    gh first on the PATH."""
    rn = os.path.join(tmp, "plugins", "rn")
    shutil.copytree(RN, rn, ignore=shutil.ignore_patterns("__pycache__"))
    repo = rn_files.repository(os.path.join(tmp, "invoicer"))
    origin = rn_files.with_origin(repo, os.path.join(tmp, "origin.git"))
    gh = os.path.join(tmp, "gh")
    env = environment(tmp)
    # The case's time zone, so that each script takes the day that the case takes.
    env.update({name: os.environ[name] for name in ("TZ",) if name in os.environ})
    env["PATH"] = os.pathsep.join([gh_double.program(os.path.join(tmp, "bin"), gh), env["PATH"]])
    return Bench(rn, repo, origin, gh, env)


# The moves of the orchestrator.


def reviewed(
    b: Bench,
    design_tree: Mapping[str, Any] | None = None,
    ground: str = "The run's facts decide it.",
    moves: Sequence[Sequence[str]] = (),
) -> list[str]:
    """The orchestrator's moves after each event: it writes the design tree where one is given,
    runs `tree.py touched` and reads each node it prints, commits by `tree.py commit` with the
    ground, and runs each move given, a script's name and its arguments, such as
    `("repository", "put-up", ...)`. Gives what each move printed."""
    if design_tree is not None:
        b.write_tree(design_tree)
    for node in b.ran("tree", "touched", b.run).split():
        assert node.startswith("/"), node
    b.ran("tree", "commit", b.run, ground)
    return [b.ran(*each) for each in moves]


def requested(b: Bench) -> None:
    """The user asked for the walkthrough's words, and the orchestrator made the run's worktree and
    its design tree with the goal as put, by `repository.py new`, and committed it."""
    b.ran("repository", "new", rn_files.NAMED, GOAL, *LANGUAGES)
    reviewed(b, ground="The goal as put.")


def planned_tree(b: Bench, answered: bool) -> dict[str, Any]:
    """The design tree once the user confirms the goal: the goal by user, the plan's conditions
    good but N2's while the tax rate's point is open, the command and the guide, and the point
    about the tax rate an open decision of the command's N1, or the user's answer once given."""
    name = b.name()
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER if answered else None, "user")
    design_tree = rn_files.walkthrough_tree(name, plan_done=False, command_decisions={"N1": [tax]})
    held_good = rn_files.conditions("design-tree")
    if not answered:
        held_good.remove("N2")
    design_tree["deliverables"][0] = rn_files.plan(name, good=held_good)
    if not answered:
        design_tree["work"].insert(
            0, rn_files.work("decide", rn_files.COMMAND, "N1", rn_files.TAX_ABOUT)
        )
    return design_tree


def confirmed(b: Bench) -> None:
    """The user confirms the goal; the orchestrator writes the plan with the tax rate's point open,
    to put it to the user."""
    reviewed(b, planned_tree(b, answered=False), "The goal, as the user confirms it.")


def put_up_plan(b: Bench) -> str:
    """The user answers the point; the orchestrator writes the answer as its decision by user, and
    puts the plan up by `repository.py put-up`; gives what put-up printed."""
    plan = rn_files.plan_path(b.name())
    moves = [("repository", "put-up", b.run, plan)]
    return reviewed(b, planned_tree(b, answered=True), "The user's answer.", moves)[0].strip()


def to_plan_signoff(b: Bench) -> None:
    """A run whose plan waits for the user's sign-off."""
    requested(b)
    confirmed(b)
    put_up_plan(b)


def signed(b: Bench, moves: Sequence[Sequence[str]] = ()) -> list[str]:
    """The user types `/rn:ty`; the orchestrator records the sign-off by `tree.py signoff`, and
    commits it with the moves given; gives what the moves printed."""
    b.ran("tree", "signoff", b.run)
    return reviewed(b, ground="The user signs it off.", moves=moves)


def cut_move(b: Bench, role: str, deliverable: str) -> tuple[str, ...]:
    """The move that writes the role's Cut for the deliverable."""
    return ("tree", "cut", b.run, role, deliverable)


def signed_plan(b: Bench) -> str:
    """A run whose plan the user signed off, and whose command's Cut the orchestrator wrote for its
    generator, the one deliverable whose inputs are done; gives the Cut's path."""
    to_plan_signoff(b)
    return signed(b, [cut_move(b, "generator", rn_files.COMMAND)])[0].strip()


CHANGELOG = "CHANGELOG.md"


def apart_tree(b: Bench, decisions: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    """The plan once the user confirms the goal, each of its conditions good: the command and a
    changelog, each resting on none, each in the work, the command's N1 holding each decision
    given."""
    command = rn_files.open_node(rn_files.COMMAND_NAME, rn_files.COMMAND, "light")
    command["inputs"] = ["invoicer/lines.py"]
    command["necessary_conditions"][0]["decisions"] += [dict(each) for each in decisions]
    return rn_files.tree(
        [rn_files.plan(b.name()), command, rn_files.open_node("The changes", CHANGELOG, "light")],
        [rn_files.work("make", rn_files.COMMAND), rn_files.work("make", CHANGELOG)],
    )


def signed_apart(b: Bench, design_tree: Mapping[str, Any], made: Sequence[str]) -> list[str]:
    """A run whose plan given the orchestrator put up, and the user signed off, the orchestrator
    writing the generator's Cut of each deliverable given; gives each Cut's path."""
    requested(b)
    plan = rn_files.plan_path(b.name())
    reviewed(b, design_tree, "The plan.", [("repository", "put-up", b.run, plan)])
    moves = [cut_move(b, "generator", each) for each in made]
    return [each.strip() for each in signed(b, moves)]


def held(
    b: Bench, deliverable: str, good: Sequence[str], decisions: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """The run's design tree as it stands with the deliverable's conditions good as given, each
    other not good, and each decision given added to its condition."""
    design_tree = b.tree()
    for node in design_tree["deliverables"]:
        if node["path"] != deliverable:
            continue
        for each in node["necessary_conditions"]:
            each["good"] = each["id"] in good
            each["decisions"] += [dict(d) for d in (decisions or {}).get(each["id"], ())]
    return design_tree


def next_round(b: Bench, deliverable: str, good: Sequence[str], role: str = "generator") -> str:
    """At a role's end, the orchestrator holds good the conditions given, and writes the role's Cut
    for the deliverable; gives the Cut's path."""
    return reviewed(
        b, held(b, deliverable, good), "The Round's findings.", [cut_move(b, role, deliverable)]
    )[0].strip()


def put_up(b: Bench, deliverable: str, good: Sequence[str]) -> str:
    """At a role's end, the orchestrator holds good the conditions given, and puts the deliverable
    up by `repository.py put-up`; gives the URL it printed."""
    return reviewed(
        b,
        held(b, deliverable, good),
        "The Round's findings.",
        [("repository", "put-up", b.run, deliverable)],
    )[0].strip()


def sent_back(b: Bench, deliverable: str, good: list[str], words: str) -> str:
    """The user types /rn:gm with the words; the orchestrator writes them as a decision by user of
    the deliverable's N1, held not good, and writes the generator's Cut; gives the Cut's path."""
    send_back = {"N1": [rn_files.decision(words, words, "user")]}
    design_tree = held(b, deliverable, [each for each in good if each != "N1"], send_back)
    return reviewed(
        b, design_tree, "The user sends it back.", [cut_move(b, "generator", deliverable)]
    )[0].strip()


def checked_whole(b: Bench) -> list[str]:
    """Once each deliverable is done, the plain subagent of the final check runs
    `repository.py diff`, then `repository.py ci`; gives what each printed."""
    return [b.ran("repository", "diff", b.run), b.ran("repository", "ci", b.run)]


# The moves of the generator and the evaluator, the doubles of their prompts' work.


COMMAND_TEXT = (
    '"""Prints an invoice from a file of its lines."""\n'
    "import sys\n\n"
    "from invoicer.lines import parse_lines\n\n"
    "with open(sys.argv[1], encoding='utf-8') as f:\n"
    "    print(len(parse_lines(f.read().replace(',', ';'))))\n"
)
# The guide, a README that holds the readme template, as check.py holds a generator's Markdown to
# its kind's template: rn's own, which check.sh holds to it.
with open(os.path.join(RN, "README.md"), encoding="utf-8") as _readme:
    GUIDE_TEXT = _readme.read()

# The repository's tests as invoicer's developers run them, writing no file.
DEVELOPERS_TESTS = [sys.executable, "-B", "-c", "import invoicer.lines"]


def cut_of(b: Bench, cut_path: str) -> dict[str, Any]:
    """The Cut at the path from the repository's top, as a role reads it."""
    return rn_files.read_json(os.path.join(b.repo, cut_path))


def wrote(b: Bench, files: Mapping[str, str]) -> None:
    """Writes each file of a deliverable, by its path from the worktree's top."""
    for path, content in files.items():
        full = os.path.join(b.worktree, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)


def resulted(b: Bench, cut_path: str, role: str, result: Mapping[str, Any]) -> None:
    """Writes the role's result in the Round's folder that its Cut names."""
    path = os.path.join(b.repo, cut_of(b, cut_path)["round"], f"{role}.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(result))


def generated(
    b: Bench,
    cut_path: str,
    files: Mapping[str, str] | None = None,
    good: Sequence[str] | None = None,
) -> None:
    """The generator makes its deliverable from its Cut and ends with `made`: it writes each file
    given, by its path from the worktree's top, or else the deliverable's own text; in a refactor
    Round runs the repository's tests as its developers run them, in its folder of the people's
    starting state that `repository.py trial` makes; writes its result, good each condition given
    or else every one; and runs `check.py generator` and `repository.py checks` on its files, each
    of which must give 0."""
    given = cut_of(b, cut_path)
    node = given["deliverable"]
    text = COMMAND_TEXT if node["path"].endswith(".py") else GUIDE_TEXT
    made_files = dict(files or {node["path"]: text})
    wrote(b, made_files)
    # A generator names in `good` the conditions of its deliverable, as rn checks them, which in a
    # refactor Round are its content kind's, not those of the refactoring kind it makes by.
    seen = [each["id"] for each in node["necessary_conditions"]] if good is None else list(good)
    if given["stage"] == "refactor":
        trial = b.ran("repository", "trial", b.run, given["round"]).strip()
        tests = subprocess.run(DEVELOPERS_TESTS, cwd=trial, capture_output=True, check=False)
        assert tests.returncode == 0, tests.stderr
    first = next(iter(made_files.values())).splitlines()[0]
    result = rn_files.made([(each, [first]) for each in seen], list(made_files))
    resulted(b, cut_path, "generator", result)
    b.ran("check", "generator", cut_path)
    b.ran("repository", "checks", b.run, *made_files)


def pointed(b: Bench, cut_path: str, words: str = rn_files.TAX_POINT) -> None:
    """The generator finds a point that only the user can settle, writes its result `point`, and
    runs `check.py generator`, which must give 0."""
    resulted(b, cut_path, "generator", rn_files.point(words))
    b.ran("check", "generator", cut_path)


def trial_made(b: Bench, cut_path: str) -> str:
    """The evaluator makes its folder of the people's starting state by `repository.py trial`;
    gives the folder it printed."""
    return b.ran("repository", "trial", b.run, cut_of(b, cut_path)["round"]).strip()


def evaluated(b: Bench, cut_path: str, more: Mapping[str, str] | None = None) -> None:
    """The evaluator tries the deliverable in the people's folder that `repository.py trial` makes,
    writes its answers, each condition good but those of `more`, with what would make each good,
    and runs `check.py evaluator`, which must give 0."""
    given = cut_of(b, cut_path)
    trial = trial_made(b, cut_path)
    with open(os.path.join(trial, "lines.csv"), "w", encoding="utf-8") as f:
        f.write("Hosting;40.00;1\nSupport hours;120.00;1\n")
    ids = [
        each["id"]
        for factor in given["judges_by"]["critical_success_factors"]
        for each in factor["necessary_conditions"]
    ]
    with open(os.path.join(b.worktree, given["deliverable"]["path"]), encoding="utf-8") as f:
        first = f.read().splitlines()[0]
    left = dict(more or {})
    result = rn_files.judged(
        [(each, [first]) for each in ids if each not in left], list(left.items())
    )
    resulted(b, cut_path, "evaluator", result)
    b.ran("check", "evaluator", cut_path)


# The runs past the plan's sign-off, each a handoff after another.


def made_command(b: Bench) -> None:
    """A run whose command's generator made its first Round."""
    generated(b, signed_plan(b))


def evaluator_cut(b: Bench) -> str:
    """A run whose command's generator made its first Round, and whose orchestrator wrote the
    evaluator's Cut; gives its path."""
    made_command(b)
    moves = [cut_move(b, "evaluator", rn_files.COMMAND)]
    return reviewed(b, ground="The generator made its Round.", moves=moves)[0].strip()


def judged_command(b: Bench, more: Mapping[str, str] | None = None) -> None:
    """A run whose command's evaluator judged its first Round, each condition good but those of
    `more`."""
    evaluated(b, evaluator_cut(b), more)


def command_signed(b: Bench) -> str:
    """A run whose command was judged good in its first Round, put up, and signed off, and whose
    guide's Cut the orchestrator then wrote for its generator; gives its path."""
    judged_command(b)
    put_up(b, rn_files.COMMAND, rn_files.conditions("light"))
    return signed(b, [cut_move(b, "generator", rn_files.GUIDE)])[0].strip()


def refactor_made(b: Bench) -> None:
    """A run whose guide the evaluator judged good in Round content-1, and a new generator
    refactored in Round refactor-2."""
    generated(b, command_signed(b))
    evaluated(b, next_round(b, rn_files.GUIDE, [], "evaluator"))
    generated(b, next_round(b, rn_files.GUIDE, rn_files.conditions("readme")))


def refactored(b: Bench) -> None:
    """A run whose guide `refactor_made` gives, which the orchestrator then put up for the user's
    sign-off."""
    refactor_made(b)
    put_up(b, rn_files.GUIDE, rn_files.conditions("readme"))


def short_twice(b: Bench) -> None:
    """A run whose command's N1 the evaluator found short in Rounds content-1 and content-2, the
    orchestrator holding N2 and N3 good."""
    more = {"N1": "The accountant prints an invoice with a comma in a line."}
    judged_command(b, more)
    generated(b, next_round(b, rn_files.COMMAND, ["N2", "N3"]))
    evaluated(b, next_round(b, rn_files.COMMAND, ["N2", "N3"], "evaluator"), more)
