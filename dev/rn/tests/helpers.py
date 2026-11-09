"""What rn's tests stand on beside what every plugin's tests do: rn's code on sys.path, its modules
taken by each test from here, so each test finds them whichever runs first; and a test that stands
in a repository of tidy, the README's walkthrough's tool, made once a run and copied into each
test's folder, with the system's temporary folder in the test's folder, so the run's folder there
goes with the test."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import sys
import tempfile
from typing import Any
from unittest import mock

RN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "rn")
)
DOMAIN = os.path.join(RN, "domain")
SCRIPTS = os.path.join(RN, "scripts")
ADAPTERS = os.path.join(RN, "hooks", "adapters")
sys.path[:0] = [DOMAIN, SCRIPTS, os.path.join(RN, "..", "..", "dev", "lane")]

import edits
import files
import practices
import records
import repository
import runs
import starts
import testing
import throwaway
import tree
import trees
import tries

__all__ = [
    "edits",
    "files",
    "practices",
    "records",
    "repository",
    "runs",
    "starts",
    "testing",
    "throwaway",
    "tree",
    "trees",
    "tries",
]

# The run of the README's walkthrough, and its goal as the planner drafts it.
RUN = os.path.join(".rn", "20261108-tidy-dry-run")
GOAL = "Someone about to sort their Downloads folder with tidy sees what it would move."
# tidy's repository as the walkthrough finds it.
TIDY = {
    "README.md": "# tidy\n\ntidy sorts a Downloads folder into folders by type.\n",
    "tidy/cli.py": "def main():\n    pass\n",
    "dev/product-vision.md": "# tidy\n\nSomeone sorts their Downloads folder.\n",
}


def deliverable(path: str, kind: str, **given: Any) -> dict[str, Any]:
    """A deliverable not done of the path and kind, each intent of its kind's best practice not
    good, as tree.py lays it, the fields given put in."""
    intents = practices.intents(
        practices.read(os.path.join(practices.OWN, kind, "best-practice.json"))
    )
    made = {
        "name": f"the {kind} of tidy",
        "path": path,
        "kind": kind,
        "inputs": [],
        "preconditions": [],
        "status": "open",
        "necessary_conditions": [{"id": i, "good": False, "decisions": []} for i in intents],
    }
    made.update(given)
    return made


def loaded(data: Any) -> Any:
    """The data written as JSON and read back, as rn reads its files."""
    return json.loads(json.dumps(data))


def done(path: str, name: str, kind: str = "readme") -> dict[str, Any]:
    """A deliverable done, in the one line the tree keeps of it."""
    return {"name": name, "path": path, "kind": kind, "status": "done"}


def walkthrough(by: str = "user") -> dict[str, Any]:
    """The walkthrough's tree once the planner lays the plan: the goal settled by whom, the README,
    which takes from the product vision, and tidy/cli.py, which takes from the README; read back
    from JSON, as rn reads a tree, so no text of it's one of the code's own."""
    return loaded(
        {
            "goal": {"decided": GOAL, "by": by},
            "deliverables": [
                deliverable("README.md", "readme", inputs=["dev/product-vision.md"]),
                deliverable("tidy/cli.py", "code", inputs=["README.md"]),
            ],
        }
    )


def decided(tree: dict[str, Any], n: int, intent: str, about: str, what: Any, by: str = "user"):
    """The tree with a decision about the point under the intent of the deliverable of the
    number, open where what's None."""
    made = copy.deepcopy(tree)
    for i in made["deliverables"][n - 1]["necessary_conditions"]:
        if i["id"] == intent:
            decision = {"about": about, "decided": what}
            if what is not None:
                decision["by"] = by
            i["decisions"].append(decision)
    return made


