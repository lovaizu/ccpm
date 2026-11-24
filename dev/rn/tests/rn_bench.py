"""What rn's integration cases share: a bench that holds a copy of rn, the user's repository,
invoicer, with a remote `origin` of its own, and the double of gh first on the PATH; and the moves
of a run as rn's architecture draws them under Sequences, each a handoff between rn's scripts.

Each move runs rn's scripts as a role runs them, from the repository's top, each in a process of its
own, and feeds what one prints to the next, as the orchestrator and each role do. A double stands in
for each prompt's work, as rn's Test strategy says under Integration testing: the pruner's writes
the design tree, rewrites the nodes that `tree.py touched` lists, and checks it by `tree.py check`,
the generator's writes a deliverable's files, the fixer's mends them or names a decision, and each
role's writes its result where the prompt's result form says. Each helper plays one move, and
says nothing of how rn's parts carry it."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

import rn_files
from gh import gh_double
from repo_files import environment, git
from repository.host import Ran
from rn_files import LANGUAGES, TOP, WORDS

RN = os.path.join(TOP, "plugins", "rn")


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
        """Writes the run's design tree whole, as the pruner writes it from the fact it weighs."""
        with open(self.tree_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(design_tree, indent=1) + "\n")

    def script(self, name: str, *args: str, given: str = "", cwd: str | None = None) -> Ran:
        """Runs rn's script with the arguments from the repository's top, or from the folder
        given, as a role runs it, or as Claude Code runs a hook, with what it's given on stdin."""
        done = subprocess.run(
            [sys.executable, os.path.join(self.rn, "scripts", f"{name}.py"), *args],
            cwd=cwd or self.repo,
            env=self.env,
            input=given,
            capture_output=True,
            text=True,
            check=False,
        )
        return Ran(done.returncode, done.stdout, done.stderr)

    def ran(self, name: str, *args: str) -> str:
        """Runs rn's script, which must give 0, and gives what it printed."""
        return self.ran_in(self.repo, name, *args)

    def ran_in(self, cwd: str, name: str, *args: str) -> str:
        """Runs rn's script from the folder, as a role that starts there runs it, which must give
        0, and gives what it printed."""
        done = self.script(name, *args, cwd=cwd)
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


# The moves of the orchestrator, and of the pruner that it starts for each unit.


def pruned(
    b: Bench, design_tree: Mapping[str, Any], rewritten: Mapping[str, Any] | None = None
) -> list[str]:
    """A new pruner weighs a unit, given the run's folder by its absolute path, from a folder of
    its own, the run's worktree: it writes the design tree given; runs `tree.py touched`, which
    lists each node that its change touches; rewrites itself each node of `rewritten`, by its
    pointer, which must be among those listed, to the value given, as the change made it false;
    and checks its write by `tree.py check`, which must give 0, before it ends. Gives the nodes
    that `tree.py touched` listed."""
    b.write_tree(design_tree)
    listed = b.ran_in(b.worktree, "tree", "touched", b.folder).split()
    if rewritten:
        mended = b.tree()
        for pointer, value in rewritten.items():
            assert pointer in listed, f"{pointer} is a node that the change touches"
            _set_at(mended, pointer, value)
        b.write_tree(mended)
    b.ran_in(b.worktree, "tree", "check", b.folder)
    return listed


def _set_at(design_tree: dict[str, Any], pointer: str, value: Any) -> None:
    """Sets the node of the design tree at the JSON Pointer to the value."""
    *up, last = pointer[1:].split("/")
    node: Any = design_tree
    for name in up:
        node = node[int(name)] if isinstance(node, list) else node[name]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value


