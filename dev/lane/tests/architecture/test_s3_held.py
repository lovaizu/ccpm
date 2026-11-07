"""S3 of dev/lane/architecture.md, a subagent with rules on a run, one test for each of its paths:
the proposal laid by `lay.py write` on a copy of `changelog`; the hooks' entries as laid called by
a double of Claude Code in the test's process, which starts each run from the main conversation,
makes each call a double of the subagent makes, and puts a held command to a double of the
person, a set answer, as its permission prompt does; and the adapters and the scripts the steps
name run real."""

import json
import os
import shutil
import subprocess
import unittest

import helpers
from helpers import testing

WRITER = testing.Run("changelog:writer", "w1")
LINTER = testing.Run("changelog:linter", "l1")
VERIFIER = testing.Run("changelog:verifier", "v1")
NOTER = testing.Run("changelog:noter", "n1")
# The findings noter answers, each `## Finding <n>` heading the item F<n> by its adapter.
REVIEW = (
    "# Review of the last notes\n\n## Finding 1\n\nx\n\n## Finding 2\n\ny\n\n## Finding 3\n\nz\n"
)
NOTES = {"version": "0.1.0", "entries": ["Added: notes are kept as Markdown files."]}
# How a call that cannot be checked ends, telling the subagent and the operator.
ASKED = "Go on with the rest of your work meanwhile."


def bash(command: str) -> tuple[str, dict]:
    """A Bash call of the command."""
    return "Bash", {"command": command, "description": "d"}


class TestWriterRun(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay(self.trial_proposal("changelog.json"))

    def commits(self) -> int:
        """The commits in the project."""
        done = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True, check=True
        )
        return int(done.stdout)

    def test_each_call_its_lanes_allow_goes_through_and_is_kept(self):
        # Given: the README's lanes laid in writer, and the main conversation starting it
        started = self.claude.start(None, WRITER, "Write the entries.")
        # When: writer reads CHANGELOG.md, runs git log --oneline, writes CHANGELOG.md and ends
        made = [
            self.claude.call(WRITER, "Read", {"file_path": "CHANGELOG.md"}),
            self.claude.call(WRITER, *bash("git log --oneline")),
            self.claude.call(WRITER, "Write", {"file_path": "CHANGELOG.md", "content": "x\n"}),
        ]
        ended = self.claude.stop(WRITER)
        # Then: each call is made with nothing said, and writer ends
        self.assertEqual(started.context, [])
        self.assertEqual([(t.made, t.said) for t in made], [(True, {})] * 3)
        self.assertEqual((ended.made, ended.said), (True, {}))
        # And: the hooks kept writer's start, the prompt its start came back with, each call as it
        # came back, and its end
        kinds = [(e["kind"], e.get("tool") or e.get("text")) for e in self.kept(WRITER)]
        calls = [("call", "Read"), ("call", "Bash"), ("call", "Write")]
        given = ("given", "Write the entries.")
        self.assertEqual(kinds, [("start", None), given, *calls, ("end", None)])

    def test_git_commit_is_stopped_with_its_sentence(self):
        # Given: the README's lanes laid in writer, started by the main conversation
        self.claude.start(None, WRITER, "Write the entries and commit them.")
        before = self.commits()
        # When: writer runs git commit
        told = self.claude.call(WRITER, *bash("git commit -am 'Add the entries'"))
        # Then: it is denied with run_only's sentence and the command it may run, and no commit
        # is made
        said = (
            "changelog: Run only `git log --oneline`.\n"
            "The commands you may run, each word for word: `git log --oneline`."
        )
        self.assertEqual((told.made, told.decision(), told.reason()), (False, "deny", said))
        self.assertEqual(self.commits(), before)

    def test_a_start_of_a_subagent_of_the_plugin_from_writer_is_stopped(self):
        # Given: the README's lanes laid in writer, started by the main conversation
        self.claude.start(None, WRITER, "Write the entries, and have them reviewed.")
        # When: writer starts reviewer itself
        reviewer = testing.Run("changelog:reviewer", "r1")
        told = self.claude.start(WRITER, reviewer, "Review the entries.")
        # Then: the start is denied with the main conversation alone starting one, and reviewer
        # never starts
        said = told.said["hookSpecificOutput"]
        self.assertFalse(told.made)
        self.assertEqual(said["permissionDecision"], "deny")
        reason = f"changelog: {helpers.guard.MAIN_STARTS}"
        self.assertEqual(said["permissionDecisionReason"], reason)

    def test_an_event_that_cannot_be_read_is_stopped_and_the_operator_told(self):
        # Given: the README's lanes laid in writer, started by the main conversation
        self.claude.start(None, WRITER, "Write the entries.")
        # When: writer's call reaches the hook as an event with no tool_input
        event = {**self.claude.common("PreToolUse", WRITER), "tool_name": "Bash"}
        said = self.claude.send({**event, "tool_use_id": "toolu_9"})
        # Then: it is denied, saying why and that Claude Code must be updated, the operator told
        told = testing.Told(False, said, [])
        self.assertEqual(told.decision(), "deny")
        self.assertTrue(
            told.reason().startswith("changelog: lane cannot check the lanes of writer")
        )
        self.assertIn("`claude update`", told.reason())
        self.assertEqual(told.operator(), told.reason())


