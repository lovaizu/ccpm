"""What rn's integration cases share: the README's walkthrough as the cases play it on the double of
Claude Code. A bench holds a copy of rn and of Lane, side by side as Claude Code installs rn with
its dependency, the repository of invoicer, the walkthrough's library, with a remote to push to, and
the double of gh first on the PATH. Each helper plays one move of the walkthrough as the user, the
orchestrator, or a role makes it, through the double alone: the orchestrator and each role run rn's
scripts by the Bash tool, and rn's guard, Lane's code that Lane lays in rn's hooks/, holds each
call. What rn shows is taken from the README where the README shows it, so that a case fails
wherever rn shows other than its users read there."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from dev.tests.claude_code import Agent, Answer, Conversation
from dev.tests.repo_files import git, readme_block, write_files

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
RN = os.path.join(TOP, "plugins", "rn")
LANE = os.path.join(TOP, "plugins", "lane")
GH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gh")
INVOICER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "invoicer")
README = os.path.join(RN, "README.md")

# The walkthrough's request, the few words that name its goal, and the goal as the user confirms it.
WORDS = "type hints for invoicer, so that the people who call it see what each function takes"
GOAL_NAME = "type hints for invoicer"
GOAL = (
    "The people who call invoicer learn from their editor and their type checker what each"
    " function takes and returns, before their code runs."
)
# The walkthrough's two deliverables, as the plan names them, with the path each lies at.
HINTS = "Type hints in each file of invoicer, checked by mypy --strict"
HINTS_PATH = "invoicer"
TYPED = "invoicer marked as typed, so that the callers' type checkers read its hints"
TYPED_PATH = "invoicer/py.typed"
# The user's point of the walkthrough, and their answer.
POINT = "which files the hints cover"
EACH_FILE = "each file"
# The decision that the generator takes without asking, as the walkthrough's sign-off shows it.
DECIMAL = {
    "point": "the type of amounts and rates",
    "decided": "Decimal",
    "ground": "the code already computes with Decimal",
}
# What an evaluator gives under N2 of the first deliverable where the people fall short by it, and
# the decision under N2 that the tree-keeper changes for it.
SHOWN_AS_TYPED = "A caller's editor shows the type of each argument as they type the call."
EVERY_ARGUMENT = {"about": "what the hints name", "decided": "every argument", "by": "reasoning"}
# The best practice that finishes a deliverable of each kind, as the generator's Cut names it.
REFACTOR = {"code": "refactor-code", "readme": "refactor-doc"}
# What a README deliverable is for, in a plan of one.
NEWCOMER = "A newcomer decides from invoicer's README alone whether invoicer fits their work"
RESUMED = "The main conversation's grounds:\n"
# What coverage.py reads in a new process to measure it, and where it writes what it measured.
COVERAGE_SETTINGS = ("COVERAGE_PROCESS_START", "COVERAGE_FILE")
# Why a case of the walkthrough beyond the walking skeleton still fails: a part it reaches that a
# later deliverable builds.
NOT_YET = "a part of rn that the case reaches has an empty body or a step not yet written"


# What rn shows at each move of the walkthrough, as the README shows it.
GOAL_SHOWN = readme_block(README, f"/rn:up {WORDS}\n```\n\nrn shows:")
POINT_SHOWN = readme_block(README, "```text\nyes\n```\n\nrn shows:")
PLAN_SHOWN = readme_block(README, f"```text\n{EACH_FILE}\n```\n\nrn shows:")
PAUSED_SHOWN = readme_block(README, "```text\n/rn:dn\n```\n\nrn shows:")
PICKED_SHOWN = readme_block(README, "```text\n/rn:up\n```\n\nrn shows:")
NO_RUN_SHOWN = "rn has no run to pick up"


@dataclass
class Bench:
    """The folders of one case: rn's and Lane's copies, the repository of invoicer with its remote,
    the double's own folder, the file of what GitHub holds for the double of gh, and the
    environment that Claude Code runs with."""

    rn: str
    lane: str
    repo: str
    origin: str
    temp: str
    github: str
    env: dict[str, str]

    def script(self, name: str, *args: str) -> str:
        """The command that runs rn's script with the arguments, as a role or the orchestrator runs
        it."""
        words = [os.path.join(self.rn, "scripts", name), *args]
        return " ".join(["python3", *map(shlex.quote, words)])

    def tree(self, *args: str) -> str:
        return self.script("tree.py", *args)

    def record(self, *args: str) -> str:
        return self.script("record.py", *args)

    def throwaway(self, *args: str) -> str:
        return self.script("throwaway.py", *args)

    def result(self, role: str, result: str) -> str:
        """The command by which a role, or the skill up, gives its result, as Lane lays it in rn."""
        return f"python3 {self.rn}/hooks/lane/result.py {role} {result}"

    def fed(self, command: str, given: Any) -> str:
        """The command with the JSON given on its standard input, from a file of the double's
        folder."""
        folder = os.path.join(self.temp, "inputs")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{uuid.uuid4().hex}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(given if isinstance(given, str) else json.dumps(given))
        return f"{command} < {shlex.quote(path)}"

    def github_holds(self) -> dict[str, Any]:
        """What the double of gh keeps of GitHub: the login, each pull request, and each issue."""
        with open(self.github, encoding="utf-8") as f:
            return json.load(f)


def invoicer_files() -> dict[str, str]:
    """Each file of invoicer, by its path, as the walkthrough's library holds it before type
    hints."""
    found = {}
    for folder, _, names in os.walk(INVOICER):
        for name in names:
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8") as f:
                found[os.path.relpath(path, INVOICER)] = f.read()
    return found


def bench(tmp: str, logged_in: bool = True, remote: bool = True) -> Bench:
    """A copy of rn and of Lane, and the repository of invoicer, with a bare repository as its
    remote where `remote` is true, and gh logged in where `logged_in` is true."""
    plugins = os.path.join(tmp, "plugins")
    rn, lane = os.path.join(plugins, "rn"), os.path.join(plugins, "lane")
    shutil.copytree(RN, rn, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(LANE, lane, ignore=shutil.ignore_patterns("__pycache__"))
    repo = os.path.join(tmp, "invoicer")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "invoicer@example.com")
    git(repo, "config", "user.name", "invoicer")
    write_files(repo, invoicer_files())
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "invoicer 1.4.0")
    origin = os.path.join(tmp, "origin.git")
    if remote:
        subprocess.run(["git", "init", "-q", "--bare", origin], check=True)
        git(repo, "remote", "add", "origin", origin)
        git(repo, "push", "-q", "origin", "main")
    github = os.path.join(tmp, "github.json")
    with open(github, "w", encoding="utf-8") as f:
        json.dump({"logged_in": logged_in, "pulls": {}, "issues": []}, f)
    env = {
        "PATH": os.pathsep.join([GH, os.environ.get("PATH", os.defpath)]),
        "HOME": os.path.join(tmp, "home"),
        "TMPDIR": os.path.join(tmp, "system-temp"),
        "RN_GH_STATE": github,
    }
    # Where check.sh measures coverage, each script and hook that a case starts in a new process,
    # such as record.py check at a role's end, counts toward it as well.
    env.update({name: os.environ[name] for name in COVERAGE_SETTINGS if name in os.environ})
    os.makedirs(env["TMPDIR"])
    temp = os.path.join(tmp, "claude")
    return Bench(rn, lane, os.path.realpath(repo), origin, temp, github, env)


def converse(b: Bench) -> Conversation:
    """A new conversation at invoicer's root, with rn and Lane installed."""
    return Conversation(b.repo, [b.lane, b.rn], b.env, b.temp)