def reviewed(
    b: Bench,
    design_tree: Mapping[str, Any] | None = None,
    ground: str = "The run's facts decide it.",
    moves: Sequence[Sequence[str]] = (),
    rewritten: Mapping[str, Any] | None = None,
) -> list[str]:
    """The moves after each event: where a tree is given, a unit is settled, and one pruner weighs
    it as `pruned` does, rewriting each node of `rewritten`; then the orchestrator commits by
    `tree.py commit` with the ground, and runs each move given, a script's name and its arguments,
    such as `("repository", "put-up", ...)`. Gives what each move printed."""
    if design_tree is not None:
        pruned(b, design_tree, rewritten)
    b.ran("tree", "commit", b.run, ground)
    return [b.ran(*each) for each in moves]


def new_run(b: Bench) -> str:
    """The user asked for the walkthrough's words, and the orchestrator made the run's worktree and
    its design tree, its goal open, by `repository.py new`; gives what it printed."""
    return b.ran("repository", "new", rn_files.NAMED, *LANGUAGES)


# The steps of the walkthrough's way to the goal, as the user settles them in the hearing: they
# check the command, and the guide.
STEPS = (
    rn_files.step("what it does", [rn_files.COMMAND], True),
    rn_files.step("how it's used", [rn_files.GUIDE], True),
)


def heard_tree(b: Bench, answered: bool = True) -> dict[str, Any]:
    """The design tree as one pruner writes the hearing that the user settled: the goal by user,
    the plan named by it, open with each condition good, the command and the guide, the steps,
    and the tax rate's point a decision by user of the command's N1. Where `answered` is false,
    the pruner leaves the point open, for only the user can settle it, the plan's N2 not good, and
    the work deciding it first."""
    name = b.name()
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER if answered else None, "user")
    design_tree = rn_files.walkthrough_tree(name, plan_done=False, command_decisions={"N1": [tax]})
    design_tree["steps"] = [dict(each) for each in STEPS]
    if not answered:
        held_good = rn_files.conditions("design-tree")
        held_good.remove("N2")
        design_tree["deliverables"][0] = rn_files.plan(name, good=held_good)
        design_tree["work"].insert(
            0, rn_files.work("decide", rn_files.COMMAND, "N1", rn_files.TAX_ABOUT)
        )
    return design_tree


def heard(b: Bench, answered: bool = True) -> None:
    """The user asked for the walkthrough's words; the orchestrator made the run by `new_run`,
    held the hearing with the user until the way to the goal was settled, handed it to one pruner,
    which wrote `heard_tree`, and committed the tree."""
    new_run(b)
    reviewed(b, heard_tree(b, answered), "The way to the goal, as the user settled it.")


def signed(b: Bench, moves: Sequence[Sequence[str]] = ()) -> list[str]:
    """The orchestrator records a sign-off by `tree.py signoff`, the plan's once the hearing is
    written or a deliverable's at the user's `/rn:ty`, and commits it with the moves given; gives
    what the moves printed."""
    b.ran("tree", "signoff", b.run)
    return reviewed(b, ground="The user signs it off.", moves=moves)


def cut_move(b: Bench, role: str, deliverable: str) -> tuple[str, ...]:
    """The move that writes the role's Cut for the deliverable."""
    return ("tree", "cut", b.run, role, deliverable)


def signed_plan(b: Bench) -> str:
    """A run whose hearing one pruner wrote, whose plan's sign-off the orchestrator recorded, and
    whose command's Cut it wrote for its generator, the one deliverable whose inputs are done;
    gives the Cut's path."""
    heard(b)
    return signed(b, [cut_move(b, "generator", rn_files.COMMAND)])[0].strip()


CHANGELOG = "CHANGELOG.md"


