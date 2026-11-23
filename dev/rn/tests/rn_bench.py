"""What rn's integration cases share: a bench that holds copies of rn and of Lane, the user's
repository, invoicer, with a remote `origin` of its own, the double of gh first on the PATH, and the
double of Claude Code to play the user, the orchestrator, and each subagent through; and the moves
of a run as rn's architecture draws them, each played through the double.

A double stands in for each prompt's work, as rn's Test strategy says under Integration testing:
the orchestrator's, the generator's, and the evaluator's, each keeping the steps that Lane gives it
and writing the files that its prompt's result form says. Each helper plays one move, and says
nothing of how rn's parts carry it."""

from __future__ import annotations

import json
import os
import shlex
import shutil
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import fresh_imports
import rn_files
from claude_code import FOREGROUND, Agent, Answer, Conversation
from gh import gh_double
from repo_files import environment, git
from rn_files import GOAL, LANGUAGES, TOP, WORDS

RN = os.path.join(TOP, "plugins", "rn")
LANE = os.path.join(TOP, "plugins", "lane")

# rn's own modules, by name, as plugins/rn/domain/ holds them, which each script that the double
# runs in the case's process imports afresh from the bench's copy.
RN_MODULES = ("fault", "practice", "tree", "rounds", "check", "repository", "template")


@contextmanager
def rn_of_the_bench() -> Iterator[None]:
    """Takes each of rn's modules out of the process while the block runs, so that each script
    that the double runs imports the bench's copy, as a new process of Python would."""
    with fresh_imports.without(RN_MODULES):
        yield


@dataclass(frozen=True)
class Bench:
    """Copies of rn and of Lane, the user's repository and its remote, the folder of the double of
    gh's state, the double's own folder, and the environment of each command."""

    rn: str
    lane: str
    repo: str
    origin: str
    gh: str
    temp: str
    env: dict[str, str] = field(default_factory=dict)

    def converse(self) -> Conversation:
        """A new conversation at the repository's top, with rn and Lane loaded."""
        return Conversation(self.repo, [self.rn, self.lane], self.env, self.temp)

    def at(self, path: str) -> str:
        """The path in the user's repository."""
        return os.path.join(self.repo, path)

    def name(self, words: str = WORDS) -> str:
        """The name of the run of the words started today, `<yyyymmdd>-<goal>`."""
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

    def script(self, name: str, *args: str) -> str:
        """The command that runs rn's script with the arguments, as rn's steps name it."""
        return " ".join(
            ["python3", shlex.quote(f"{self.rn}/scripts/{name}.py"), *map(shlex.quote, args)]
        )

    def branch_files(self, branch: str) -> list[str]:
        """Each file that the remote's branch holds."""
        return git(self.origin, "ls-tree", "-r", "--name-only", branch).split()

    def asked_gh(self) -> list[list[str]]:
        """Each gh command that the double of gh was asked."""
        return gh_double.state(self.gh)["asked"]


def bench(tmp: str) -> Bench:
    """Copies of rn and of Lane, and invoicer's repository with a remote `origin` holding `main`,
    the double of gh first on the PATH."""
    rn = os.path.join(tmp, "plugins", "rn")
    lane = os.path.join(tmp, "plugins", "lane")
    for source, copy_ in ((RN, rn), (LANE, lane)):
        shutil.copytree(source, copy_, ignore=shutil.ignore_patterns("__pycache__"))
    repo = rn_files.repository(os.path.join(tmp, "invoicer"))
    origin = rn_files.with_origin(repo, os.path.join(tmp, "origin.git"))
    gh = os.path.join(tmp, "gh")
    env = environment(tmp)
    # The case's time zone, so that each script and hook takes the day that the case takes.
    env.update({name: os.environ[name] for name in ("TZ",) if name in os.environ})
    env["PATH"] = os.pathsep.join([gh_double.program(os.path.join(tmp, "bin"), gh), env["PATH"]])
    return Bench(rn, lane, repo, origin, gh, os.path.join(tmp, "claude"), env)