class TestValueCommand(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay(self.trial_proposal("value_command.json"))
        self.write("notes v2.json", json.dumps(NOTES))
        self.check = f"python3 {self.plugin}/scripts/check.py"
        self.may = (
            "changelog: Run only `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py {notes}`.\n"
            f"The commands you may run, each word for word: `{self.check} 'notes v2.json'`."
        )

    def test_a_command_with_the_runs_own_value_as_one_word_goes_through(self):
        # Given: linter run_only on check.py {notes}, started with `notes v2.json` as its notes
        self.claude.start(None, LINTER, '{"notes": "notes v2.json"}\nCheck the notes.')
        # When: linter runs the check of its notes, the name in quotes as one word
        told = self.claude.call(LINTER, *bash(f"{self.check} 'notes v2.json'"))
        # Then: it goes through with nothing said, and the check is made
        self.assertEqual((told.made, told.said), (True, {}))
        self.assertEqual(self.kept(LINTER)[-1]["input"]["command"], f"{self.check} 'notes v2.json'")

    def test_a_command_with_another_value_or_its_value_as_two_words_is_stopped(self):
        for command in (f"{self.check} old.json", f"{self.check} notes v2.json"):
            with self.subTest(command=command):
                # Given: linter started with `notes v2.json` as its notes
                self.claude.start(None, LINTER, '{"notes": "notes v2.json"}\nCheck the notes.')
                # When: linter runs the check of another file, or of its own unquoted
                told = self.claude.call(LINTER, *bash(command))
                # Then: it is denied with run_only's sentence and the command it may run, its
                # value put in
                self.assertEqual((told.made, told.reason()), (False, self.may))

    def test_a_value_not_given_stops_the_call_as_one_that_cannot_be_checked(self):
        # Given: linter run_only on check.py {notes}, started with no notes
        self.claude.start(None, LINTER, "Check the notes.")
        # When: linter runs the check
        told = self.claude.call(LINTER, *bash(f"{self.check} 'notes v2.json'"))
        # Then: it is denied as a call that cannot be checked, whoever starts linter told to give
        # it notes, and the operator told too
        self.assertEqual((told.made, told.decision()), (False, "deny"))
        self.assertIn("`{notes}` was given no value", told.reason())
        self.assertIn("whoever starts linter must give it `notes`", told.reason())
        self.assertEqual(told.operator(), told.reason())

    def test_a_call_before_the_runs_prompt_is_kept_is_stopped_as_one_that_cannot_be_checked(self):
        # Given: linter run_only on check.py {notes}
        early: list[testing.Told] = []
        # When: linter runs its check after it started and before its start comes back
        command = f"{self.check} 'notes v2.json'"
        self.claude.start(
            None,
            LINTER,
            '{"notes": "notes v2.json"}\nCheck the notes.',
            lambda: early.append(self.claude.call(LINTER, *bash(command))),
        )
        # Then: after the wait it is denied as a call that cannot be checked, whoever starts
        # linter told to start it with the Agent tool, and the operator told too
        (told,) = early
        self.assertEqual((told.made, told.decision()), (False, "deny"))
        self.assertIn("gave back no ID of its run within 3 seconds", told.reason())
        self.assertIn("whoever starts linter must start it with the Agent tool", told.reason())
        self.assertTrue(told.reason().endswith(ASKED))
        self.assertEqual(told.operator(), told.reason())


class TestTwoRunsAtOnce(helpers.RunTest):
    def test_two_runs_at_once_are_each_held_to_their_own_value(self):
        # Given: drafter writing only {work}, two runs of it started at once by the main
        # conversation, the second before the first makes a call, given a.md and b.md
        self.lay(self.trial_proposal("at_once.json"))
        runs = {
            "a.md": testing.Run("changelog:drafter", "d1"),
            "b.md": testing.Run("changelog:drafter", "d2"),
        }
        for work, run in runs.items():
            self.claude.start(None, run, f'{{"work": "{work}"}}\nWrite the entries.')
        # When: each writes its own work and the other's
        told = {
            (work, other): self.claude.call(run, "Write", {"file_path": other, "content": "x\n"})
            for work, run in runs.items()
            for other in runs
        }
        # Then: each write of its own work goes through, and each of the other's is stopped with
        # write_only's sentence
        said = "changelog: Write only `{work}`."
        for (work, other), t in told.items():
            with self.subTest(work=work, other=other):
                own = work == other
                self.assertEqual((t.made, t.reason()), (own, "" if own else said))


class TestDependencyCommand(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        manifest = os.path.join(self.plugin, ".claude-plugin", "plugin.json")
        declared = {**self.read_json(manifest), "dependencies": ["checker"]}
        self.write_json(manifest, declared)
        self.lay(self.trial_proposal("dependency.json"))
        # checker installed in a folder of its own, as Claude Code's cache holds a plugin.
        self.installed = os.path.join(self.base, "cache", "checker", "0.1.0")
        shutil.copytree(os.path.join(helpers.TRIALS, "checker"), self.installed)
        self.claude.start(None, VERIFIER, "Check CHANGELOG.md by checker's skill.")
        self.said = (
            "changelog: Run only `python3 ${dependency:checker}/scripts/check.py CHANGELOG.md`."
        )

    def test_a_dependencys_command_by_its_folder_goes_through(self):
        # Given: verifier run_only on checker's command, checker declared and installed
        # When: verifier runs the command its skill gives, by checker's folder
        told = self.claude.call(
            VERIFIER, *bash(f"python3 {self.installed}/scripts/check.py CHANGELOG.md")
        )
        # Then: it goes through with nothing said, and the check is made
        self.assertEqual((told.made, told.said), (True, {}))

    def test_a_dependencys_command_by_a_folder_with_no_manifest_or_in_other_words_is_stopped(self):
        vendor = os.path.join(self.repo, "vendor", "checker")
        shutil.copytree(os.path.join(self.installed, "scripts"), os.path.join(vendor, "scripts"))
        for command in (
            f"python3 {vendor}/scripts/check.py CHANGELOG.md",
            f"python3 {self.installed}/scripts/check.py CHANGELOG.md --all",
        ):
            with self.subTest(command=command):
                # Given: a copy of checker's script in a folder that holds no manifest
                # When: verifier runs the command by that copy, or by checker's folder in other
                # words
                told = self.claude.call(VERIFIER, *bash(command))
                # Then: it is denied with run_only's sentence
                self.assertFalse(told.made)
                self.assertTrue(told.reason().startswith(self.said + "\n"), told.reason())


class TestAdapterRun(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay(self.trial_proposal("lanes.json"), ("items-findings",))
        self.write("review.md", REVIEW)
        self.gives = f"python3 {self.plugin}/hooks/lane/result.py noter done"
        self.check = f"python3 {self.plugin}/scripts/check.py notes.json"
        self.part = self.claude.start(None, NOTER, '{"work": "notes.json"}\nWrite the notes.')

    def work(self, answers: str) -> list[testing.Told]:
        """noter's work by its steps, each read, write and check its lanes allow, review.md's
        findings answered as given."""
        return [
            self.claude.call(NOTER, "Read", {"file_path": "CHANGELOG.md"}),
            self.claude.call(NOTER, "Read", {"file_path": "review.md"}),
            self.claude.call(
                NOTER, "Write", {"file_path": "notes.json", "content": json.dumps(NOTES)}
            ),
            self.claude.call(NOTER, *bash(self.check)),
            self.claude.call(NOTER, "Write", {"file_path": "answers.md", "content": answers}),
        ]

    def test_noter_given_its_part_gives_its_result_with_every_item_read_through_its_adapter(self):
        # Given: noter's lanes of every type checked as a call is made or at its end, review.md
        # read through the items adapter, and noter started with notes.json as its work
        # When: noter does its work, answering each finding, and runs its result command
        made = self.work("F1: done\nF2: done\nF3: done\n")
        gave = self.claude.call(NOTER, *bash(self.gives))
        ended = self.claude.stop(NOTER)
        # Then: it was given its part whole as it started, the plugin's folder put in
        with open(os.path.join(self.plugin, "domain", "noter.md"), encoding="utf-8") as f:
            part = f.read().replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)
        self.assertEqual(self.part.context, [part])
        # And: each call went through, the result script exited 0, the result was kept, and noter
        # ended
        self.assertEqual([(t.made, t.said) for t in [*made, gave]], [(True, {})] * 6)
        self.assertIn({"kind": "result", "on": "done"}, self.kept(NOTER))
        self.assertTrue(ended.made)

    def test_a_result_with_an_item_unanswered_is_stopped_with_what_is_missing(self):
        # Given: noter's lanes laid, review.md read through the items adapter
        # When: noter does its work answering F1 and F2 alone, and runs its result command
        self.work("F1: done\nF2: done\n")
        told = self.claude.call(NOTER, *bash(self.gives))
        # Then: it is denied with every_item's sentence and the item unanswered
        said = "changelog: Answer every item of `review.md`.\nF3 of `review.md` unanswered"
        self.assertEqual((told.made, told.reason()), (False, said))

    def test_an_adapter_that_fails_stops_the_result_as_one_that_cannot_be_checked(self):
        # Given: noter's items adapter, as laid in the plugin, failing
        adapter = os.path.join(self.plugin, "hooks", "adapters", "items-findings.py")
        self.write(adapter, "import sys\nsys.exit('no findings read')\n")
        # When: noter does its work and runs its result command
        self.work("F1: done\nF2: done\nF3: done\n")
        told = self.claude.call(NOTER, *bash(self.gives))
        # Then: it is denied as a call that cannot be checked, naming the adapter's failure and
        # who must fix it, and the operator is told too
        self.assertEqual((told.made, told.decision()), (False, "deny"))
        self.assertIn("the adapter hooks/adapters/items-findings.py exited 1", told.reason())
        self.assertIn("the maker of changelog must fix its adapter", told.reason())
        self.assertEqual(told.operator(), told.reason())


ADD = "git add CHANGELOG.md"
SAID = f"changelog: Run `{ADD}` only with the person's approval."


class TestSteps(helpers.RunTest):
    """steps.json: writer's step 2 held by run_step and step 3 by write_step, and the steps of its
    intents read at the steps port by the tests' own adapter, from changelog's
    domain/practices.json, as the sequence's branches of a trace before an earlier one's and of
    steps read through an adapter draw."""

    def setUp(self) -> None:
        super().setUp()
        self.lay(self.trial_proposal("steps.json"), ("steps-practices",))

    def write_entries(self) -> testing.Told:
        """writer's write of CHANGELOG.md."""
        return self.claude.call(WRITER, "Write", {"file_path": "CHANGELOG.md", "content": "x\n"})

    def test_a_trace_before_an_earlier_steps_is_stopped_with_the_step_due(self):
        # Given: writer started with no intent
        self.claude.start(None, WRITER, "{}")
        # When: it writes CHANGELOG.md before it runs git log --oneline, then runs it and writes
        # again
        early = self.write_entries()
        ran = self.claude.call(WRITER, *bash("git log --oneline"))
        later = self.write_entries()
        # Then: the first write is denied with step 2 and what of it is missing, and the run and
        # the second write go through
        said = (
            "changelog: Read the commits since then with `git log --oneline`. Run `git log"
            " --oneline`.\n`git log --oneline` not run"
        )
        self.assertEqual((early.made, early.reason()), (False, said))
        self.assertTrue(ran.made and later.made)

    def test_the_steps_of_an_intent_read_through_the_adapter_are_held_in_their_order(self):
        # Given: writer started on Q2, whose steps read CHANGELOG.md whole, then run git status
        self.claude.start(None, WRITER, '{"intents": ["Q2"]}')
        # When: it runs git status first, then reads CHANGELOG.md and runs git status again
        early = self.claude.call(WRITER, *bash("git status"))
        read = self.claude.call(WRITER, "Read", {"file_path": "CHANGELOG.md"})
        later = self.claude.call(WRITER, *bash("git status"))
        # Then: the first run is denied with Q2's first step, which no step of writer's own
        # says, and its trace's sentence, and the read and the second run go through
        said = (
            "changelog: Read the file whole. Read `CHANGELOG.md` to its end.\n`CHANGELOG.md`"
            " unread from line 1"
        )
        self.assertEqual((early.made, early.reason()), (False, said))
        self.assertTrue(read.made and later.made)


class TestHeldCommand(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        given = self.trial_proposal("changelog.json")
        held = {"lane": "hold", "takes": [ADD]}
        given["subagents"][0]["steps"][1]["lanes"].append(held)
        self.lay(given)
        self.claude.start(None, WRITER, "Write the entries and stage them.")
        self.claude.call(WRITER, "Write", {"file_path": "CHANGELOG.md", "content": "x\n"})

    def staged(self) -> str:
        """The files staged in the project."""
        done = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        return done.stdout

    def held(self, yes: bool) -> testing.Told:
        """writer's run of the held command, the person answering yes or no."""
        self.claude.answers = [yes]
        return self.claude.call(WRITER, "Bash", {"command": ADD, "description": "d"})

    def test_the_person_says_yes_and_the_command_runs(self):
        # Given: writer holding git add CHANGELOG.md, CHANGELOG.md written
        # When: writer runs it, and the person says yes
        told = self.held(True)
        # Then: it was asked of the person with hold's sentence, and it ran
        self.assertEqual((told.decision(), told.reason(), told.made), ("ask", SAID, True))
        self.assertEqual(self.staged(), "CHANGELOG.md\n")
        self.assertEqual(self.claude.answers, [])

    def test_the_person_says_no_and_the_command_does_not_run(self):
        # Given: writer holding git add CHANGELOG.md, CHANGELOG.md written
        # When: writer runs it, and the person says no
        told = self.held(False)
        # Then: it was asked of the person with hold's sentence, and it did not run
        self.assertEqual((told.decision(), told.reason(), told.made), ("ask", SAID, False))
        self.assertEqual(self.staged(), "")


if __name__ == "__main__":
    unittest.main()
