"""What Turn's tests stand on beside what every plugin's tests do: Turn's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; a small best
practice of the kind `note`, kept as the repository's own, for a test to change; and a test whose
folder is the top of a repository, with that best practice laid and a Call written."""

from __future__ import annotations

import copy
import json
import os
import sys
from typing import Any

TURN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "turn")
)
DOMAIN = os.path.join(TURN, "core", "domain")
SCRIPTS = os.path.join(TURN, "scripts")
sys.path[:0] = [DOMAIN, SCRIPTS, os.path.join(TURN, "..", "..", "dev", "lane")]

import files
import phases
import plan
import practices
import rounds
import runs
import testing
import throwaway
import tree

__all__ = ["files", "phases", "plan", "practices", "rounds", "runs", "testing", "throwaway", "tree"]

# A best practice of the kind `note`: two parts, three questions, the last of the whole.
PRACTICE: dict[str, Any] = {
    "goal": "The reader acts on the note.",
    "parts": [
        {"id": "summary", "what": "One sentence."},
        {"id": "steps", "what": "The steps."},
    ],
    "intents": [
        {"id": "Q1", "about": "summary", "what": "Can the reader say what it asks?"},
        {"id": "Q2", "about": "steps", "what": "Can the reader take each step?"},
        {"id": "Q3", "about": "the whole", "what": "Does each answer come when needed?"},
    ],
    "practices": [{"intent": f"Q{n}", "thinking": "Think.", "steps": []} for n in (1, 2, 3)],
}
# Where a run's folder lies, and the repository's best practice of `note`.
RUN = os.path.join(".turn", "20261103-tidy-note")
NOTE = os.path.join(".turn", "best-practices", "note", "best-practice.json")
VERIFICATION = os.path.join(RUN, "verification")
# A Call of the kind `note`, as the planner writes it.
CALL: dict[str, Any] = {
    "request": "a note on tidy",
    "kind": "note",
    "reading": "refactor-doc",
    "goal": "Someone new to tidy sorts their folder with it.",
}
# A decision the calling AI settled, as Calling Turn gives it.
SETTLED: dict[str, Any] = {
    "id": "D1",
    "what": "Which run the steps show",
    "contributes_to": [],
    "builds_on": [],
    "decided": "tidy --dry-run, then tidy",
    "settled_by": "maker",
    "grounds": ["the person, 2026-11-03"],
}


def practice() -> dict[str, Any]:
    """A copy of the best practice of `note`, for a test to change."""
    return copy.deepcopy(PRACTICE)


def call(**given: Any) -> dict[str, Any]:
    """A copy of the Call, each field given put in its place."""
    return {**copy.deepcopy(CALL), **given}


class RepositoryTest(testing.FolderTest):
    """Each test stands at the top of a repository, `base`, which holds the best practice of
    `note`, and may write a Call into the run's folder."""

    def setUp(self) -> None:
        super().setUp()
        self.write_json(NOTE, PRACTICE)

    def calls(self, data: dict[str, Any] | None = None) -> None:
        """Writes the Call, `data` or the one of `note`, into the run's folder."""
        self.write_json(os.path.join(RUN, runs.CALL), CALL if data is None else data)

    def run_data(self) -> dict[str, Any]:
        """The Run on disk."""
        return self.read_json(os.path.join(RUN, runs.RUN))

    def started(self, data: dict[str, Any] | None = None) -> str:
        """A run begun from the Call, `data` or the one of `note`: its Request."""
        self.calls(data)
        return runs.start(RUN)

    def lay_run(self, works: list[dict[str, Any]]) -> None:
        """Writes the Run of the works, the Call of `note` beside it."""
        self.calls()
        self.write_json(os.path.join(RUN, runs.RUN), {"works": works})


def work(**given: Any) -> dict[str, Any]:
    """A work of `note`, in its rounds, lying at NOTES.md, each field given put in its place."""
    made = {
        "kind": "note",
        "practice": NOTE,
        "reading": "refactor-doc",
        "folder": RUN,
        "paths": ["NOTES.md"],
        "commands": [],
        "files": [],
        "at": "rounds",
    }
    made.update(given)
    return made


