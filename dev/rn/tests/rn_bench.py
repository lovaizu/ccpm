"""What rn's integration cases share: the README's walkthrough as the cases play it on the double of
Claude Code. A bench holds copies of rn and Lane, the repository of `invoicer` with a remote to push
to, and the run's folder with the design tree of the walkthrough's plan once the person signed it
off, and each helper plays one move as the person, the orchestrator, or a role makes it, through the
double, or runs an adapter of rn's as Lane runs it, or rn's script of a start's Cut as the
orchestrator runs it."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

from claude_code import Conversation
from repo_files import environment, git, write_files

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
RN = os.path.join(TOP, "plugins", "rn")
LANE = os.path.join(TOP, "plugins", "lane")
INVOICER = os.path.join(TOP, "dev", "rn", "tests", "invoicer")

# The run's folder, from the top of the repository, as rn's Directory structure names it.
RUN = ".rn/20261119-invoices"
COMMAND = "invoicer/__main__.py"
GUIDE = "docs/print-invoice.md"
GOAL = (
    "The accounting team prints each invoice themselves from the lines they keep in a spreadsheet,"
    " without asking a developer. Once it holds, a colleague from accounting prints an invoice from"
    " the guide alone."
)


def conditions(kind: str) -> list[dict[str, Any]]:
    """Each necessary condition of the kind's best practice, in its order, none good yet."""
    path = os.path.join(RN, "domain", "best-practices", kind, "best-practice.json")
    with open(path, encoding="utf-8") as f:
        practice = json.load(f)
    return [
        {"id": n["id"], "good": False, "decisions": []}
        for c in practice["goal"]["critical_success_factors"]
        for n in c["necessary_conditions"]
    ]


def plan() -> dict[str, Any]:
    """The design tree of the walkthrough's plan, once the person signed it off: the command, with
    the tax rate given each time, before the guide that names it."""
    command = {
        "name": "Anyone at a terminal prints an invoice from a file of its lines with one command",
        "path": COMMAND,
        "kind": "code",
        "inputs": ["docs/architecture.md", "docs/software-design.md", "docs/test-design.md"],
        "status": "open",
        "necessary_conditions": conditions("code"),
    }
    command["necessary_conditions"][0]["decisions"] = [
        {"about": "The tax rate", "decided": "given with each invoice, as --rate", "by": "user"},
        {
            "about": "The lines",
            "decided": "read as invoicer already reads them, description;price;quantity",
            "by": "reasoning",
        },
    ]
    guide = {
        "name": "A colleague from accounting prints an invoice from the guide alone",
        "path": GUIDE,
        "kind": "readme",
        "inputs": ["docs/product-vision.md", COMMAND],
        "status": "open",
        "necessary_conditions": conditions("readme"),
    }
    return {
        "goal": {"decided": GOAL, "by": "user"},
        "deliverables": [command, guide],
        "work": [{"do": "make", "path": COMMAND}, {"do": "make", "path": GUIDE}],
    }