def printed(answer: Answer) -> Any:
    """The JSON that a command of rn printed, which must have given 0."""
    assert answer.exit_code == 0, answer.output or answer.said
    return json.loads(answer.output)


def due_text(said: str, role: str) -> str:
    """The text of the role's start that the guard gives due, as Lane gives each start due among
    the moves of one line after `rn: `: ``Start `rn:<role>` with `<text>`.``"""
    found = re.search(rf"Start `rn:{re.escape(role)}` with `(.*?)`\.(?: |$)", said, re.MULTILINE)
    assert found, f"the guard gives no start of {role} due: {said!r}"
    return found[1]


def cut_of(text: str) -> dict[str, Any]:
    """The Cut that a start's text holds, as one JSON line first."""
    return json.loads(text.split("\n", 1)[0])


def steps_of(plugin: str, file: str) -> list[int]:
    """The number of each step under `## Steps` of a prompt's file in the plugin."""
    with open(os.path.join(plugin, file), encoding="utf-8") as f:
        lines = f.read().split("\n")
    within, found = False, []
    for each in lines:
        if each.startswith("#"):
            within = each.strip() == "## Steps"
        elif within and re.match(r"^\d+\. ", each):
            found.append(int(each.split(".", 1)[0]))
    return found


def practices_of(plugin: str, kind: str, at: str) -> list[str]:
    """The ID of each practice of the kind's best practice that's carried out at `at`, decide or
    make, in its order."""
    path = os.path.join(plugin, "domain", "best-practices", kind, "best-practice.json")
    with open(path, encoding="utf-8") as f:
        goal = json.load(f)["goal"]
    return [
        f"{condition['id']}.{number}"
        for factor in goal["critical_success_factors"]
        for condition in factor["necessary_conditions"]
        for number, item in enumerate(condition["items"], 1)
        if item["at"] == at
    ]