def line(data: dict[str, Any]) -> str:
    """The data as one JSON line, as Turn's scripts print run values."""
    return json.dumps(data, ensure_ascii=False)


# A best practice of how a note reads, of one question about the whole.
READING = {
    "goal": "The reader takes in what it says.",
    "intents": [{"id": "Q1", "about": "the whole", "what": "Is each fact said once?"}],
}
# The design of the note: D1 serves note/Q1 and note/Q3, D2 serves note/Q2, D3 serves D2.
TREE = {
    "goal": {"what": "A newcomer sorts their folder.", "grounds": ["the person"]},
    "questions": [{"id": f"note/Q{n}", "what": f"Q{n}?"} for n in (1, 2, 3)],
    "decisions": [
        {
            "id": f"D{n}",
            "what": f"D{n}",
            "contributes_to": serves,
            "builds_on": on,
            "decided": None,
            "settled_by": None,
            "grounds": [],
        }
        for n, serves, on in (
            (1, ["note/Q1", "note/Q3"], []),
            (2, ["note/Q2"], []),
            (3, ["D2"], ["D2"]),
        )
    ],
}
NOTES = "# tidy\n\ntidy sorts a folder.\n\n## Steps\n\nRun tidy --dry-run.\n"


def met(*questions, line="NOTES.md:1"):
    """Answers that meet each question, by the line given."""
    return {"met": [{"question": q, "lines": [line]} for q in questions], "not_met": []}


def short(*questions):
    """Answers that meet none of the questions."""
    return {"met": [], "not_met": [{"question": q, "lacks": f"{q} lacks"} for q in questions]}


class RoundsTest(RepositoryTest):
    """A run of one work of `note`, in its rounds, its design, its Standards and the note laid."""

    def setUp(self) -> None:
        super().setUp()
        self.lays()

    def lays(self) -> None:
        """Lays the run, its design, its Standards and the note where the test stands, as a
        property-based test does again for each of its examples."""
        self.write_json(NOTE, PRACTICE)
        self.lay_run([work()])
        tree.save(os.path.join(RUN, runs.DESIGN), TREE)
        self.write_json(os.path.join(RUN, "standard.json"), practices.standard(PRACTICE))
        self.write_json(os.path.join(RUN, "reading-standard.json"), READING)
        self.write("NOTES.md", NOTES)

    def answers(self, name, data):
        """Writes the Answers of the name into the round's folder."""
        self.write_json(os.path.join(VERIFICATION, name), data)

    def round(self):
        """The Round on disk."""
        return self.read_json(os.path.join(VERIFICATION, "round.json"))

    def content_round(self, *groups):
        """A content round settled, each group's Answers given in order, the generator's meeting
        every question."""
        phases.settle(RUN)
        self.answers("generator.json", met("note/Q1", "note/Q2", "note/Q3"))
        for n, data in enumerate(groups, 1):
            self.answers(f"G{n}.json", data)

    def finished(self):
        """A content round and then a reading round, each meeting every question."""
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        phases.settle(RUN)
        self.answers("G1.json", met("refactor-doc/Q1"))


# What the architecture tests stand on: Pin installed beside Turn, the guards' modules as Turn takes
# them through its link to Lane's code, and the subject `tidy` the ux trials work on, kept in
# ux/tidy/ for them too, each file by its path in it.
PIN = os.path.join(os.path.dirname(TURN), "pin")
hook, schema, guard, result = testing.lane_code(TURN, "hook", "schema", "guard", "result")
SUBJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ux", "tidy")
TIDY: dict[str, str] = {}
for _folder, _, _names in os.walk(SUBJECT):
    for _name in [] if "__pycache__" in _folder else _names:
        with open(os.path.join(_folder, _name), encoding="utf-8") as _f:
            TIDY[os.path.relpath(os.path.join(_folder, _name), SUBJECT)] = _f.read()