def ran(module: Any, *argv: str, stdin: str = "") -> tuple[int, str, str]:
    """What the script module's main gives on the arguments, the text on its standard input: its
    exit code, what it printed, and its errors."""
    out, err = io.StringIO(), io.StringIO()
    stdin_ = mock.patch("sys.stdin", io.StringIO(stdin))
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), stdin_:
        code = module.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class RunTest(testing.GitTest):
    """A test standing in tidy's repository, `repo` in `base`, committed on main, with the system's
    temporary folder in `base`."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.copied("tidy", self.make)
        self.tmp = os.path.join(self.base, "tmp")
        os.makedirs(self.tmp)
        patched = mock.patch.object(tempfile, "tempdir", self.tmp)
        patched.start()
        self.addCleanup(patched.stop)

    def make(self) -> None:
        """tidy's repository, its files committed on main."""
        self.git("init", "-q", "-b", "main")
        for name, text in TIDY.items():
            self.write(name, text)
        self.commit()

    def lays(self, data: dict[str, Any], run: str = RUN) -> None:
        """The run's tree written, as tree.py writes it."""
        files.save(runs.tree_path(run), data)

    def commits(self, data: dict[str, Any], run: str = RUN) -> None:
        """The run's tree written and committed on its branch, as the planner's last commit left
        it."""
        self.lays(data, run)
        repository.commit(run, [run], "rn: laid")

    def edit(self, data: dict[str, Any], run: str = RUN) -> str:
        """The planner's tree edit written at its path: the path."""
        path = os.path.join(runs.temporary(run), runs.EDIT)
        self.write_json(path, data)
        return path

    def tree_now(self, run: str = RUN) -> dict[str, Any]:
        """The run's tree on disk."""
        return self.read_json(runs.tree_path(run))

    def handed(self, data: dict[str, Any]) -> str:
        """The change handed by tree.py change: what it printed."""
        return starts.change(json.dumps(data))


# A small best practice of the kind `note`, which the run keeps as its own: two intents, each of a
# part of its own, so a round has two evaluators.
NOTE = {
    "goal": "Someone new to tidy sorts their folder with it.",
    "inputs": [],
    "preconditions": [],
    "parts": [{"id": "use", "what": "How to use it."}],
    "necessary_conditions": [
        {"id": "Q1", "about": "use", "what": "Can the reader sort their folder by it?"},
        {"id": "Q2", "about": "the whole", "what": "Does each answer come when needed?"},
    ],
    "practices": [
        {
            "intent": "Q1",
            "thinking": "Show the run.",
            "steps": [
                {
                    "text": "Read what it takes from.",
                    "trace": {"action": "read", "takes": ["{inputs}"]},
                }
            ],
        },
        {"intent": "Q2", "thinking": "Order it.", "steps": []},
    ],
}
NOTES = "NOTES.md"
# What a note says once the generator has made it.
NOTED = "# Notes\n\nRun `tidy --dry-run` to see each move, then `tidy` to make them.\n"


def note_tree(by: str = "user", **given: Any) -> dict[str, Any]:
    """A tree of the one deliverable, a note of the kind note, taking from the product vision."""
    d = {
        "name": "a note on tidy's dry run",
        "path": NOTES,
        "kind": "note",
        "inputs": ["dev/product-vision.md"],
        "preconditions": [],
        "status": "doing",
        "necessary_conditions": [
            {"id": "Q1", "good": False, "decisions": []},
            {"id": "Q2", "good": False, "decisions": []},
        ],
    }
    d.update(given)
    return {"goal": {"decided": GOAL, "by": by}, "deliverables": [d]}


class Claude(testing.ClaudeCode):
    """The double of Claude Code, which also keeps what the last Bash call printed, or its error, as
    the call's result hands it to whoever made it."""

    printed = ""

    def made(self, tool: str, given: dict[str, Any]) -> tuple[Any, str | None]:
        response, error = super().made(tool, given)
        if tool == "Bash":
            self.printed = error if error is not None else response["stdout"]
        return response, error


def lines_of(context: list[str]) -> list[str]:
    """Lane's lines to the main conversation in the context the hooks added, each headed `rn:`."""
    return [line for said in context for line in said.splitlines() if line.startswith("rn: ")]