# The moves of the orchestrator, the main conversation, through the double.


def ran(c: Conversation, command: str, agent: Agent | None = None) -> str:
    """The main conversation, or the agent, runs the command, which the hooks must let through and
    which must give 0; gives what it printed."""
    answer = c.bash(command, agent)
    assert not answer.blocked, answer.said
    assert answer.exit_code == 0, answer.output
    return answer.output


def marked(c: Conversation, step: str, agent: Agent | None = None) -> Answer:
    """The main conversation, or the agent, reports the step done; the mark must go through, as
    Lane says no step's sentence of it. Lane stops a mark at its PostToolUse, which the double
    gives as what the model reads, not as a call stopped."""
    answer = c.bash(f"lane-step {step}", agent)
    assert not answer.blocked, answer.said
    assert not stopped(answer.said), answer.said
    return answer


def stopped(said: str) -> bool:
    """Whether what the model reads holds a sentence of Lane's that stops a move."""
    return any(each in said for each in ("You're at the step", "You end "))


def from_cwd(c: Conversation, path: str) -> str:
    """The path as Lane compares it, from the conversation's folder, as rules.py gives each."""
    return os.path.relpath(os.path.realpath(os.path.join(c.cwd, path)), os.path.realpath(c.cwd))


def listed(values: Sequence[str]) -> str:
    """The values as Lane's sentences list them, the last two joined by `and`."""
    *before, last = values
    return f"{', '.join(before)} and {last}" if before else last


def touched_items(b: Bench, c: Conversation, agent: Agent | None = None) -> list[str]:
    """The orchestrator runs `tree.py touched <run>`, reports each node it prints done as an item
    of the step `touched`, and gives the nodes."""
    nodes = ran(c, b.script("tree", "touched", b.run)).split()
    for node in nodes:
        c.bash(f"lane-item touched {node}", agent)
    return nodes


def written_tree(b: Bench, c: Conversation, design_tree: Mapping[str, Any]) -> Answer:
    """The orchestrator writes the run's design tree by the Write tool, keeping the session that
    the tree's context holds, as it edits the tree in place and leaves its context's session as
    `new` or a pick-up wrote it."""
    held = dict(design_tree)
    if os.path.isfile(b.tree_path) and held["context"].get("session") is None:
        session = b.tree()["context"].get("session")
        held["context"] = dict(held["context"], session=session)
    return c.write(None, b.tree_path, json.dumps(held, indent=1) + "\n")


def moved(
    b: Bench,
    c: Conversation,
    design_tree: Mapping[str, Any] | None = None,
    ground: str = "The run's facts decide it.",
    moves: Sequence[str] = (),
) -> list[str]:
    """The orchestrator keeps the steps that every event shares up to `move`: `review`, writing the
    design tree where one is given; `touched`, each node that `tree.py touched` prints reported
    done; `commit`, by `tree.py commit` with the ground; and `move`, each command given run, such
    as `repository.py put-up` or `tree.py cut`. Gives what each move printed."""
    if design_tree is not None:
        answer = written_tree(b, c, design_tree)
        assert not answer.blocked, answer.said
    marked(c, "review")
    touched_items(b, c)
    marked(c, "touched")
    ran(c, b.script("tree", "commit", b.run, ground))
    marked(c, "commit")
    printed = [ran(c, each) for each in moves]
    marked(c, "move")
    return printed


def shared_steps(
    b: Bench,
    c: Conversation,
    design_tree: Mapping[str, Any] | None = None,
    ground: str = "The run's facts decide it.",
    moves: Sequence[str] = (),
) -> list[str]:
    """The orchestrator keeps the steps that every event shares, as `moved` keeps them, and then
    `final`, which checks nothing while a deliverable isn't done. Gives what each move printed."""
    printed = moved(b, c, design_tree, ground, moves)
    marked(c, "final")
    return printed