# The line a point for the person begins with, and the line an answer begins with, as up's part
# and the pinner's give them.
FOR_THE_PERSON = "For the person:"
ANSWERED = "The person's answer, word for word:"
PINNER = testing.Run("pin:pinner", "n1")
# The calling AI of S3 and S4, a subagent of a plugin that has Turn make a work.
CALLER = testing.Run("caller:caller", "c1")
# The run's folder up picks for "a README for tidy" on the day of the tests.
TIDY_RUN = os.path.join(".turn", "20261104-tidy-readme")
README_PRACTICE = runs.read_practice(runs.practice_in(runs.OWN, "readme"))


def entry_of(root: str, *path: str) -> str:
    """The text of a plugin's file, at its path in the plugin's folder, as the guard gives it to
    the role it is the part of, the plugin's folder put in."""
    with open(os.path.join(root, *path), encoding="utf-8") as f:
        return f.read().replace("${CLAUDE_PLUGIN_ROOT}", root)


def tidy_tree(practice: dict[str, Any] | None = None, **changed: dict[str, Any]) -> dict[str, Any]:
    """The design of tidy's README by the best practice given, Turn's own where none is, confirmed:
    who reads it, the walkthrough's run, the person's, and Python 3.9, found in setup.cfg, the two
    serving the questions of the walkthrough and of what tidy needs, Turn's Q5 and Q6, or the
    small one's Q2; each decision of a name given changed so."""
    asked = runs.questions("readme", practice or README_PRACTICE)
    run_q, needs_q = ("readme/Q2", "readme/Q2") if practice else ("readme/Q5", "readme/Q6")
    rest = [q["id"] for q in asked if q["id"] not in (run_q, needs_q)]
    decisions = [
        {
            "id": "D1",
            "what": "Who reads the README, and what they do with it",
            "contributes_to": rest,
            "builds_on": [],
            "decided": "someone with a cluttered Downloads folder, who installs tidy and sorts it",
            "settled_by": "reasoning",
            "grounds": ["the goal"],
        },
        {
            "id": "D2",
            "what": "Which run the walkthrough shows",
            "contributes_to": [run_q],
            "builds_on": ["D1"],
            "decided": "tidy --dry-run, then tidy, on five files",
            "settled_by": "user",
            "grounds": ["the person: yes, 2026-11-04"],
        },
        {
            "id": "D3",
            "what": "What tidy needs to run",
            "contributes_to": [needs_q],
            "builds_on": [],
            "decided": "Python 3.9 or later",
            "settled_by": "research",
            "grounds": [
                'setup.cfg:9 "python_requires = >=3.9"',
                "the person confirmed, 2026-11-04",
            ],
        },
    ]
    for d in decisions:
        d.update(changed.get(str(d["id"]), {}))
    return {
        "goal": {
            "what": "Someone with a cluttered Downloads folder learns what tidy does, installs it"
            " and sorts their folder.",
            "grounds": ["the person: yes, 2026-11-04"],
        },
        "questions": asked,
        "decisions": decisions,
    }


# What the planner reads out of tidy's design: where the README lies, what its user runs, and the
# files those commands need under the home.
READ_OUT = {
    "paths": ["README.md"],
    "commands": ["python3 -m tidy --dry-run ~/Downloads", "python3 -m tidy ~/Downloads"],
    "files": [f"Downloads/{n}" for n in ("a.jpg", "b.pdf", "c.zip", "d.mp3", "notes")],
}
README = "# tidy\n\ntidy sorts your Downloads folder into folders by type.\n"


def handed(event: dict[str, Any]) -> str:
    """What is wrong with the event as Claude Code hands it, by the guard's own check of the fields
    the hooks reference documents, the subagent's filled where the main conversation sent it, and an
    Agent call's tool_response held to what the guard reads of it; "" where nothing is."""
    named = event["hook_event_name"]
    wrong = hook.event_wrong({"agent_id": "main", "agent_type": "", **event}, named)
    if not wrong and named == "PostToolUse" and event["tool_name"] == "Agent":
        out = schema.held(guard.BACK, event["tool_response"])
        wrong = out.told() if out is not None else ""
    return wrong


class Claude(testing.ClaudeCode):
    """The double of Claude Code, which also keeps what the last Bash call printed, or its error, as
    the call's result hands it to the role that made it."""

    printed = ""

    def made(self, tool: str, given: dict[str, Any]) -> tuple[Any, str | None]:
        response, error = super().made(tool, given)
        if tool == "Bash":
            self.printed = error if error is not None else response["stdout"]
        return response, error