def groups_of(plugin: str, kind: str) -> list[list[str]]:
    """The ID of each necessary condition of each group of the kind's best practice."""
    path = os.path.join(plugin, "domain", "best-practices", kind, "best-practice.json")
    with open(path, encoding="utf-8") as f:
        goal = json.load(f)["goal"]
    return [
        [condition["id"] for condition in factor["necessary_conditions"]]
        for factor in goal["critical_success_factors"]
    ]


def prompt_file(of: str) -> str:
    """The file of rn that holds a prompt's steps, by its role, its command, or orchestrator."""
    if of in ("up", "dn", "ty", "gm"):
        return f"skills/{of}/SKILL.md"
    return f"domain/{of}.md"


def keeps(
    b: Bench, who: Agent | Conversation, record: str, of: str, kinds: Sequence[str] = ()
) -> None:
    """The role, or the orchestrator, records its prompt's first step, each practice of each kind
    taken while deciding and then while making, and its other steps, each by record.py add, as its
    prompt says. Each must give 0."""
    steps = steps_of(b.rn, prompt_file(of))
    entries = [(of, str(n)) for n in steps[:1]]
    entries += [
        (k, p) for at in ("decide", "make") for k in kinds for p in practices_of(b.rn, k, at)
    ]
    entries += [(of, str(n)) for n in steps[1:]]
    for what, number in entries:
        ran = who.bash(b.record("add", record, what, number, f"{what} {number} carried out"))
        assert ran.exit_code == 0, ran.output or ran.said


def give(b: Bench, agent: Agent, result: str, message: str) -> tuple[Answer, Answer | None]:
    """The role gives its result by Lane's result script, and ends with the message; gives what the
    end met, and what the main conversation reads as the end reaches it."""
    role = agent.type.split(":")[-1]
    ran = agent.bash(b.result(role, result))
    assert ran.exit_code == 0, ran.output or ran.said
    return agent.end(message)


def reached(b: Bench, agent: Agent, result: str, message: str) -> Answer:
    """What the main conversation reads as the role's end, with its result, reaches it; the end
    must pass."""
    ended, then = give(b, agent, result, message)
    assert not ended.blocked, ended.said
    assert then is not None
    return then