def taken(
    b: Bench,
    c: Conversation,
    design_tree: Mapping[str, Any] | None = None,
    ground: str = "The run's facts decide it.",
    moves: Sequence[str] = (),
) -> list[str]:
    """The orchestrator keeps `take`, the first step of a send-back, an answer, and a role's end,
    writing the design tree there where one is given, and then the steps that every event shares,
    as `shared_steps` keeps them. Gives what each move printed."""
    if design_tree is not None:
        answer = written_tree(b, c, design_tree)
        assert not answer.blocked, answer.said
    marked(c, "take")
    return shared_steps(b, c, None, ground, moves)


def ended(c: Conversation, message: str = "Done.") -> Answer:
    """The orchestrator ends its turn with the message; the end must go through."""
    answer = c.stop(message)
    assert not answer.blocked, answer.said
    return answer


def heard(b: Bench) -> Conversation:
    """A conversation in which the user typed `/rn:on`, and the orchestrator kept its step `hear`
    and asked what it can help with."""
    c = b.converse()
    typed = c.type("/rn:on")
    assert not typed.blocked, typed.said
    marked(c, "hear")
    ended(c, "What can I help with? An issue number or a few words of what you want both work.")
    return c


def requested(b: Bench) -> Conversation:
    """A conversation in which the user typed `/rn:on`, the orchestrator asked what it can help
    with, the user typed the walkthrough's words, and the orchestrator made the run's worktree and
    its design tree with the goal as put, by `repository.py new`, kept the steps that every event
    shares, and put the goal's summary to the user."""
    c = heard(b)
    c.type(WORDS)
    ran(c, b.script("repository", "new", WORDS, GOAL, *LANGUAGES))
    marked(c, "start")
    shared_steps(b, c, ground="The goal as put.")
    summary = f"Here is what I'll work toward.\n\nFor: the accounting team\nGoal: {GOAL}"
    ended(c, f"{summary}\n\nIs that right?")
    return c


def planned_tree(b: Bench, answered: bool) -> dict[str, Any]:
    """The design tree once the user confirms the goal: the goal by user, the plan's conditions
    good but N2's while the tax rate's point is open, the command and the guide, and the point
    about the tax rate an open decision of the command's N1, or the user's answer once given."""
    name = b.name()
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER if answered else None, "user")
    design_tree = rn_files.walkthrough_tree(name, plan_done=False, command_decisions={"N1": [tax]})
    held = rn_files.conditions("design-tree")
    if not answered:
        held.remove("N2")
    design_tree["deliverables"][0] = rn_files.plan(name, good=held)
    if not answered:
        design_tree["work"].insert(
            0, rn_files.work("decide", rn_files.COMMAND, "N1", rn_files.TAX_ABOUT)
        )
    return design_tree


def confirmed(b: Bench, c: Conversation) -> None:
    """The user confirms the goal; the orchestrator writes the plan with the tax rate's point open
    and puts the point to the user."""
    c.type("yes")
    taken(b, c, planned_tree(b, answered=False), "The goal, as the user confirms it.")
    ended(c, f"The tax rate.\n\n{rn_files.TAX_POINT}")


def put_up_plan(b: Bench, c: Conversation) -> str:
    """The user answers the point; the orchestrator writes the answer as its decision by user, puts
    the plan up by `repository.py put-up`, and shows it with no link; gives what put-up printed."""
    c.type(rn_files.TAX_ANSWER)
    plan = rn_files.plan_path(b.name())
    printed = taken(
        b,
        c,
        planned_tree(b, answered=True),
        "The user's answer.",
        [b.script("repository", "put-up", b.run, plan)],
    )
    ended(c, f"The way to the goal:\n\n1. What it does ({rn_files.COMMAND})\n\nWhere do you check?")
    return printed[0].strip()


def to_plan_signoff(b: Bench) -> Conversation:
    """A conversation whose plan waits for the user's sign-off."""
    c = requested(b)
    confirmed(b, c)
    put_up_plan(b, c)
    return c


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