class TurnTest(testing.FolderTest):
    """A test of a path of Turn's Sequences, in tidy's repository `repo` in `base`: Turn's guard and
    Pin's run real, by each plugin's hook entries on its Rules laid, through a double of Claude
    Code working in `repo`, whose hooks keep their records in `base` as the system's temporary
    folder; plan.py, rounds.py, throwaway.py and Pin's check.py run real, by the commands the rules
    name. Doubles stand in for up, the planner, the pinner, the generator, the evaluator, the
    starter, `starter`, the main conversation where None, and the person, set answers."""

    starter: testing.Run | None = None
    folder = TIDY_RUN

    def setUp(self) -> None:
        super().setUp()
        self.repo = os.path.join(self.base, "tidy")
        for name, text in TIDY.items():
            self.write(os.path.join(self.repo, name), text)
        self.env = {**os.environ, "TMPDIR": self.base}
        self.claude = Claude(TURN, self.repo, self.env, others=(PIN,), check=handed)
        # What reached the person, in order; each role's last message, by its run's ID; and the
        # runs started, for each a new ID.
        self.heard: list[str] = []
        self.last: dict[str, str] = {}
        self.made = 0

    def at(self, *path: str) -> str:
        """The path in the repository."""
        return os.path.join(self.repo, *path)

    def new(self, role: str) -> testing.Run:
        """A new run of Turn's role."""
        self.made += 1
        return testing.Run(f"turn:{role}", f"{role[0]}{self.made}")

    def begins(self, request: str) -> list[str]:
        """The starter begins a run of the skill up with the request: the person by typing
        `/turn:up`, or the calling AI, the main conversation, by its Skill call: what the main
        conversation, the orchestrator, is told as the run begins."""
        if self.starter is None:
            return self.claude.typed("turn:up")
        called = self.claude.skill("turn:up")
        self.assertTrue(called.made, called.said)
        return called.context

    def starts(self, run: testing.Run, prompt: str) -> testing.Told:
        """The orchestrator starts the run with the prompt, and ends its turn to wait for it; fails
        the test where the start or the end is not let through."""
        told = self.claude.start(None, run, prompt)
        self.assertTrue(told.made, told.said)
        self.assertTrue(self.claude.end_turn().made)
        return told

    def does(self, run: testing.Run | None, tool: str, **given: Any) -> testing.Told:
        """The run's call of the tool with its input."""
        return self.claude.call(run, tool, given)

    def runs(self, run: testing.Run, command: str) -> str:
        """The run runs the command with Bash, which goes through: what it printed."""
        told = self.does(run, "Bash", command=command, description="d")
        self.assertTrue(told.made, told.said)
        return self.claude.printed

    def writes(self, run: testing.Run, path: str, text: str) -> testing.Told:
        """The run writes the text at the path with Write, which goes through."""
        told = self.does(run, "Write", file_path=path, content=text)
        self.assertTrue(told.made, told.said)
        return told

    def gives(self, run: testing.Run, on: str) -> None:
        """The run gives its result by the command its last step names, its plugin's result script
        on a result that script takes, which goes through."""
        root = PIN if run.kind.startswith("pin:") else TURN
        name = run.kind.split(":")[1]
        self.assertEqual(result.said([name, on], root), "")
        self.runs(run, f"python3 {root}/hooks/lane/result.py {name} {on}")

    def ends(self, run: testing.Run, message: str) -> list[str]:
        """The run ends with the message, let end, and its end reaches the orchestrator: what the
        orchestrator is told."""
        ended = self.claude.stop(run)
        self.assertTrue(ended.made, ended.said)
        self.last[run.agent_id] = message
        return lines_of(self.claude.notify(run))

    def passes(self, run: testing.Run) -> str:
        """The orchestrator puts the run's last message to the person as given, and ends its turn to
        wait: what the person heard."""
        self.assertTrue(self.claude.end_turn().made)
        message = self.last[run.agent_id]
        heard = message.split("\n", 1)[1] if message.startswith(FOR_THE_PERSON) else message
        self.heard.append(heard)
        return heard

    def answers(self, words: str, run: testing.Run) -> None:
        """The person answers, typing their words where the person started Turn, or the calling AI
        has them; the orchestrator resumes the run with them under the Answer's line, which Claude
        Code starts again, and ends its turn to wait."""
        message = f"{ANSWERED}\n{words}"
        if self.starter is None:
            self.claude.prompted(words)
        passed = self.does(None, "SendMessage", to=run.agent_id, message=message)
        self.assertTrue(passed.made, passed.said)
        self.claude.started(run)
        self.assertTrue(self.claude.end_turn().made)

    def plans(self, planner: testing.Run, command: str) -> str:
        """The planner runs plan.py's command on the run's folder: what it printed."""
        return self.runs(planner, f"python3 {TURN}/scripts/plan.py {command} {self.folder}")

    def calls(self, planner: testing.Run, **given: Any) -> None:
        """The planner writes the Call of tidy's README into the run's folder, each field given put
        in its place."""
        data = {
            "request": "a README for tidy",
            "kind": "readme",
            "reading": "refactor-doc",
            "goal": "Someone with a cluttered Downloads folder learns what tidy does and sorts it.",
            **given,
        }
        self.writes(planner, os.path.join(self.folder, runs.CALL), json.dumps(data))

    def lays(self, at: str, design: dict[str, Any], call: dict[str, Any] | None = None, **out: Any):
        """A run stopped with its work at the place given, its design tree the tree and its paths,
        commands and files as given, as plan.py left it, begun from the Call given or tidy's
        README's."""
        given = {"request": "a README for tidy", "kind": "readme", "reading": "refactor-doc"}
        self.write_json(self.at(self.folder, runs.CALL), call or {**given, "goal": "g"})
        here = os.getcwd()
        os.chdir(self.repo)
        try:
            runs.start(self.folder)
        finally:
            os.chdir(here)
        data = self.run_file()
        runs.current(data).update(at=at, **out)
        self.write_json(self.at(self.folder, runs.RUN), data)
        folder = runs.current(data)["folder"]
        tree.save(self.at(folder, runs.DESIGN), design)

    def run_file(self) -> dict[str, Any]:
        """The Run on disk."""
        return self.read_json(self.at(self.folder, runs.RUN))

    def begun(self, words: str, planner: testing.Run, **given: Any) -> str:
        """up starts the planner on the request; the planner finds no Run, writes the Call, begins
        the run, passes plan.py check, gives `handed` and ends with the Request: what up is told."""
        self.starts(planner, json.dumps({"run": self.folder}) + "\n" + words)
        self.assertIn("holds no Run yet", self.plans(planner, "check"))
        return self.hands_over(planner, **given)

    def hands_over(self, planner: testing.Run, **given: Any) -> str:
        """The planner writes the Call, each field given put in its place, begins the run, passes
        plan.py check, gives `handed` and ends with the Request, which up is told to start the
        pinner on: the Request."""
        self.calls(planner, **given)
        request = self.plans(planner, "start").split("\n", 1)[1].rstrip("\n")
        self.assertIn("holds.", self.plans(planner, "check"))
        self.gives(planner, "handed")
        self.assertEqual(self.ends(planner, request), [told("planner", "handed", "pin:pinner")])
        return request

    def changes(self, run: testing.Run, path: str, data: dict[str, Any]) -> None:
        """The run changes the design tree at the path to the data, as Pin's pinner may: it reads
        the file with Read and changes it with Edit, its whole text the old string, both of which
        go through."""
        self.assertTrue(self.does(run, "Read", file_path=path).made)
        with open(self.at(path), encoding="utf-8") as f:
            now = f.read()
        told = self.does(
            run, "Edit", file_path=path, old_string=now, new_string=tree.markdown(data)
        )
        self.assertTrue(told.made, told.said)

    def pin_checks(self, design: str) -> str:
        """The pinner runs Pin's check on the design tree, which holds: what it printed."""
        printed = self.runs(PINNER, f"python3 {PIN}/scripts/check.py {design}")
        self.assertIn("holds", printed)
        return printed

    def pinner_asks(self, design: str, tree: dict[str, Any], point: str) -> str:
        """The pinner writes the tree, which Pin's check passes, gives `asks` and ends with the
        point; up passes it on: what the person heard."""
        self.changes(PINNER, design, tree)
        self.pin_checks(design)
        self.gives(PINNER, "asks")
        reply = f"{FOR_THE_PERSON}\n{point}"
        self.assertEqual(self.ends(PINNER, reply), [asked("pin:pinner")])
        return self.passes(PINNER)

    def pinner_done(self, design: str, tree: dict[str, Any]) -> list[str]:
        """The pinner writes the confirmed tree, which Pin's check passes, gives `done` and ends
        with the design tree's path: what up is told."""
        self.changes(PINNER, design, tree)
        printed = self.pin_checks(design)
        self.gives(PINNER, "done")
        return self.ends(PINNER, f"{FOR_THE_PERSON}\nThe design is in {design}.\n{printed}")

    def reads_out(self, planner: testing.Run, design: str, out: dict[str, Any]) -> str:
        """The planner, started with the run's folder alone, reads the design whole, writes where
        the work lies and what its user runs into the Run, puts the work into its rounds and passes
        plan.py check, gives `ready` and ends with the generator's line: the line."""
        self.starts(planner, json.dumps({"run": self.folder}))
        self.assertIn("is with Pin", self.plans(planner, "check"))
        self.assertTrue(self.does(planner, "Read", file_path=design).made)
        data = self.run_file()
        runs.current(data).update(out)
        self.writes(planner, os.path.join(self.folder, runs.RUN), json.dumps(data))
        line = self.plans(planner, "ready").split("\n", 1)[1].rstrip("\n")
        self.assertIn("holds.", self.plans(planner, "check"))
        self.gives(planner, "ready")
        self.assertEqual(self.ends(planner, line), [told("planner", "ready", "turn:generator")])
        return line