class FlowTest(RunTest):
    """A test of a path of rn's sequences, in tidy's repository: rn's guard, by its hook entries on
    its lanes and routes laid, tree.py, throwaway.py and the adapters run real, through a double of
    Claude Code working in the repository; doubles stand in for the main conversation, the roles,
    making set calls and giving set results, and the user, giving set answers."""

    def setUp(self) -> None:
        super().setUp()
        self.env = {**os.environ, "TMPDIR": self.tmp}
        hook, guard, schema = testing.lane_code(RN, "hook", "guard", "schema")

        def handed(event: dict[str, Any]) -> str:
            named = event["hook_event_name"]
            wrong = hook.event_wrong({"agent_id": "main", "agent_type": "", **event}, named)
            if not wrong and named == "PostToolUse" and event["tool_name"] == "Agent":
                out = schema.held(guard.BACK, event["tool_response"])
                wrong = out.told() if out is not None else ""
            return wrong

        self.claude = Claude(RN, self.repo, self.env, check=handed)
        self.made_runs = 0

    def new(self, role: str) -> Any:
        """A new run of rn's role."""
        self.made_runs += 1
        return testing.Run(f"rn:{role}", f"{role[0]}{self.made_runs}")

    def begins(self) -> list[str]:
        """The user types `/rn:up`: the lines Lane gives the main conversation."""
        return lines_of(self.claude.typed("rn:up"))

    def calls_up(self) -> list[str]:
        """The main conversation calls the skill rn:up itself: Lane's lines it's told."""
        called = self.claude.skill("rn:up")
        self.assertTrue(called.made, called.said)
        return lines_of(called.context)

    def tree_command(self, *words: str) -> str:
        """The command of tree.py with the words."""
        return " ".join(("python3", f"{RN}/scripts/tree.py", *words))

    def hands(self, change: dict[str, Any]) -> str:
        """The main conversation hands the change to tree.py change on its standard input: what it
        printed."""
        command = f"{self.tree_command('change')} <<'EOF'\n{json.dumps(change)}\nEOF"
        told_ = self.claude.call(None, "Bash", {"command": command, "description": "d"})
        self.assertTrue(told_.made, told_.said)
        return self.claude.printed

    def main_runs(self, *words: str) -> str:
        """The main conversation runs tree.py with the words: what it printed."""
        told_ = self.claude.call(
            None, "Bash", {"command": self.tree_command(*words), "description": "d"}
        )
        self.assertTrue(told_.made, told_.said)
        return self.claude.printed

    def starts(self, run: Any, prompt: str) -> Any:
        """The main conversation starts the run with the prompt, which goes through, and ends its
        turn: what Lane told the start."""
        told_ = self.claude.start(None, run, prompt)
        self.assertTrue(told_.made, told_.said)
        self.assertTrue(self.claude.end_turn().made)
        return told_

    def cut_and_start(self, role: str) -> tuple[Any, dict[str, Any]]:
        """The main conversation runs the start command for the role and starts a new run of it
        with what it printed: the run and its values."""
        printed = self.main_runs("start", role)
        run = self.new(role)
        self.starts(run, printed)
        return run, json.loads(printed.splitlines()[0])

    def does(self, run: Any, tool: str, **given: Any) -> Any:
        """The run's call of the tool with its input."""
        return self.claude.call(run, tool, given)

    def runs(self, run: Any, command: str) -> str:
        """The run runs the command with Bash, which goes through: what it printed."""
        told_ = self.does(run, "Bash", command=command, description="d")
        self.assertTrue(told_.made, told_.said)
        return self.claude.printed

    def writes(self, run: Any, path: str, data: Any) -> None:
        """The run writes the data at the path with Write, as JSON where it's no text, which goes
        through."""
        text = data if isinstance(data, str) else json.dumps(data)
        told_ = self.does(run, "Write", file_path=os.path.join(self.repo, path), content=text)
        self.assertTrue(told_.made, told_.said)

    def reads(self, run: Any, path: str) -> None:
        """The run reads the file at the path whole, which goes through."""
        told_ = self.does(run, "Read", file_path=os.path.join(self.repo, path))
        self.assertTrue(told_.made, told_.said)

    def gives(self, run: Any, on: str) -> None:
        """The run gives its result by its result command, which goes through."""
        name = run.kind.split(":")[1]
        self.runs(run, f"python3 {RN}/hooks/lane/result.py {name} {on}")

    def ends(self, run: Any) -> list[str]:
        """The run ends, let end, and its end reaches the main conversation: Lane's lines it's
        told."""
        ended = self.claude.stop(run)
        self.assertTrue(ended.made, ended.said)
        return lines_of(self.claude.notify(run))

    def plans(self, planner: Any, values: dict[str, Any], *edits: dict[str, Any]) -> str:
        """The planner writes each edit and has tree.py write it, then commits: what the commit
        printed."""
        for edit in edits:
            self.writes(planner, values["edit"], edit)
            self.runs(planner, self.tree_command("write", values["run"], values["edit"]))
        return self.runs(planner, self.tree_command("commit", values["run"]))

    def gave(self, printed: str) -> str:
        """The result a tree.py command names."""
        return printed.split("Give `")[1].split("`")[0]