def resume_text(grounds: str, words: str | None = None, change: Any = None) -> str:
    """The message by which the orchestrator resumes a role, in the form of its in-schema's resume:
    the grounds, the person's words as they wrote them, and the change to write."""
    text = RESUMED + grounds + "\n"
    if words is not None:
        text += "The person's words:\n" + words + "\n"
    if change is not None:
        text += "The change:\n" + json.dumps(change) + "\n"
    return text


def condition_nodes(kind: str) -> list[dict[str, Any]]:
    """Each necessary condition of the kind's best practice, not yet good, with no decision."""
    return [
        {"id": each, "good": False, "decisions": []}
        for group in groups_of(RN, kind)
        for each in group
    ]


def deliverable(name: str, path: str, kind: str = "code") -> dict[str, Any]:
    """A deliverable of the kind, open, with each necessary condition of its best practice."""
    return {
        "name": name,
        "path": path,
        "kind": kind,
        "inputs": [],
        "preconditions": [],
        "status": "open",
        "necessary_conditions": condition_nodes(kind),
    }


def plan(*deliverables: dict[str, Any]) -> dict[str, Any]:
    """The goal drafted and a plan of the deliverables, as tree.py write takes them."""
    nodes = {"goal": {"decided": GOAL, "by": "reasoning"}, "deliverables": list(deliverables)}
    return {"nodes": nodes, "more": []}


def walkthrough_plan() -> dict[str, Any]:
    """The walkthrough's plan: type hints in each file, then invoicer marked as typed."""
    return plan(deliverable(HINTS, HINTS_PATH), deliverable(TYPED, TYPED_PATH))


def hints_plan() -> dict[str, Any]:
    """A plan of the walkthrough's first deliverable alone."""
    return plan(deliverable(HINTS, HINTS_PATH))


def readme_plan() -> dict[str, Any]:
    """A plan of invoicer's README alone, a kind whose best practice holds a Markdown template."""
    return plan(deliverable(NEWCOMER, "README.md", "readme"))


@dataclass
class Walk:
    """Where one case's run of the walkthrough stands: the conversation, what tree.py start printed,
    the tree-keeper, what the main conversation last read from the guard, and each role started
    since."""

    c: Conversation
    run: dict[str, Any]
    keeper: Agent
    said: str
    agents: list[Agent] = field(default_factory=list)

    def folder(self, *names: str) -> str:
        """A path in the run's folder."""
        return os.path.join(self.run["worktree"], self.run["folder"], *names)

    def branch(self) -> str:
        """The work's branch, which the run's worktree is on."""
        return git(self.run["worktree"], "branch", "--show-current").strip()


def asked(
    b: Bench, c: Conversation | None = None, words: str = WORDS
) -> tuple[Conversation, Answer]:
    """The user types /rn:up with the request; the guard must let it through."""
    c = c or converse(b)
    answer = c.type(f"/rn:up {words}")
    assert not answer.blocked, answer.said
    return c, answer


def run_made(b: Bench, c: Conversation, goal: str = GOAL_NAME) -> tuple[dict[str, Any], Answer]:
    """The orchestrator makes the run's worktree by tree.py start and enters it; gives what tree.py
    start printed, and what the main conversation read as it entered."""
    run = printed(c.bash(b.tree("start", goal)))
    entered = c.enter_worktree(path=run["worktree"])
    assert not entered.blocked, entered.said
    return run, entered


def due_text_of(agent: Agent) -> str:
    """The text that the agent was started with."""
    return agent.start_use["tool_input"]["prompt"]


def started(c: Conversation, role: str, said: str) -> tuple[Answer, Agent]:
    """The orchestrator starts the role with the text that the guard gave due for it."""
    answer, agent = c.start(f"rn:{role}", due_text(said, role), role)
    assert agent is not None, answer.said
    return answer, agent


def keeper_started(b: Bench, c: Conversation, run: dict[str, Any], said: str) -> Walk:
    """The tree-keeper starts with its Cut, reads it, and ends done."""
    _, keeper = started(c, "tree-keeper", said)
    record = cut_of(due_text_of(keeper))["record"]
    keeps(b, keeper, record, "tree-keeper")
    then = reached(b, keeper, "done", "Read the design tree.")
    return Walk(c, run, keeper, then.said)