@dataclass(frozen=True)
class Bench:
    """Copies of rn and Lane, the repository of invoicer on the work's branch with its remote, the
    double's own folder, and the environment of each command."""

    rn: str
    lane: str
    repo: str
    remote: str
    temp: str
    env: dict[str, str]

    @property
    def run(self) -> str:
        """The run's folder."""
        return os.path.join(self.repo, RUN)

    def tree(self) -> dict[str, Any]:
        """The run's design tree as it reads now."""
        with open(os.path.join(self.run, "design-tree.json"), encoding="utf-8") as f:
            return json.load(f)

    def write_tree(self, tree: dict[str, Any]) -> None:
        """Writes the design tree as the orchestrator edits it."""
        write_files(self.run, {"design-tree.json": json.dumps(tree, indent=2) + "\n"})

    def converse(self) -> Conversation:
        """A new conversation in the repository, with rn and Lane loaded."""
        return Conversation(self.repo, [self.rn, self.lane], self.env, self.temp)

    def commit(self, c: Conversation, ground: str) -> Any:
        """The orchestrator commits the run's folder with the ground, by tree.py."""
        script = os.path.join(self.rn, "scripts", "tree.py")
        return c.bash(f"python3 {script} commit {RUN} {shlex.quote(ground)}")

    def check(self, agent: Any, role: str, cut: str) -> Any:
        """A role runs rn's check of its result beside its Cut, as Lane runs it at its end."""
        return agent.bash(f"python3 {os.path.join(self.rn, 'scripts', 'check.py')} {role} {cut}")

    def adapter(self, name: str, args: list[str], given: dict[str, Any]) -> tuple[int, Any, str]:
        """Runs rn's adapter as Lane runs it, in the repository, with what Lane gives on its
        standard input, and gives its exit code, what it printed, as JSON where it's JSON, and what
        it said."""
        done = subprocess.run(
            ["python3", os.path.join(self.rn, "lane", "adapters", f"{name}.py"), *args],
            input=json.dumps(given),
            capture_output=True,
            text=True,
            cwd=self.repo,
            env=self.env,
            check=False,
        )
        try:
            printed: Any = json.loads(done.stdout)
        except json.JSONDecodeError:
            printed = done.stdout
        return done.returncode, printed, done.stderr

    def due(
        self, words: str = "", moves: list[dict[str, Any]] | None = None
    ) -> tuple[int, Any, str]:
        """Runs rn's adapter of the starts due as Lane runs it, for a run of /rn:up with the words
        and the moves given, none by default."""
        run = {"skill": "rn:up", "words": words, "moves": moves or []}
        return self.adapter("starts_due", [], {"run": run})

    def cutting(self, role: str) -> tuple[int, str, str]:
        """Runs rn's script of a start's Cut as the orchestrator runs it, in the repository, for the
        role, and gives its exit code, the path it printed, and what it said."""
        script = os.path.join(self.rn, "scripts", "cut.py")
        done = subprocess.run(
            ["python3", script, role],
            capture_output=True,
            text=True,
            cwd=self.repo,
            env=self.env,
            check=False,
        )
        return done.returncode, done.stdout.strip(), done.stderr

    def cut(self, role: str) -> str:
        """The path of the Cut that rn writes for the role's start due."""
        code, path, said = self.cutting(role)
        assert code == 0, said
        return path

    def start(self, c: Conversation, role: str, does: str) -> tuple[str, Any]:
        """The orchestrator writes the Cut of the role's start due and starts the role in the
        conversation, with a prompt that names its Cut; gives the Cut's path and the agent, None
        where the start was stopped."""
        cut = self.cut(role)
        prompt = f"Carry out your steps, from your Cut at {cut}"
        return cut, c.start(f"rn:{role}", prompt, does)[1]

    def write_result(self, cut: str, result: dict[str, Any]) -> str:
        """Writes a role's result beside its Cut, as the role does, and gives its path."""
        path = os.path.join(self.repo, cut).removesuffix(".cut.json") + ".json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f)
        return path


def bench(tmp: str) -> Bench:
    """Copies of rn and Lane, and invoicer on the work's branch with a remote, holding the run's
    folder with the walkthrough's plan, committed and pushed."""
    rn, lane = os.path.join(tmp, "rn"), os.path.join(tmp, "lane")
    shutil.copytree(RN, rn, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(LANE, lane, ignore=shutil.ignore_patterns("__pycache__"))
    remote = os.path.join(tmp, "remote.git")
    subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
    repo = os.path.join(tmp, "invoicer")
    shutil.copytree(INVOICER, repo, ignore=shutil.ignore_patterns("__pycache__"))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "invoicer@example.com")
    git(repo, "config", "user.name", "invoicer")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "invoicer renders invoices")
    git(repo, "remote", "add", "origin", remote)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "-b", "rn/20261119-invoices")
    temp = os.path.join(tmp, "claude")
    env = environment(tmp)
    b = Bench(rn, lane, os.path.realpath(repo), remote, temp, env)
    b.write_tree(plan())
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "The plan, signed off")
    git(repo, "push", "-q", "-u", "origin", "rn/20261119-invoices")
    return b


