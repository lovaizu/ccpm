"""Each time one of fw's roles replies, the facts of its turn are written into its CCS from its own
JSONL: the exchange in order, what it ran, read and wrote, and the turn's records; replies of other
agents leave every CCS untouched."""

import os
import unittest

from support import Repo, WORK, path


class Facts(Repo):
    def test_the_exchange_is_written_in_the_order_of_the_roles_jsonl(self):
        # Given a maker sent request, go and check, and replying to each
        self.write("make", self.ready("make"))
        p = path("make")
        transcript = self.role_jsonl("maker", [
            ("conductor", f"request {p}"), ("role", "thinking aloud"), ("role", f"reply to request {p}\nI will."),
            ("conductor", f"go {p}"), ("role", f"reply to go {p}"),
            ("conductor", f"check {p}"), ("role", f"reply to check {p}"),
            ("conductor", "a message with no header"), ("role", "")])
        # When
        self.stop("fw:maker", transcript)
        # Then
        said = [e for e in self.load("make")["episodic_trace"] if e[0] in ("request", "go", "check", "reply")]
        self.assertEqual(said, [("request", f"request {p}"), ("reply", f"reply to request {p}"),
                                ("go", f"go {p}"), ("reply", f"reply to go {p}"),
                                ("check", f"check {p}"), ("reply", f"reply to check {p}")])

    def test_what_the_role_ran_read_and_wrote_is_written_from_its_jsonl(self):
        # Given
        self.write("make", self.ready("make"))
        transcript = self.role_jsonl("maker", [("conductor", f"request {path('make')}"), ("role", "reply to request")], tools=[
            ("Read", {"file_path": os.path.join(self.root, "docs/a.md")}, {"content": "a"}),
            ("Read", {"file_path": os.path.join(self.root, "docs/a.md")}, {"content": "a"}),
            ("Bash", {"command": "cat " + "x" * 200}, {"content": "ok"}),
            ("Bash", {"command": "ls /none"}, {"content": "Exit code 1\nno", "is_error": True}),
            ("Bash", {"command": "false"}, {"content": [{"type": "text", "text": "failed"}], "is_error": True}),
            ("Write", {"file_path": os.path.join(self.root, WORK)}, {"content": "ok"}),
            ("Edit", {"file_path": "/tmp/elsewhere.md"}, {"content": "ok"}),
        ])
        with open(transcript, "a") as f:
            f.write('{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "z", "name": "Bash", "input": {"command": "sleep 9"}}]}}\n')
        # When
        self.stop("fw:maker", transcript)
        # Then
        state = self.load("make")
        trace = [e for e in state["episodic_trace"] if e[0] not in ("request", "reply")]
        self.assertEqual(trace, [
            ("executed", "cat " + "x" * 156 + "… → exit 0"),
            ("failed", "ls /none → exit 1"),
            ("failed", "false → exit 1"),
            ("wrote", os.path.join(self.root, WORK)),
            ("wrote_outside", "/tmp/elsewhere.md"),
            ("failed", "sleep 9 → exit None"),
        ])
        self.assertIn(("read", "docs/a.md"), state["retrieved_artifacts"])
        self.assertEqual(sum(1 for e in state["retrieved_artifacts"] if e[0] == "read"), 1)

    def test_a_turn_is_recorded_once_and_worked_once_its_reply_to_go_has_come(self):
        # Given a maker turn that replied to request, then to go, then to ok
        self.write("make", self.ready("make"))
        p = path("make")
        said = [("conductor", f"request {p}"), ("role", f"reply to request {p}")]
        transcript = self.role_jsonl("maker", said)
        self.stop("fw:maker", transcript)
        self.assertEqual([e[0] for e in self.load("make")["retrieved_artifacts"] if e[0] in ("turn", "worked")], ["turn"])
        self.update("make", "goal_orientation", ("agreed", "x"))
        self.update("make", "episodic_trace", ("work_before", "absent"))
        # When the work is made and the role replies to go, then to ok
        self.make_work("hello\n")
        said += [("conductor", f"go {p}"), ("role", f"reply to go {p}")]
        self.stop("fw:maker", self.role_jsonl("maker", said))
        said += [("conductor", f"ok {p}"), ("role", f"reply to ok {p}")]
        self.stop("fw:maker", self.role_jsonl("maker", said))
        # Then
        records = [e for e in self.load("make")["retrieved_artifacts"] if e[0] in ("turn", "worked", "made")]
        self.assertEqual(records, [("turn", f"#1 {transcript}"), ("worked", f"#1 {transcript}"), ("made", f"#1 {transcript}")])
        self.assertIn(("work_before", "absent"), self.load("make")["episodic_trace"])

    def test_a_maker_that_left_the_work_unchanged_has_not_made_it(self):
        # Given a work that exists before go, and is the same after
        self.make_work("hello\n")
        self.write("make", self.ready("make"))
        self.turn("make", go=False)
        # When
        self.turn("make", made="hello\n")
        # Then
        self.assertNotIn("made", [e[0] for e in self.load("make")["retrieved_artifacts"]])

    def test_the_learners_learnings_are_kept(self):
        # Given a learner that wrote its learnings into its CCS
        self.write("learn", self.ready("learn", ("semantic_gist", "content", "say who it is from")))
        p = path("learn")
        # When it replies
        self.stop("fw:learner", self.role_jsonl("learner", [("conductor", f"request {p}"), ("role", f"reply to request {p}")]))
        # Then
        self.assertIn(("content", "say who it is from"), self.load("learn")["semantic_gist"])

    def test_the_learner_is_handed_the_conductors_jsonl(self):
        # Given a task used once
        self.write("make", self.ready("make"))
        self.turn("make", made="hello\n")
        self.write("use", self.ready("use"))
        self.turn("use")
        self.write("learn", self.ready("learn"))
        # When the learner is started
        self.pre("Agent", {"subagent_type": "fw:learner", "prompt": f"request {path('learn')}"})
        # Then
        self.assertIn(("conductor", self.conductor), self.load("learn")["retrieved_artifacts"])

    def test_a_reply_of_another_agent_leaves_the_ccs_untouched(self):
        # Given
        self.write("make", self.ready("make"))
        with open(os.path.join(self.root, path("make"))) as f:
            before = f.read()
        transcript = self.role_jsonl("other", [("conductor", f"request {path('make')}"), ("role", "hi")])
        # When
        for agent, file in (("Explore", transcript), ("fw:maker", None), ("fw:maker", "/none.jsonl"),
                            ("fw:first-user", transcript)):
            self.stop(agent, file)
        self.stop("fw:maker", self.role_jsonl("x", [("conductor", "request .mock/none/make.yaml"), ("role", "hi")]))
        # Then
        with open(os.path.join(self.root, path("make"))) as f:
            self.assertEqual(f.read(), before)


if __name__ == "__main__":
    unittest.main()