def keeper_writes(
    b: Bench, w: Walk, grounds: str, change: Any, words: str | None = None
) -> dict[str, Any]:
    """The orchestrator resumes the tree-keeper with a change, which it writes by tree.py write and
    ends done; gives what tree.py write printed, and keeps in the walk what the main conversation
    read."""
    resumed = w.c.resume(w.keeper, resume_text(grounds, words, change))
    assert not resumed.blocked, resumed.said
    record = cut_of(due_text_of(w.keeper))["record"]
    wrote = printed(w.keeper.bash(b.fed(b.tree("write", record, grounds), change)))
    keeps(b, w.keeper, record, "tree-keeper", ("design-tree",))
    w.said = reached(b, w.keeper, "done", json.dumps(wrote)).said
    return wrote


def opened(b: Bench, change: Any = None) -> Walk:
    """The walkthrough up to the goal and the plan in the design tree: the request, the run made and
    entered, the tree-keeper started, and the goal drafted and the plan written."""
    c, _ = asked(b)
    run, entered = run_made(b, c)
    w = keeper_started(b, c, run, entered.said)
    keeper_writes(b, w, "The goal drafted, and the plan.", change or walkthrough_plan())
    return w


def orchestrator_ends(b: Bench, w: Walk, command: str, shown: str) -> Answer:
    """The orchestrator records the steps of the command and of its part, and ends its turn with
    what it shows; gives what the stop met."""
    keeps(b, w.c, w.run["record"], command)
    keeps(b, w.c, w.run["record"], "orchestrator")
    return w.c.stop(shown)


def confirmed(b: Bench, change: Any = None) -> Walk:
    """The walkthrough up to the user's point answered: the goal put to the user and confirmed, the
    point written open and put to them, and their answer written by them."""
    w = opened(b, change)
    assert not orchestrator_ends(b, w, "up", GOAL_SHOWN).blocked
    assert not w.c.type("yes").blocked
    goal = {"decided": GOAL, "by": "user"}
    point = {"about": POINT, "decided": None}
    open_point = {"goal": goal, "deliverables/0/necessary_conditions/0/decisions/0": point}
    keeper_writes(b, w, "The user confirmed the goal.", {"nodes": open_point, "more": []}, "yes")
    assert not orchestrator_ends(b, w, "up", POINT_SHOWN).blocked
    assert not w.c.type(EACH_FILE).blocked
    answered = {"about": POINT, "decided": EACH_FILE, "by": "user"}
    nodes = {"deliverables/0/necessary_conditions/0/decisions/0": answered}
    keeper_writes(b, w, "The user's answer.", {"nodes": nodes, "more": []}, EACH_FILE)
    return w


def plan_put_up(b: Bench, change: Any = None) -> Walk:
    """The walkthrough up to the plan put up for the user's sign-off: the work pushed with its draft
    pull request, the plan put up, and the orchestrator's turn ended with it."""
    w = confirmed(b, change)
    printed(w.c.bash(b.tree("push")))
    printed(w.c.bash(b.tree("put-up", "plan")))
    stopped = orchestrator_ends(b, w, "up", PLAN_SHOWN)
    assert not stopped.blocked, stopped.said
    return w


def approved(b: Bench, w: Walk, grounds: str, change: Any = None) -> dict[str, Any]:
    """The user's /rn:ty, the sign-off waiting approved by tree.py approve, and the tree-keeper's
    write of the change, none by default, which marks each deliverable whose turn has come doing;
    gives what tree.py write printed."""
    typed = w.c.type("/rn:ty")
    assert not typed.blocked, typed.said
    printed(w.c.bash(b.tree("approve")))
    return keeper_writes(b, w, grounds, change or {"nodes": {}, "more": []}, "/rn:ty")


def planned(b: Bench, change: Any = None) -> Walk:
    """The walkthrough up to the plan signed off, each deliverable whose turn has come doing."""
    w = plan_put_up(b, change)
    approved(b, w, "The user signed off the plan.")
    return w