def signed_apart(
    b: Bench, design_tree: Mapping[str, Any], made: Sequence[str]
) -> tuple[Conversation, list[str]]:
    """A conversation whose goal the user confirmed, the orchestrator wrote the plan given and put
    it up, and the user signed it off by `/rn:ty`, the orchestrator writing the generator's Cut of
    each deliverable given; gives the conversation and each Cut's path."""
    c = requested(b)
    c.type("yes")
    plan = rn_files.plan_path(b.name())
    taken(b, c, design_tree, "The plan.", [b.script("repository", "put-up", b.run, plan)])
    ended(c, "The way to the goal.")
    moves = [b.script("tree", "cut", b.run, "generator", each) for each in made]
    return c, [each.strip() for each in signed(b, c, moves)]


def cut(b: Bench, c: Conversation, role: str, deliverable: str) -> str:
    """The orchestrator runs `tree.py cut` for the role and the deliverable, and gives the Cut's
    path from the repository's top that it printed."""
    return ran(c, b.script("tree", "cut", b.run, role, deliverable)).strip()


def started(c: Conversation, role: str, cut_path: str) -> Agent:
    """The orchestrator starts the role in the background with the Cut's path as its prompt; the
    start must go through."""
    answer, agent = c.start(role, cut_path, f"Run {role}")
    assert agent is not None, answer.said
    return agent


def signed_plan(b: Bench) -> tuple[Conversation, Agent]:
    """A conversation in which the user signed the plan off by `/rn:ty`, and the orchestrator
    recorded it by `tree.py signoff`, kept the shared steps, wrote the command's Cut, and started
    its generator, the one deliverable whose inputs are done; gives the generator."""
    c = to_plan_signoff(b)
    c.type("/rn:ty")
    ran(c, b.script("tree", "signoff", b.run))
    marked(c, "record")
    cut_path = shared_steps(
        b,
        c,
        ground="The user signs the plan off.",
        moves=[b.script("tree", "cut", b.run, "generator", rn_files.COMMAND)],
    )[0].strip()
    generator = started(c, "rn:generator", cut_path)
    ended(c, f'Making "{rn_files.COMMAND_NAME}".')
    return c, generator


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


def cut_of(c: Conversation, agent: Agent) -> dict[str, Any]:
    """The Cut that the agent's prompt names, read from the JSON of its file."""
    prompt = agent.start_use.get("tool_input", {}).get("prompt", "")
    return rn_files.read_json(os.path.join(c.cwd, prompt))


def items(c: Conversation, agent: Agent, step: str, ids: Sequence[str]) -> None:
    """The agent reports each item of the step's checklist done."""
    for each in ids:
        agent.bash(f"lane-item {step} {each}")


def read_step(b: Bench, c: Conversation, agent: Agent, given: Mapping[str, Any]) -> None:
    """The generator reads whole its Cut, its best practice's best-practice.md, each input that is
    a file, and each file of its deliverable that stands at its paths, and reports `read` done."""
    agent.read(os.path.join(c.cwd, agent.start_use["tool_input"]["prompt"]))
    md = os.path.join(c.cwd, given["best_practice"], "best-practice.md")
    if os.path.exists(md):
        agent.read(md)
    node = given["deliverable"]
    worktree = os.path.join(c.cwd, given["worktree"])
    stands = [os.path.join(worktree, each) for each in [node["path"], *node.get("more_paths", [])]]
    for each in [*(os.path.join(c.cwd, one) for one in given["inputs"]), *stands]:
        if os.path.isfile(each):
            agent.read(each)
    marked(c, "read", agent)


def kind_of(given: Mapping[str, Any]) -> str:
    """The kind of the best practice whose folder the Cut names."""
    return os.path.basename(os.path.normpath(given["best_practice"]))


