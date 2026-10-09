"""Each condition fw sets on a step of a role's turn stops a call that lacks it, says what is
missing, and lets through one that has it; calls that are not fw's go through untouched."""

import os
import unittest

from support import Repo, path


class Request(Repo):
    def request(self, role, prompt=None, agent_type=None):
        return self.pre("Agent", {"subagent_type": agent_type or f"fw:{ {'make': 'maker', 'use': 'first-user', 'learn': 'learner'}[role]}",
                                  "prompt": prompt or f"request {path(role)}"})

    def test_a_ready_maker_ccs_lets_the_maker_start(self):
        # Given
        self.write("make", self.ready("make"))
        # When
        code, _, said = self.request("make")
        # Then
        self.assertEqual((code, said), (0, ""))

    def test_a_prompt_without_its_header_is_stopped_and_told_the_header(self):
        # Given
        self.write("make", self.ready("make"))
        # When
        code, _, said = self.request("make", prompt="make the greeting")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("Begin the prompt with `request <task>/make.yaml`", said)

    def test_a_header_for_another_role_is_stopped(self):
        # Given
        self.write("use", self.ready("use"))
        # When
        code, _, said = self.request("make", prompt=f"request {path('use')}")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("request <task>/make.yaml", said)

    def test_a_missing_ccs_is_stopped(self):
        # Given no CCS
        # When
        code, _, said = self.request("make")
        # Then
        self.assertEqual(code, 2)
        self.assertIn(f"{path('make')} does not exist", said)

    def test_a_missing_entry_of_fws_list_is_named_with_where_it_comes_from(self):
        # Given
        state = self.ready("make")
        state["focal_entities"] = [e for e in state["focal_entities"] if e[0] != "receiver"]
        self.write("make", state)
        # When
        code, _, said = self.request("make")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("focal_entities: receiver (from steering: who uses the work)", said)

    def test_a_missing_entry_of_the_plugins_list_is_named(self):
        # Given
        state = self.ready("make")
        state["constraints"] = []
        self.write("make", state)
        # When
        code, _, said = self.request("make")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("constraints: language (from steering)", said)

    def test_a_domain_folder_without_the_roles_list_is_named(self):
        # Given
        os.remove(os.path.join(self.domain, "make.json"))
        self.write("make", self.ready("make"))
        # When
        code, _, said = self.request("make")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("make.json does not exist", said)

    def test_an_open_gap_stops_the_start(self):
        # Given
        self.write("make", self.ready("make", ("uncertainty_signal", "gap", "who sends it")))
        # When
        code, _, said = self.request("make")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("Open gaps: who sends it", said)

    def test_a_fix_needs_the_judgment_and_the_learnings_of_the_last_turn(self):
        # Given a task whose work was made and used, not yet learned from
        self.write("make", self.ready("make"))
        self.turn("make", made="hello\n")
        self.write("use", self.ready("use"))
        self.turn("use")
        self.write("make", self.ready("make"))
        # When the maker is started again
        code, _, said = self.request("make")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("goal_orientation: fix", said)
        self.assertIn("goal_orientation: keep", said)
        self.assertIn("the learner's learnings from the last use", said)
        # And once they are there, it starts
        self.write("learn", self.ready("learn"))
        self.turn("learn")
        self.write("make", self.ready("make", ("goal_orientation", "fix", "line 1"), ("goal_orientation", "keep", "all")))
        self.assertEqual(self.request("make")[0], 0)

    def test_a_first_use_needs_a_made_work(self):
        # Given a maker that has not made the work
        self.write("use", self.ready("use"))
        # When
        code, _, said = self.request("use")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("a work made since the last use, at greeting.txt", said)

    def test_a_second_use_is_a_recheck_of_the_stumbled_places_after_a_fix(self):
        # Given a task used once, then fixed
        self.write("make", self.ready("make"))
        self.turn("make", made="hello\n")
        self.write("use", self.ready("use"))
        self.turn("use")
        # When the first user is started again before a fix
        code, _, said = self.request("use")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("a work made since the last use", said)
        self.assertIn("goal_orientation: recheck", said)
        # And after a fix, with the places to redo, it starts
        self.write("learn", self.ready("learn"))
        self.turn("learn")
        self.write("make", self.ready("make", ("goal_orientation", "fix", "line 1"), ("goal_orientation", "keep", "all")))
        self.turn("make", made="hello\nfrom: mock\n")
        self.write("use", self.ready("use", ("goal_orientation", "recheck", "greeting.txt:1")))
        self.assertEqual(self.request("use")[0], 0)

    def test_the_learner_needs_a_use_not_yet_learned_from(self):
        # Given no use yet
        self.write("learn", self.ready("learn"))
        # When
        code, _, said = self.request("learn")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("a use by the first user not yet learned from", said)

    def test_another_agent_is_never_stopped(self):
        # Given no CCS at all
        # When
        code, _, said = self.request("make", prompt="anything", agent_type="Explore")
        # Then
        self.assertEqual((code, said), (0, ""))


