"""rn's Stop hook: checks 8, 13 and 14 when the conductor ends its turn."""
import unittest

from harness import Session, sh, SDIR, STEERING, PROPOSE, PAUSED_MAP


class Stop(Session):
    # Check 8
    def test_unpushed_commit_blocks_the_end(self):
        # Given a sign-off commit not pushed
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked
        self.assertIn('"decision": "block"', out)

    def test_pushed_commit_lets_the_end_through(self):
        # Given a sign-off commit pushed
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_unpushed_commit_blocks_the_second_end_too(self):
        # Given a commit not pushed
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● design ── agreed → writ rewrites the documents")
        # When the turn ends a second time
        _, out = self.r.hook("stop", stop_hook_active=True)
        # Then the end is blocked, saying it is not pushed
        self.assertIn("not pushed", out)

    def test_pushed_commit_lets_the_second_end_through(self):
        # Given a commit pushed
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends a second time
        _, out = self.r.hook("stop", stop_hook_active=True)
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
        # Given a sign-off commit on a branch never pushed
        sh(self.r.dir, "git", "switch", "-qc", "other")
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, saying to push it
        self.assertIn("no remote branch", out)

    # Check 13
    def test_ending_a_turn_with_nothing_for_the_user_is_blocked(self):
        # Given a pushed commit that leaves nothing for the user to decide
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: agree\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, saying to go on
        self.assertIn('"decision": "block"', out)
        self.assertIn("go on", out)

    def test_ending_a_turn_again_with_nothing_for_the_user_passes(self):
        # Given a pushed commit that leaves nothing for the user to decide
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: agree\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends a second time
        _, out = self.r.hook("stop", stop_hook_active=True)
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_ending_a_turn_at_a_stop_passes(self):
        for line in ("● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off",
                     "● #1 Plan sign-off ── approved → #2 Design sign-off",
                     "● #3 cart ── half → paused at #3 cart"):
            # Given a pushed commit stopping for the user
            self.r.write("a.txt", line + "\n")
            self.r.commit("rn: x\n\n" + line + "\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
            sh(self.r.dir, "git", "push", "-q")
            # When the turn ends
            _, out = self.r.hook("stop")
            # Then nothing is said
            self.assertEqual(out.strip(), "", line)

    def test_ending_a_turn_with_a_question_open_passes(self):
        # Given a pushed commit that leaves a question in open/
        self.r.write(f"{SDIR}/open/01-notes-question.md", "Serves: A1\n\nWhich way?\n")
        self.r.commit("rn: ask\n\n● design ── question written → asking the user")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    # Check 14
    def test_ending_a_turn_in_another_language_is_blocked_even_the_second_time(self):
        # Given a pushed sign-off and a Japanese conversation
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        sh(self.r.dir, "git", "push", "-q")
        english = "Which word should come before the code? I recommend A, since it matches the screen."
        for active in (False, True):
            # When the turn ends, the first time or the second, with an English message
            _, out = self.r.hook("stop", last_assistant_message=english, stop_hook_active=active)
            # Then the end is blocked, naming Japanese
            self.assertIn('"decision": "block"', out)
            self.assertIn("Japanese", out)

    def test_ending_a_turn_in_the_conversation_language_passes(self):
        # Given a pushed sign-off and a Japanese conversation
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        sh(self.r.dir, "git", "push", "-q")
        for text in ("`src/account` を TypeScript にすることで、何を得たいですか？ "
                     "推奨は A です。`DISPLAY_NAME_KEY` を設定しないとアプリは起動しません。",
                     "── typescript: 型の誤りがビルドで止まる ──\n✅ #1 Plan sign-off\n"
                     "👉 #2 Design sign-off ── PR で読んで /rn:ty で承認、/rn:gm で修正依頼\n\n"
                     "メールだけで登録したユーザーにも、ちゃんとした名前を出します。",
                     "OK"):
            # When the turn ends with a Japanese message, or one too short to judge
            _, out = self.r.hook("stop", last_assistant_message=text)
            # Then nothing is said
            self.assertEqual(out.strip(), "", text)

    def test_japanese_map_quoting_the_record_passes(self):
        # Given a pushed pause whose task name is English
        self.commit_quoting_record_and_push()
        # When the turn ends with a Japanese map quoting the goal, task names and decision line
        _, out = self.r.hook("stop", last_assistant_message=PAUSED_MAP)
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_japanese_list_of_quoted_decision_lines_passes(self):
        # Given a pushed pause whose task name is English
        self.commit_quoting_record_and_push()
        bullets = "前回の承認からの変更:\n" + "".join(
            f"- ● #{n} Apply the discount before the coupon ── half → paused at #{n} Apply the "
            "discount before the coupon\n" for n in range(3, 9)) + "確認してください。"
        # When the turn ends with a Japanese list of quoted decision lines
        _, out = self.r.hook("stop", last_assistant_message=bullets)
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_english_around_text_quoted_from_the_record_is_blocked(self):
        # Given a pushed pause whose task name is English
        self.commit_quoting_record_and_push()
        english = PAUSED_MAP.replace("ここで一時停止", "paused here").replace(
            "次: /clear してから /rn:up", "Next: clear the conversation, then take it up again.")
        # When the turn ends with the same map, its own words in English
        _, out = self.r.hook("stop", last_assistant_message=english)
        # Then the end is blocked, naming Japanese
        self.assertIn("Japanese", out)

    # No session: nothing is checked.
    def test_ending_a_turn_with_no_session_passes(self):
        # Given no session on the branch
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        # When the turn ends
        code, _ = self.r.hook("stop")
        # Then it passes
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