class InRoundsTest(TurnTest):
    """A path of the rounds: a run of tidy's README stopped in its rounds, gone on from its folder,
    the planner giving `ready`, so up is told to start the generator with `line`."""

    def setUp(self) -> None:
        super().setUp()
        self.lays_rounds()
        self.begins(self.folder)
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}) + "\n" + self.folder)
        self.plans(planner, "check")
        self.line = self.plans(planner, "ready").split("\n", 1)[1].rstrip("\n")
        self.gives(planner, "ready")
        self.assertEqual(
            self.ends(planner, self.line), [told("planner", "ready", "turn:generator")]
        )

    def lays_rounds(self) -> None:
        """The run stopped in its rounds: tidy's README, its design confirmed and read out, by the
        repository's own best practice of a README, PRACTICE, which Turn takes over its own, so
        each round has a run of the evaluator for each of three questions."""
        self.write_json(self.at(runs.practice_in(runs.REPOSITORY, "readme")), PRACTICE)
        self.lays("rounds", tidy_tree(PRACTICE), **READ_OUT)

    def questions(self) -> list[str]:
        """The questions of the round on disk, in the order of its groups."""
        data = self.run_file()
        settled = phases.last(
            {**runs.current(data), "folder": self.at(runs.current(data)["folder"])}
        )
        assert settled is not None
        return [q for g in settled["groups"] for q in g["questions"]]

    def answered(self, questions: list[str], short: Any = (), opens: Any = ()) -> str:
        """Answers to the questions: each met by the work's first line, but those `short`, not
        met, and a point open on each of `opens`."""
        line = f"{runs.current(self.run_file())['paths'][0]}:1"
        data: dict[str, Any] = {
            "met": [{"question": q, "lines": [line]} for q in questions if q not in short],
            "not_met": [
                {"question": q, "lacks": f"the user lacks {q}"} for q in questions if q in short
            ],
        }
        mine = [q for q in questions if q in opens]
        if mine:
            data["open"] = [{"question": q, "what": f"what {q} needs changes"} for q in mine]
        return json.dumps(data)

    def generates(self, line: str, text: str = README, short: Any = (), opens: Any = ()):
        """up starts a run of the generator with the line, which settles the round, writes the work,
        reads it whole, runs its commands in a throwaway copy, answers each question and passes
        rounds.py check, gives the result it names and ends with the lines it printed: the round's
        phase, those lines, and what up is told."""
        generator = self.new("generator")
        self.starts(generator, line)
        values = json.loads(line)
        printed = self.runs(generator, f"python3 {TURN}/scripts/rounds.py round {self.folder}")
        phase = "content" if "of what the work says" in printed else "reading"
        for path in values["work"]:
            self.writes(generator, path, text)
            self.assertTrue(self.does(generator, "Read", file_path=path).made)
        shown = self.runs(generator, self.throwaway())
        self.assertEqual(shown.count("(exit 0)"), len(runs.current(self.run_file())["commands"]))
        self.writes(generator, values["answers"], self.answered(self.questions(), short, opens))
        out = self.runs(generator, self.check(values["answers"]))
        on = "open" if "Give `open`" in out else "made"
        ended = [said for said in out.split("\n")[1:] if said]
        self.gives(generator, on)
        return phase, ended, self.ends(generator, "\n".join(ended) or out)

    def throwaway(self) -> str:
        """The command a role runs the work's commands by."""
        return f"python3 {TURN}/scripts/throwaway.py {self.folder}"

    def check(self, answers: str) -> str:
        """The command a role checks its Answers by."""
        return f"python3 {TURN}/scripts/rounds.py check {self.folder} {answers}"

    def evaluates(self, lines: list[str], short: Any = (), opens: Any = (), none: int = 0):
        """The orchestrator starts a run of the evaluator for each line, all at once, and ends its
        turn; each run reads
        the Standard, use-and-answer.md and the work whole, runs its commands in a throwaway copy,
        answers its questions and passes rounds.py check, gives the result it names and ends with
        the line it printed, but the run numbered `none`, which ends with no result, kept going
        once; the orchestrator, told of each end, ends its turn to wait: what it was told after the
        last."""
        started = [self.new("evaluator") for _ in lines]
        for run, line in zip(started, lines):
            told_ = self.claude.start(None, run, line)
            self.assertTrue(told_.made, told_.said)
        self.assertTrue(self.claude.end_turn().made)
        after: list[str] = []
        for n, (run, line) in enumerate(zip(started, lines), 1):
            values = json.loads(line)
            for path in [
                values["standard"],
                f"{TURN}/core/domain/use-and-answer.md",
                *values["work"],
            ]:
                read = self.does(run, "Read", file_path=path)
                self.assertTrue(read.made, read.said)
            self.runs(run, self.throwaway())
            if n == none:
                kept = self.claude.stop(run)
                self.assertEqual((kept.made, kept.decision()), (False, "block"))
                self.assertTrue(self.claude.stop(run).made)
                after = lines_of(self.claude.notify(run))
            else:
                answers = self.answered(values["questions"], short, opens)
                self.writes(run, values["answers"], answers)
                out = self.runs(run, self.check(values["answers"]))
                on = out.split("Give `")[1].split("`")[0]
                self.gives(run, on)
                after = self.ends(run, out.rstrip("\n").split("\n")[-1])
            if n < len(lines):
                self.assertTrue(self.claude.end_turn().made)
        return after


def lines_of(context: list[str]) -> list[str]:
    """Lane's lines to up in the context the hooks added, each headed `turn:`, its part left out."""
    return [line for said in context for line in said.splitlines() if line.startswith("turn: ")]


def told(name: str, on: str, to: str = "") -> str:
    """What up is told once the subagent of the name gave the result: the start its route names, or
    none."""
    start = f"Start `{to}`." if to else "Start no more subagents."
    return f"turn: {name} gave `{on}`. {start}"


def asked(kind: str) -> str:
    """What up is told once the subagent of the type, as Claude Code names it, gave `asks`, whose
    route waits for the person: to put its point to them and resume it with their answer."""
    name = kind.removeprefix("turn:")
    return (
        f"turn: {name} gave `asks`. Put its point to the user, and resume `{kind}` with their"
        " answer by SendMessage."
    )