def generator_started(w: Walk) -> tuple[Agent, dict[str, Any]]:
    """The orchestrator starts the generator with the text that the guard gives due; gives it with
    its Cut."""
    answer, generator = started(w.c, "generator", w.said)
    w.said = answer.posted
    w.agents.append(generator)
    return generator, cut_of(due_text_of(generator))


def kinds_of(cut: dict[str, Any]) -> tuple[str, str]:
    """The kind of the deliverable of a generator's Cut, and the refactor best practice's."""
    return cut["kind"], os.path.basename(cut["refactor"].rstrip("/"))


def made(
    b: Bench, w: Walk, generator: Agent, cut: dict[str, Any], every_item: bool = True
) -> dict[str, Any]:
    """The generator makes the deliverable of its Cut: records each step and practice, commits at
    the end of each step, tries its work in a throwaway copy, and writes its Made, naming each
    decision and More kept of its Cut where `every_item` is true and none where it's false; gives
    the Made."""
    keeps(b, generator, cut["record"], "generator", kinds_of(cut))
    for number in steps_of(b.rn, "domain/generator.md") or [1]:
        ran = generator.bash(b.tree("commit", cut["record"], str(number)))
        assert ran.exit_code == 0, ran.output or ran.said
    tried = generator.bash(b.throwaway(cut["deliverable"], "python3 -m compileall -q invoicer"))
    assert tried.exit_code == 0, tried.output or tried.said
    where = cut["deliverable"]
    decisions = [each["decision"]["path"] for each in cut["cut"]["decisions"]]
    more = [each["condition"] for each in cut["cut"]["more"]]
    result = {
        "decisions": [{"path": d, "where": where} for d in decisions if every_item],
        "more": [{"condition": m, "where": where} for m in more if every_item],
        "settled": [DECIMAL],
    }
    written = generator.write(os.path.join(w.c.cwd, cut["made"]), json.dumps(result))
    assert not written.blocked, written.said
    return result


def answers(conditions: Sequence[str], more: Mapping[str, str] | None = None) -> dict[str, Any]:
    """An evaluator's Answers: each condition in good with a line that meets it, but each that
    `more` names, in more with its good_when."""
    more = more or {}
    line = "def total(lines: list[Line], rate: Decimal) -> Decimal:"
    return {
        "good": [{"question": c, "lines": [line]} for c in conditions if c not in more],
        "more": [{"question": c, "good_when": more[c]} for c in conditions if c in more],
    }


def evaluated(
    b: Bench, w: Walk, kinds: Sequence[str], more: Mapping[str, str] | None = None
) -> list[dict[str, Any]]:
    """One evaluator starts for each group of necessary conditions of the kinds' best practices,
    each with the text that the guard gives due, commits its work, writes its Answers, and ends
    done; gives each evaluator's Cut."""
    cuts, evaluators = [], []
    for _ in range(sum(len(groups_of(b.rn, kind)) for kind in kinds)):
        answer, evaluator = started(w.c, "evaluator", w.said)
        w.said = answer.posted
        evaluators.append(evaluator)
        cut = cut_of(due_text_of(evaluator))
        cuts.append(cut)
        ran = evaluator.bash(b.tree("commit", cut["record"], "1"))
        assert ran.exit_code == 0, ran.output or ran.said
        path = os.path.join(w.c.cwd, cut["answers"])
        assert not evaluator.write(path, json.dumps(answers(cut["conditions"], more))).blocked
        keeps(b, evaluator, cut["record"], "evaluator")
    w.agents += evaluators
    for evaluator in evaluators:
        w.said = reached(b, evaluator, "done", "Done.").said
    return cuts


def generator_in_step_2(b: Bench) -> tuple[Walk, Agent, dict[str, Any]]:
    """The walkthrough up to its generator in step 2: the plan signed off, and the generator of the
    first deliverable started, which committed the end of its step 1; gives the walk, the
    generator, and its Cut."""
    w = planned(b)
    generator, cut = generator_started(w)
    ran = generator.bash(b.tree("commit", cut["record"], "1"))
    assert ran.exit_code == 0, ran.output or ran.said
    return w, generator, cut