def apart_tree(b: Bench, decisions: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    """The plan as one pruner writes the hearing, each of its conditions good: the command and a
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
    """A run whose hearing one pruner wrote as the plan given, whose plan's sign-off the
    orchestrator recorded, writing the generator's Cut of each deliverable given; gives each Cut's
    path."""
    new_run(b)
    reviewed(b, design_tree, "The way to the goal, as the user settled it.")
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
    """At a role's end, the pruner holds good the conditions given, and the orchestrator writes the
    role's Cut for the deliverable; gives the Cut's path."""
    return reviewed(
        b, held(b, deliverable, good), "The Round's findings.", [cut_move(b, role, deliverable)]
    )[0].strip()


def put_up(b: Bench, deliverable: str, good: Sequence[str]) -> str:
    """At a role's end, the pruner holds good the conditions given, and the orchestrator puts the
    deliverable up by `repository.py put-up`; gives the URL it printed."""
    return reviewed(
        b,
        held(b, deliverable, good),
        "The Round's findings.",
        [("repository", "put-up", b.run, deliverable)],
    )[0].strip()


def sent_back(b: Bench, deliverable: str, good: list[str], words: str) -> str:
    """The user types /rn:gm with the words; the pruner writes them as a decision by user of the
    deliverable's N1, held not good, and the orchestrator writes the generator's Cut; gives the
    Cut's path."""
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

# A figure of the guide's, as its template has it keep one of its own.
FIGURE_TEXT = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>\n'

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
    given, by its path from the worktree's top, or else the deliverable's own text and a figure at
    each of its more paths; in a refactor
    Round runs the repository's tests as its developers run them, in its folder of the people's
    starting state that `repository.py trial` makes; writes its result, good each condition given
    or else every one; and runs `check.py generator` and `repository.py checks` on its files, each
    of which must give 0."""
    given = cut_of(b, cut_path)
    node = given["deliverable"]
    text = COMMAND_TEXT if node["path"].endswith(".py") else GUIDE_TEXT
    made_files = dict(
        files or {node["path"]: text, **dict.fromkeys(node.get("more_paths", []), FIGURE_TEXT)}
    )
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


def refactoring_put_up(b: Bench) -> str:
    """The guide's refactoring Round ended its Rounds, and the orchestrator, starting no pruner,
    commits and puts the guide up for the user's sign-off by `repository.py put-up`; gives the URL
    that put-up printed."""
    moves = [("repository", "put-up", b.run, rn_files.GUIDE)]
    return reviewed(b, ground="The refactoring ends the guide's Rounds.", moves=moves)[0].strip()


def refactored(b: Bench) -> str:
    """A run whose guide `refactor_made` gives, then put up by `refactoring_put_up`; gives the URL
    that put-up printed."""
    refactor_made(b)
    return refactoring_put_up(b)


def short_twice(b: Bench) -> None:
    """A run whose command's N1 the evaluator found short in Rounds content-1 and content-2, the
    pruner holding N2 and N3 good."""
    more = {"N1": "The accountant prints an invoice with a comma in a line."}
    judged_command(b, more)
    generated(b, next_round(b, rn_files.COMMAND, ["N2", "N3"]))
    evaluated(b, next_round(b, rn_files.COMMAND, ["N2", "N3"], "evaluator"), more)


# The repository's own check before a push, and the moves of a Fix: the orchestrator's, and the
# fixer's, the double of its prompt's work.


# What the repository's check before a push prints where a line of the command ends in a space.
PUSH_REFUSAL = "lint: invoicer/__main__.py: a line ends in a space; strip it"
# The command with a line that ends in a space, which the check before a push refuses.
SPACED_TEXT = COMMAND_TEXT.replace("import sys\n", "import sys \n")


def push_checked(b: Bench) -> None:
    """The user's repository checks each push by a pre-push hook of git, which every worktree of
    it runs: it refuses the push, printing PUSH_REFUSAL, where a line of the command ends in a
    space."""
    hook = os.path.join(b.repo, ".git", "hooks", "pre-push")
    with open(hook, "w", encoding="utf-8") as f:
        f.write(
            "#!/bin/sh\n"
            "if grep -q ' $' invoicer/__main__.py; then\n"
            f"  echo '{PUSH_REFUSAL}' >&2\n"
            "  exit 1\n"
            "fi\n"
        )
    os.chmod(hook, 0o755)


def push_refused(b: Bench) -> Ran:
    """A run whose repository checks each push, as `push_checked` sets, and whose command's
    generator made it with a line that ends in a space, judged good in Round content-1; one pruner
    holds each condition good, and the orchestrator puts the command up by `repository.py put-up`;
    gives what put-up gave."""
    push_checked(b)
    generated(b, signed_plan(b), {rn_files.COMMAND: SPACED_TEXT})
    evaluated(b, next_round(b, rn_files.COMMAND, [], "evaluator"))
    reviewed(b, held(b, rn_files.COMMAND, rn_files.conditions("light")), "The Round's findings.")
    return b.script("repository", "put-up", b.run, rn_files.COMMAND)


def fix_written(b: Bench, deliverable: str, source: str, words: str) -> str:
    """The orchestrator judges, from the design tree, that the problem's mend keeps each decision
    of the deliverable, and writes the Fix by `tree.py fix` with the problem's words on stdin,
    which must give 0; gives the Fix's folder that it printed."""
    done = b.script("tree", "fix", b.run, deliverable, source, given=words)
    assert done.code == 0, done.err + done.out
    return done.out.strip()


def fixer_resulted(b: Bench, cut_path: str, result: Mapping[str, Any]) -> None:
    """Writes the fixer's result in the Fix's folder that its Cut names."""
    path = os.path.join(b.repo, cut_of(b, cut_path)["fix"], "fixer.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(result))


def fixed(b: Bench, cut_path: str, files: Mapping[str, str]) -> None:
    """The fixer mends its deliverable from its Cut within its decisions and ends with `fixed`: it
    writes each file given, by its path from the worktree's top; runs `repository.py checks` on
    them, which must give 0; runs the repository's tests as its developers run them, in the run's
    worktree; writes its result with the files; and runs `check.py fixer`, which must give 0."""
    wrote(b, files)
    b.ran("repository", "checks", b.run, *files)
    tests = subprocess.run(DEVELOPERS_TESTS, cwd=b.worktree, capture_output=True, check=False)
    assert tests.returncode == 0, tests.stderr
    fixer_resulted(b, cut_path, {"result": "fixed", "files": list(files)})
    b.ran("check", "fixer", cut_path)


def decision_named(b: Bench, cut_path: str, words: str) -> None:
    """The fixer finds that its mend would change a decision of its deliverable, mends nothing,
    ends with `decision`, naming it in the words given, and runs `check.py fixer`, which must
    give 0."""
    fixer_resulted(b, cut_path, {"result": "decision", "decision": words})
    b.ran("check", "fixer", cut_path)


# The hook, as Claude Code runs it before a tool call.


def tree_written(b: Bench, agent: str | None, tool: str = "Write") -> str:
    """The hook's input of a Write or Edit of the run's design tree, by its absolute path, by the
    agent, or by the main conversation where none is named, as Claude Code gives it."""
    if tool == "Edit":
        tool_input: dict[str, Any] = {
            "file_path": b.tree_path,
            "old_string": '"work": []',
            "new_string": '"work": [{"do": "make", "path": "invoicer/__main__.py"}]',
            "replace_all": False,
        }
    else:
        tool_input = {"file_path": b.tree_path, "content": json.dumps(b.tree(), indent=1) + "\n"}
    return rn_files.hook_input(b.repo, tool, tool_input, agent)


def bash_called(b: Bench, command: str, agent: str | None) -> str:
    """The hook's input of a Bash call of the command by the agent, or by the main conversation
    where none is named, made in the repository's top, as Claude Code gives it."""
    return rn_files.hook_input(b.repo, "Bash", {"command": command}, agent)


def denial(ran: Ran) -> str | None:
    """The reason of the hook's denial, where it denied the call; None where it let it pass,
    printing nothing; the hook gives 0 and nothing on stderr either way."""
    assert (ran.code, ran.err) == (0, ""), ran
    if ran.out == "":
        return None
    output = json.loads(ran.out)["hookSpecificOutput"]
    assert (output["hookEventName"], output["permissionDecision"]) == ("PreToolUse", "deny")
    return output["permissionDecisionReason"]