def generated(
    b: Bench,
    c: Conversation,
    agent: Agent,
    files: Mapping[str, str] | None = None,
    good: Sequence[str] | None = None,
) -> Answer:
    """The generator keeps each of its steps and ends with `made`: it reads, reports each `decide`
    and `make` item of its best practice, writes each file of the deliverable, given by its path
    from the worktree's top or else the deliverable's own text, in a refactor Round runs at `try`
    the repository's tests as its developers run them, in its folder of the people's starting
    state that `repository.py trial` makes, which must go through and give 0, writes
    its result in the Round's folder, saw good each condition given or else every one, runs
    `repository.py checks` on its files, and gives `made`. Gives what the main conversation reads
    as its end reaches it."""
    given = cut_of(c, agent)
    node = given["deliverable"]
    read_step(b, c, agent, given)
    kind = kind_of(given)
    items(c, agent, "decide", rn_files.items_at(kind, "decide"))
    marked(c, "decide", agent)
    text = COMMAND_TEXT if node["path"].endswith(".py") else GUIDE_TEXT
    wrote = dict(files or {node["path"]: text})
    for path, content in wrote.items():
        agent.write(os.path.join(b.worktree, path), content)
    items(c, agent, "make", rn_files.items_at(kind, "make"))
    marked(c, "make", agent)
    # A generator names in `good` the conditions of its deliverable, as rn checks them, which in a
    # refactor Round are its content kind's, not those of the refactoring kind it makes by.
    seen = [each["id"] for each in node["necessary_conditions"]] if good is None else list(good)
    if given["stage"] == "refactor":
        trial = ran(c, b.script("repository", "trial", b.run, given["round"]), agent).strip()
        ran(c, DEVELOPERS_TESTS.format(trial), agent)
    first = next(iter(wrote.values())).splitlines()[0]
    result = rn_files.made([(each, [first]) for each in seen], list(wrote))
    agent.write(os.path.join(c.cwd, given["round"], "generator.json"), json.dumps(result))
    marked(c, "try", agent)
    ran(c, b.script("repository", "checks", b.run, *wrote), agent)
    agent.bash("lane-result made")
    marked(c, "check", agent)
    return reached(agent)


# The repository's tests as invoicer's developers run them, from a folder of its branch, writing no
# file.
DEVELOPERS_TESTS = "(cd {} && python3 -B -c 'import invoicer.lines')"


def pointed(b: Bench, c: Conversation, agent: Agent, words: str = rn_files.TAX_POINT) -> Answer:
    """The generator reads, finds at `decide` a point that only the user can settle, writes its
    result `point` in the Round's folder, and ends with `point`; gives what the main conversation
    reads as its end reaches it."""
    given = cut_of(c, agent)
    read_step(b, c, agent, given)
    agent.write(
        os.path.join(c.cwd, given["round"], "generator.json"), json.dumps(rn_files.point(words))
    )
    agent.bash("lane-result point")
    return reached(agent)


def reached(agent: Agent, reply: str = "made") -> Answer:
    """The subagent ends, its end must go through, and gives what the main conversation reads as
    its end reaches it."""
    stopped, notified = agent.end(reply)
    assert not stopped.blocked and notified is not None, stopped.said
    return notified


def evaluated(
    b: Bench, c: Conversation, agent: Agent, more: Mapping[str, str] | None = None
) -> Answer:
    """The evaluator keeps each of its steps and ends with `judged`: it reads its Cut, makes the
    folder of the people's starting state by `repository.py trial`, tries the deliverable there,
    reports each condition judged, writes its answers in the Round's folder, each condition good but
    those of `more`, with what would make each good, and gives `judged`. Gives what the main
    conversation reads as its end reaches it."""
    given = cut_of(c, agent)
    agent.read(os.path.join(c.cwd, agent.start_use["tool_input"]["prompt"]))
    marked(c, "read", agent)
    trial = ran(c, b.script("repository", "trial", b.run, given["round"]), agent).strip()
    marked(c, "start", agent)
    agent.write(os.path.join(trial, "lines.csv"), "Hosting;40.00;1\nSupport hours;120.00;1\n")
    marked(c, "try", agent)
    ids = [
        each["id"]
        for factor in given["judges_by"]["critical_success_factors"]
        for each in factor["necessary_conditions"]
    ]
    items(c, agent, "judge", ids)
    with open(os.path.join(b.worktree, given["deliverable"]["path"]), encoding="utf-8") as f:
        first = f.read().splitlines()[0]
    left = dict(more or {})
    result = rn_files.judged(
        [(each, [first]) for each in ids if each not in left], list(left.items())
    )
    agent.write(os.path.join(c.cwd, given["round"], "evaluator.json"), json.dumps(result))
    agent.bash("lane-result judged")
    marked(c, "judge", agent)
    return reached(agent, "judged")