def deliverable_made(b: Bench, change: Any = None) -> tuple[Walk, dict[str, Any]]:
    """The walkthrough up to its first deliverable made: the plan signed off, and the generator's
    deliverable made and its end passed; gives the walk and the generator's Cut."""
    w = planned(b, change)
    generator, cut = generator_started(w)
    made(b, w, generator, cut)
    w.said = reached(b, generator, "done", "Made.").said
    return w, cut


def first_round(
    b: Bench, more: Mapping[str, str] | None = None, change: Any = None
) -> tuple[Walk, dict[str, Any], list[dict[str, Any]]]:
    """The walkthrough up to the first round of its first deliverable judged: the deliverable made,
    and each evaluator's Answers written, with `more` as each necessary condition that falls short;
    gives the walk, the generator's Cut, and each evaluator's Cut."""
    w, cut = deliverable_made(b, change)
    return w, cut, evaluated(b, w, kinds_of(cut), more)


def short_by_n2_kept(b: Bench, w: Walk) -> None:
    """The orchestrator judges that the people fall short by N2 of the first round, and the
    tree-keeper writes EVERY_ARGUMENT under N2 of the first deliverable, with the more of
    SHOWN_AS_TYPED to keep."""
    nodes = {"deliverables/0/necessary_conditions/1/decisions/0": EVERY_ARGUMENT}
    more = [{"deliverable": HINTS_PATH, "condition": "N2", "good_when": SHOWN_AS_TYPED}]
    keeper_writes(b, w, "The people fall short by N2.", {"nodes": nodes, "more": more})


def sign_off_put_up(b: Bench, change: Any = None) -> tuple[Walk, dict[str, Any]]:
    """The walkthrough up to its first deliverable put up for the user's sign-off, every necessary
    condition good; gives the walk and the generator's Cut."""
    w, cut, _ = first_round(b, change=change)
    printed(w.c.bash(b.tree("round", cut["deliverable"])))
    printed(w.c.bash(b.tree("push")))
    printed(w.c.bash(b.tree("put-up", "deliverable", cut["deliverable"])))
    stopped = orchestrator_ends(b, w, "up", f'"{HINTS}", for your sign-off:')
    assert not stopped.blocked, stopped.said
    return w, cut


def handed_over(b: Bench) -> tuple[Walk, str]:
    """A run of the walkthrough's first deliverable alone up to the pull request handed over: the
    deliverable signed off and marked done, and tree.py ready; gives the walk and the pull
    request's URL."""
    w, _ = sign_off_put_up(b, hints_plan())
    done = {"name": HINTS, "path": HINTS_PATH, "kind": "code", "status": "done"}
    approved(b, w, "The user signed it off.", {"nodes": {"deliverables/0": done}, "more": []})
    url = printed(w.c.bash(b.tree("ready")))
    stopped = orchestrator_ends(
        b, w, "up", f"Done. The pull request is ready for your merge: {url}"
    )
    assert not stopped.blocked, stopped.said
    return w, url


def tree_in(w: Walk) -> dict[str, Any]:
    """The run's design tree, as its folder holds it."""
    with open(w.folder("design-tree.json"), encoding="utf-8") as f:
        return json.load(f)


def sign_offs_in(w: Walk) -> list[dict[str, Any]]:
    """The run's sign-offs, as its folder holds them."""
    with open(w.folder("sign-offs.json"), encoding="utf-8") as f:
        return json.load(f)["sign_offs"]


def files_holding(folder: str, text: str) -> list[str]:
    """Each file under the folder whose text holds the text given."""
    found = []
    for at, _, names in os.walk(folder):
        for name in names:
            path = os.path.join(at, name)
            with open(path, encoding="utf-8", errors="replace") as f:
                if text in f.read():
                    found.append(path)
    return found