def head(b: Bench) -> str:
    """The subject of the latest commit on the work's branch."""
    return git(b.repo, "log", "-1", "--format=%s").strip()


def read_json(b: Bench, path: str) -> Any:
    """The JSON file at the path in the repository."""
    with open(os.path.join(b.repo, path), encoding="utf-8") as f:
        return json.load(f)


def made(b: Bench, carried_out: list[dict[str, str]] | None = None) -> str:
    """The generator due ends with its deliverable made and a place for each decision named, none
    by default, and gives its Cut's path."""
    cut = b.cut("generator")
    deliverable = read_json(b, cut)["deliverable"]["path"]
    write_files(b.repo, {deliverable: "import sys\n"})
    each = [{**d, "at": f"{deliverable}:1"} for d in carried_out or []]
    b.write_result(cut, {"result": "made", "carried_out": each})
    return cut


def judged(b: Bench, more: dict[str, str]) -> list[tuple[str, str]]:
    """One evaluator for each group due ends, answering more on each condition named, with its
    good_when, and good on each other, and gives each group with its Cut's path."""
    done: list[tuple[str, str]] = []
    # Each group of the largest best practice once, and the none after them.
    for _ in range(7):
        code, cut, said = b.cutting("evaluator")
        if code == 1 and "no start" in said:
            return done
        assert code == 0, said
        conditions = read_json(b, cut)["conditions"]
        answers = {
            "good": [{"condition": c, "lines": ["x:1"]} for c in conditions if c not in more],
            "more": [{"condition": c, "good_when": more[c]} for c in conditions if c in more],
        }
        b.write_result(cut, answers)
        done.append((read_json(b, cut)["group"], cut))
    raise AssertionError(f"rn gave evaluators past each group: {done}")


def decided(b: Bench, condition: int, decision: dict[str, str], ground: str = "") -> None:
    """The orchestrator adds the decision under the command's condition at the index, and commits
    it with the ground where one is given."""
    tree = b.tree()
    tree["deliverables"][0]["necessary_conditions"][condition]["decisions"].append(decision)
    b.write_tree(tree)
    if ground:
        assert b.commit(b.converse(), ground).exit_code == 0


def command_done(b: Bench) -> None:
    """The orchestrator marks the command done, keeping its one line, and the guide comes next."""
    tree = b.tree()
    tree["deliverables"][0] = {k: tree["deliverables"][0][k] for k in ("name", "path", "kind")}
    tree["deliverables"][0]["status"] = "done"
    tree["work"] = tree["work"][1:]
    b.write_tree(tree)


def worktree(tmp: str, files: dict[str, Any] | None = None) -> str:
    """A git repository of invoicer's documents, the inputs of the plan's deliverables, with the
    run's folder holding the plan and each file given by its path, as JSON where it isn't text, all
    committed, for the unit cases; gives its top."""
    top = os.path.join(tmp, "invoicer")
    os.makedirs(top)
    git(top, "init", "-q", "-b", "main")
    git(top, "config", "user.email", "invoicer@example.com")
    git(top, "config", "user.name", "invoicer")
    docs = ("architecture", "software-design", "test-design", "product-vision")
    write_files(top, {f"docs/{name}.md": f"# {name}\n" for name in docs})
    given = {f"{RUN}/design-tree.json": plan(), **(files or {})}
    write_files(top, {p: v if isinstance(v, str) else json.dumps(v) for p, v in given.items()})
    git(top, "add", "-A")
    git(top, "commit", "-q", "-m", "The plan")
    return top