# The moves of a run past the plan's sign-off, each through the double.


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


def made_command(b: Bench) -> tuple[Conversation, Answer]:
    """A conversation whose command's generator made its first Round and ended; gives what the
    main conversation read as its end reached it."""
    c, generator = signed_plan(b)
    return c, generated(b, c, generator)


def evaluator_started(b: Bench) -> tuple[Conversation, Agent]:
    """A conversation whose command's generator made its first Round, and whose orchestrator, at
    the generator's end, kept the shared steps, wrote the evaluator's Cut, and started it."""
    c, _ = made_command(b)
    cut_path = taken(
        b,
        c,
        ground="The generator made its Round.",
        moves=[b.script("tree", "cut", b.run, "evaluator", rn_files.COMMAND)],
    )[0].strip()
    evaluator = started(c, "rn:evaluator", cut_path)
    ended(c, "Trying it as its people would.")
    return c, evaluator


def judged_command(b: Bench, more: Mapping[str, str] | None = None) -> tuple[Conversation, Answer]:
    """A conversation whose command's evaluator judged its first Round, each condition good but
    those of `more`, and ended; gives what the main conversation read as its end reached it."""
    c, evaluator = evaluator_started(b)
    return c, evaluated(b, c, evaluator, more)


def next_round(
    b: Bench, c: Conversation, deliverable: str, good: Sequence[str], role: str = "generator"
) -> tuple[str, Agent]:
    """At a role's end, the orchestrator holds good the conditions given, keeps the shared steps,
    writes the role's Cut for the deliverable, and starts the role; gives the Cut's path and the
    role's agent."""
    cut_path = taken(
        b,
        c,
        held(b, deliverable, good),
        "The Round's findings.",
        [b.script("tree", "cut", b.run, role, deliverable)],
    )[0].strip()
    agent = started(c, f"rn:{role}", cut_path)
    ended(c, "Going on.")
    return cut_path, agent


def put_up(b: Bench, c: Conversation, deliverable: str, good: Sequence[str]) -> str:
    """At a role's end, the orchestrator holds good the conditions given, keeps the shared steps,
    and puts the deliverable up by `repository.py put-up`; gives the URL it printed."""
    url = taken(
        b,
        c,
        held(b, deliverable, good),
        "The Round's findings.",
        [b.script("repository", "put-up", b.run, deliverable)],
    )[0].strip()
    ended(c, f"For your sign-off. Changes: {url}")
    return url


def checked_whole(b: Bench, c: Conversation) -> list[str]:
    """At `final`, the orchestrator starts a plain subagent in the foreground, none of rn's roles,
    with the brief of the final check; it runs `repository.py diff`, then `repository.py ci`, and
    ends with no finding. Gives what each printed."""
    answer, checker = c.start(
        "general-purpose",
        "Check the work whole: the goal, the fit, nothing extra, and CI.",
        "Check the work whole",
        how=FOREGROUND,
    )
    assert checker is not None, answer.said
    printed = []
    for each in (b.script("repository", "diff", b.run), b.script("repository", "ci", b.run)):
        given = checker.bash(each)
        assert not given.blocked and given.exit_code == 0, given.said + given.output
        printed.append(given.output)
    ended_answer, _ = checker.end("No findings.")
    assert not ended_answer.blocked, ended_answer.said
    return printed


