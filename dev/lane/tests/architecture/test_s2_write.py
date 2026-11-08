"""S2 of dev/lane/architecture.md, `lay.py write`, one test for each of its paths: lay.py run as the
user runs it on the README's walkthrough, the proposal set as the user would write it, a double of
`claude` on PATH whose `plugin validate` gives a set answer, and lay.py and the files it lays
real."""

import json
import os
import sys
import unittest

import helpers


class TestWritten(helpers.WalkthroughTest):
    def test_the_proposal_without_an_adapter_is_written_as_the_walkthrough_shows(self):
        # Given: the walkthrough's plugin and proposal
        # When: lay.py write is run on the proposal
        done = self.lay_py("write")
        # Then: it prints what the walkthrough shows, the repository's folder put in, and exits 0
        said = helpers.shown(helpers.README_WROTE).replace("<the repository>", self.base)
        self.assertEqual((done.returncode, done.stdout), (0, said))
        # And: the skill and the subagents read as print showed them, and the checks, the rules
        # and the routes are written
        skill = os.path.join("changelog", "skills", "write", "SKILL.md")
        self.assertEqual(self.read(skill), helpers.SKILL_LAID)
        writer = os.path.join("changelog", "agents", "writer.md")
        self.assertEqual(self.read(writer), helpers.WRITER_LAID)
        reviewer = self.read(os.path.join("changelog", "agents", "reviewer.md"))
        self.assertTrue(reviewer.endswith(f" {helpers.END_REVIEWER}\n"), reviewer)
        hooks = self.read_json(os.path.join("changelog", "hooks", "hooks.json"))["hooks"]
        self.assertEqual(
            {e: hooks[e] for e in hooks if e != "PreToolUse"},
            {e: h for e, h in helpers.HOOKS["hooks"].items() if e != "PreToolUse"},
        )
        command = hooks["PreToolUse"][0]["hooks"][0]["command"]
        self.assertIn('"agent_type":"changelog:reviewer"', command)
        laid = {**helpers.RULES, "routes": json.loads(helpers.README_PROPOSAL)["routes"]}
        self.assertEqual(self.read_json(os.path.join("changelog", "hooks", "lanes.json")), laid)
        self.assertFalse(os.path.exists(helpers.README_PROPOSED))

    def test_the_proposal_with_an_adapter_is_written_with_it_and_removed_from_beside_it(self):
        # Given: the walkthrough's proposal with writer's values read by an adapter beside it
        beside = self.adapter()
        self.propose(lambda p: p["subagents"][0].update(adapter="hooks/adapters/values-w.py"))
        # When: lay.py write is run on it
        done = self.lay_py("write")
        # Then: the adapter lies in the plugin, and is gone from beside the proposal
        self.assertEqual(done.returncode, 0, done.stdout)
        written = os.path.join("changelog", "hooks", "adapters", "values-w.py")
        self.assertEqual(self.read(written), helpers.VALUES_ADAPTER)
        self.assertFalse(os.path.exists(beside))


class TestKept(helpers.WalkthroughTest):
    def test_a_proposal_that_cannot_be_laid_writes_nothing_and_exits_1(self):
        # Given: the walkthrough's proposal with a lane on a step writer does not have
        self.propose(lambda p: p["subagents"][0]["steps"][0].update(step=9))
        # When: lay.py write is run on it
        done = self.lay_py("write")
        # Then: it prints what is wrong, exits 1, and writes nothing, the proposal kept
        self.assertEqual(done.returncode, 1)
        self.assertTrue(done.stdout.startswith("lay.py: the proposal gives step 9"), done.stdout)
        self.assertEqual(
            self.read(os.path.join("changelog", "agents", "writer.md")), helpers.README_WRITER
        )
        self.assertFalse(os.path.exists(os.path.join("changelog", "hooks")))
        self.assertTrue(os.path.exists(helpers.README_PROPOSED))

    def test_a_plugin_claude_finds_malformed_keeps_the_proposal_and_exits_1(self):
        # Given: a claude whose plugin validate finds the plugin malformed
        self.write(os.path.join("bin", "claude"), "#!/bin/sh\necho '✘ Found 1 error'\nexit 1\n")
        # When: lay.py write is run on the proposal
        done = self.lay_py("write")
        # Then: it says what claude found and to run it again once fixed, keeps the proposal, and
        # exits 1
        said = (
            "lay.py: claude plugin validate found changelog malformed:\n✘ Found 1 error\n"
            f"fix what it names, then run `lay.py write {helpers.README_PROPOSED}` again.\n"
        )
        self.assertEqual((done.returncode, done.stdout), (1, said))
        self.assertTrue(os.path.exists(helpers.README_PROPOSED))

    def test_claude_missing_keeps_the_proposal_and_exits_1(self):
        # Given: no claude on PATH
        self.env["PATH"] = os.path.dirname(sys.executable)
        # When: lay.py write is run on the proposal
        done = self.lay_py("write")
        # Then: it says so, keeps the proposal, and exits 1
        self.assertEqual(
            (done.returncode, done.stdout),
            (1, "lay.py: claude is not on PATH; install Claude Code and run again.\n"),
        )
        self.assertTrue(os.path.exists(helpers.README_PROPOSED))


if __name__ == "__main__":
    unittest.main()