class Messages(Repo):
    def started(self):
        self.write("make", self.ready("make"))
        return self.turn("make", go=False)

    def send(self, to, text):
        return self.pre("SendMessage", {"to": to, "message": text})

    def test_go_needs_what_was_agreed(self):
        # Given a maker that replied to its request
        agent = self.started()
        # When go is sent before agreed is written
        code, _, said = self.send(agent, f"go {path('make')}")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("goal_orientation: agreed", said)
        self.update("make", "goal_orientation", ("agreed", "as said"))
        self.assertEqual(self.send(agent, f"go {path('make')}")[0], 0)

    def test_go_records_the_work_as_it_was_before_the_maker_works(self):
        # Given
        agent = self.started()
        self.update("make", "goal_orientation", ("agreed", "as said"))
        # When
        self.send(agent, f"go {path('make')}")
        # Then
        self.assertIn(("work_before", "absent"), self.load("make")["episodic_trace"])

    def test_no_second_message_goes_to_a_role_still_answering(self):
        # Given a check sent and not yet answered
        agent = self.started()
        self.message(agent, f"check {path('make')}")
        # When
        code, _, said = self.send(agent, f"ok {path('make')}")
        # Then
        self.assertEqual(code, 2)
        self.assertIn(f"The reply of fw:maker to `check {path('make')}` has not come", said)
        # And once the reply has come, it goes
        self.notice(agent)
        self.assertEqual(self.send(agent, f"ok {path('make')}")[0], 0)

    def test_a_role_started_in_the_foreground_has_replied_when_its_start_returns(self):
        # Given
        self.write("make", self.ready("make"))
        agent = self.launch("make", background=False)
        # When
        code, _, said = self.send(agent, f"check {path('make')}")
        # Then
        self.assertEqual((code, said), (0, ""))

    def test_a_message_that_failed_to_send_waits_for_nothing(self):
        # Given
        agent = self.started()
        self.message(agent, f"check {path('make')}", success=False)
        # When
        code, _, _ = self.send(agent, f"ok {path('make')}")
        # Then
        self.assertEqual(code, 0)

    def test_a_message_to_a_role_without_its_header_is_stopped_and_told_the_header(self):
        # Given
        agent = self.started()
        # When
        code, _, said = self.send(agent, "please go on")
        # Then
        self.assertEqual(code, 2)
        self.assertIn(f"Begin the message with `<request|go|check|ok> {path('make')}`", said)

    def test_a_message_to_the_wrong_agent_for_its_ccs_is_stopped(self):
        # Given
        self.started()
        # When
        code, _, said = self.send("someone", f"check {path('make')}")
        # Then
        self.assertEqual(code, 2)
        self.assertIn(f"someone was not started for {path('make')}", said)

    def test_a_new_turn_is_never_requested_by_message(self):
        # Given
        agent = self.started()
        # When
        code, _, said = self.send(agent, f"request {path('make')}")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("A turn starts with the Agent tool", said)

    def test_two_roles_on_two_tasks_wait_each_for_their_own_reply(self):
        # Given a maker on each of two tasks, one still answering a check
        other = ".mock/farewell/make.yaml"
        os.makedirs(os.path.join(self.root, ".mock/farewell"))
        self.write("make", self.ready("make"))
        state = self.ready("make")
        __import__("ccs").dump(state, os.path.join(self.root, other))
        first = self.launch("make")
        second = self.launch("make", prompt=f"request {other}")
        self.notice(first)
        self.notice(second)
        self.message(first, f"check {path('make')}")
        # When the conductor writes to the other task's maker
        code, _, said = self.send(second, f"check {other}")
        # Then it goes, and the first still waits
        self.assertEqual((code, said), (0, ""))
        self.assertEqual(self.send(first, f"ok {path('make')}")[0], 2)

    def test_a_message_to_an_agent_that_is_not_fws_is_never_stopped(self):
        # Given no conductor JSONL at all
        # When
        code, _, said = self.pre("SendMessage", {"to": "researcher", "message": "start on it"})
        # Then
        self.assertEqual((code, said), (0, ""))


class Results(Repo):
    def write_result(self):
        return self.pre("Write", {"file_path": ".mock/open/01-report-greeting.md"})

    def test_a_result_needs_a_use_and_its_learnings(self):
        # Given a made work never used
        self.write("make", self.ready("make"))
        self.turn("make", made="hello\n")
        # When
        code, _, said = self.write_result()
        # Then
        self.assertEqual(code, 2)
        self.assertIn("a use by the first user", said)
        self.assertIn("the learner's learnings from the last use", said)

    def test_a_result_after_a_use_not_learned_from_is_stopped(self):
        # Given
        self.write("make", self.ready("make"))
        self.turn("make", made="hello\n")
        self.write("use", self.ready("use"))
        self.turn("use")
        # When
        code, _, said = self.write_result()
        # Then
        self.assertEqual(code, 2)
        self.assertNotIn("a use by the first user (", said)
        self.assertIn("the learner's learnings from the last use", said)

    def test_a_result_file_with_no_task_folder_and_other_files_are_never_stopped(self):
        # Given no CCS
        # When
        codes = [self.pre("Write", {"file_path": p})[0] for p in ("docs/open/01-report-x.md", "notes.md")]
        # Then
        self.assertEqual(codes, [0, 0])

    def test_a_tool_fw_does_not_watch_is_never_stopped(self):
        # Given
        # When
        code, _, said = self.pre("Skill", {"skill": "fw:flow"})
        # Then
        self.assertEqual((code, said), (0, ""))


if __name__ == "__main__":
    unittest.main()