def signed(b: Bench, c: Conversation, moves: Sequence[str] = (), whole: bool = False) -> list[str]:
    """The user types `/rn:ty`; the orchestrator records the sign-off by `tree.py signoff`, keeps
    the shared steps with the moves given, and, where `whole`, checks the work whole at `final` by
    `checked_whole`; gives what the moves and the check printed."""
    c.type("/rn:ty")
    ran(c, b.script("tree", "signoff", b.run))
    marked(c, "record")
    printed = moved(b, c, ground="The user signs it off.", moves=moves)
    if whole:
        printed += checked_whole(b, c)
    marked(c, "final")
    return printed


def command_signed(b: Bench) -> tuple[Conversation, Agent]:
    """A conversation whose command was judged good in its first Round, put up, and signed off,
    and whose guide's generator then started; gives the guide's generator."""
    c, _ = judged_command(b)
    put_up(b, c, rn_files.COMMAND, rn_files.conditions("light"))
    cut_path = signed(b, c, [b.script("tree", "cut", b.run, "generator", rn_files.GUIDE)])[
        0
    ].strip()
    generator = started(c, "rn:generator", cut_path)
    ended(c, f'Making "{rn_files.GUIDE_NAME}".')
    return c, generator


def refactor_made(b: Bench) -> Conversation:
    """A conversation whose guide the evaluator judged good in Round content-1, and a new
    generator refactored in Round refactor-2, its end reaching the main conversation."""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, rn_files.GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    _, refactoring = next_round(b, c, rn_files.GUIDE, rn_files.conditions("readme"))
    generated(b, c, refactoring)
    return c


def refactored(b: Bench) -> Conversation:
    """A conversation whose guide `refactor_made` gives, which the orchestrator then put up for the
    user's sign-off."""
    c = refactor_made(b)
    put_up(b, c, rn_files.GUIDE, rn_files.conditions("readme"))
    return c


def decided_command(b: Bench) -> tuple[Conversation, Agent]:
    """A conversation whose command's generator read its inputs and kept its step `decide`, each
    decide item reported done."""
    c, generator = signed_plan(b)
    read_step(b, c, generator, cut_of(c, generator))
    items(c, generator, "decide", rn_files.items_at("light", "decide"))
    marked(c, "decide", generator)
    return c, generator


def trial_made(b: Bench) -> tuple[Conversation, Agent, dict[str, Any], str]:
    """A conversation whose command's evaluator read its Cut and made the people's folder by
    `repository.py trial`; gives the evaluator, its Cut, and the folder that trial printed."""
    c, evaluator = evaluator_started(b)
    given = cut_of(c, evaluator)
    evaluator.read(os.path.join(c.cwd, evaluator.start_use["tool_input"]["prompt"]))
    marked(c, "read", evaluator)
    trial = ran(c, b.script("repository", "trial", b.run, given["round"]), evaluator).strip()
    return c, evaluator, given, trial


def short_twice(b: Bench) -> Conversation:
    """A conversation whose command's N1 the evaluator found short in Rounds content-1 and
    content-2, the orchestrator holding N2 and N3 good, whose second evaluator's end reached the
    main conversation."""
    more = {"N1": "The accountant prints an invoice with a comma in a line."}
    c, _ = judged_command(b, more)
    _, generator = next_round(b, c, rn_files.COMMAND, ["N2", "N3"])
    generated(b, c, generator)
    _, evaluator = next_round(b, c, rn_files.COMMAND, ["N2", "N3"], "evaluator")
    evaluated(b, c, evaluator, more)
    return c


def sent_back(b: Bench, c: Conversation, deliverable: str, good: list[str], words: str) -> str:
    """The user types /rn:gm with the words; the orchestrator writes them as a decision by user of
    the deliverable's N1, held not good, keeps the shared steps, and writes the generator's Cut;
    gives the Cut's path that tree.py cut printed."""
    c.type(f"/rn:gm {words}")
    send_back = {"N1": [rn_files.decision(words, words, "user")]}
    design_tree = held(b, deliverable, [each for each in good if each != "N1"], send_back)
    return taken(
        b,
        c,
        design_tree,
        "The user sends it back.",
        [b.script("tree", "cut", b.run, "generator", deliverable)],
    )[0].strip()
