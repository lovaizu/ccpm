"""rn's Stop hook: when the conductor ends its turn, the record keeps its form and every commit is
pushed."""
import unittest

from harness import Session, sh, SDIR, STEERING, PROPOSE


class Stop(Session):
    def test_unpushed_commit_blocks_the_end(self):
        # Given a sign-off commit not pushed
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, saying it is not pushed
        self.assertIn('"decision": "block"', out)
        self.assertIn("not pushed", out)

    def test_pushed_commit_lets_the_end_through(self):
        # Given a commit that leaves nothing for the user, pushed
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_unpushed_finishing_commit_blocks_the_end(self):
        # Given the commit finishing the session, not pushed
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("status: running", "status: finished"))
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, saying it is not pushed
        self.assertIn("not pushed", out)

    def test_pushed_finishing_commit_lets_the_end_through(self):
        # Given the commit finishing the session, pushed
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("status: running", "status: finished"))
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_branch_with_no_remote_branch_blocks_the_end(self):
        # Given a commit on a branch never pushed
        sh(self.r.dir, "git", "switch", "-qc", "other")
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, saying to push it
        self.assertIn("no remote branch", out)

    def test_record_out_of_form_blocks_the_end(self):
        # Given a steering.md without its `# Tasks` heading, committed and pushed
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("# Tasks\n", ""))
        self.r.commit("rn: a\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, naming the heading
        self.assertIn('"decision": "block"', out)
        self.assertIn("`# Tasks`", out)

    def test_ending_a_turn_with_no_session_passes(self):
        # Given no session on the branch
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        # When the turn ends
        code, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual((code, out.strip()), (0, ""))


if __name__ == "__main__":
    unittest.main()
