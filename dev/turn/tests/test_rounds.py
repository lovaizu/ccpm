import json
from unittest import mock

from helpers import (
    CALL,
    CHECKED,
    EVALUATED,
    FIRST_READ,
    FOUND,
    GOOD,
    ID,
    READ_GIVEN,
    READ_SHOWN,
    SENT_BACK,
    STOPPED,
    WAITS,
    RepoTest,
    pretooluse,
    run,
    subagentstop,
)

RESULT = CALL["result"]
# The generator's claim of every item's Good.
CLAIM = {"items": [GOOD, dict(GOOD, item="B-1")], "questions": []}
# A reading of the orchestrator's own, which the run does not take between the roles.
EVERY = {"items": [GOOD, dict(GOOD, item="B-1")], "questions": []}


class RoundTest(RepoTest):
    """A round in which the generator and the first user, once they have replied, are sent what
    comes next by message."""

    def setUp(self):
        super().setUp()
        self.prompt = self.started()
        self.claim()

    def claim(self):
        """The generator replies with its claim, as turn's hook keeps it."""
        self.assertEqual(self.replied("turn:generator", self.prompt, CLAIM, *READ_GIVEN), (0, ""))

    def answer(self, agent_type, reply):
        """The role sent a message replies again, as turn's hook sees it on the same record."""
        path = f"{self.repo}/session/subagents/agent-{agent_type.partition(':')[2]}.jsonl"
        event = self.event(
            "SubagentStop",
            agent_type,
            agent_transcript_path=path,
            last_assistant_message=json.dumps(reply),
            stop_hook_active=False,
        )
        return self.hook(subagentstop, event)

    def waited(self, *replies):
        """What the script prints asked with nothing, while each pause of its wait lets the next
        of the replies, an (agent, reply) pair, arrive."""
        pending = list(replies)

        def pause(seconds):
            if pending:
                self.assertEqual(self.answer(*pending.pop(0)), (0, ""))

        with mock.patch.object(run.time, "sleep", pause):
            return self.next()

    def first_user_read(self):
        """After the generator's claim, the first user is started."""
        out = self.next()
        self.assertEqual(out["agent"], "turn:first-user")
        self.assertIn("prompt", out)
        return out["prompt"]

    def stopped(self):
        """The first user stops at an item, and the script prints the message sending it back to
        the generator; with the first user's prompt."""
        prompt = self.first_user_read()
        self.assertEqual(self.replied("turn:first-user", prompt, {"items": FIRST_READ}), (0, ""))
        return self.next(), prompt


class TestGeneratorKept(RoundTest):
    def test_a_generator_that_replied_is_sent_the_first_users_stop_by_message(self):
        # Given: a generator that replied once, and a first user that stopped at an item
        # When: the orchestrator goes on
        # Then: the script names the generator, the message and its agent to send it to, and the
        # generator is given the stop as the first user gave it
        out, _ = self.stopped()
        self.assertEqual(out, {"agent": "turn:generator", "message": self.prompt, "to": ID})
        self.assertEqual(self.given()["sent_back"], [STOPPED])

    def test_the_messaged_generators_reply_is_waited_for_and_the_first_user_sent_it(self):
        # Given: a generator sent an item back by message
        # When: the orchestrator runs the script with nothing, and the reply arrives as it waits
        # Then: the first user is sent the work made again by message, with no reading between
        _, prompt = self.stopped()
        out = self.waited(("turn:generator", CLAIM))
        self.assertEqual(out, {"agent": "turn:first-user", "message": prompt, "to": ID})

    def test_a_reply_not_come_within_the_wait_leaves_the_run_waiting(self):
        # Given: a generator sent an item back by message
        # When: no reply comes while the script waits
        # Then: it waits a hundred pauses of one second, and says the run waits on the generator
        self.stopped()
        pauses = []
        with mock.patch.object(run.time, "sleep", pauses.append):
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(pauses, [1] * 100)

    def test_a_run_read_while_the_hook_writes_it_is_read_again(self):
        # Given: a generator sent an item back by message
        # When: the script finds the run half written at one pause, and the reply at the next
        # Then: it goes on from the reply
        _, prompt = self.stopped()
        with open(RESULT, encoding="utf-8") as f:
            whole = f.read()
        steps = [whole[:10], whole]

        def pause(seconds):
            if steps:
                self.write(RESULT, steps.pop(0))
            else:
                self.answer("turn:generator", CLAIM)

        with mock.patch.object(run.time, "sleep", pause):
            out = self.next()
        self.assertEqual(out, {"agent": "turn:first-user", "message": prompt, "to": ID})

    def test_a_reading_before_the_messaged_generator_replied_stops(self):
        # Given: a generator sent an item back by message, not replied yet
        # When: the orchestrator gives a reading of its own
        # Then: it stops, saying the run waits on the generator's reply
        self.stopped()
        self.assertIn("waits on turn:generator's reply", self.refused(EVERY))


class TestFirstUserKept(RoundTest):
    def test_a_first_user_finding_every_good_has_the_evaluator_started(self):
        # Given: a first user started after the generator's claim
        # When: it finds every item's Good
        # Then: the evaluator is started with its reading
        prompt = self.first_user_read()
        reading = [FOUND, dict(FOUND, item="B-1")]
        self.assertEqual(self.replied("turn:first-user", prompt, {"items": reading}), (0, ""))
        self.assertEqual(self.next()["agent"], "turn:evaluator")
        self.assertEqual(self.given()["reading"], reading)

    def test_an_item_the_first_user_stopped_at_goes_to_the_generator_and_back_to_it(self):
        # Given: a first user that finds no Good for one item
        # When: the generator replies with the work made again, and the first user then finds
        # every Good
        # Then: the evaluator is started
        self.stopped()
        self.waited(("turn:generator", CLAIM))
        reading = [FOUND, dict(FOUND, item="B-1")]
        self.assertEqual(
            self.waited(("turn:first-user", {"items": reading}))["agent"], "turn:evaluator"
        )

    def test_the_first_user_sends_back_three_times_a_round_at_most(self):
        # Given: a first user that stops at an item every time it reads
        # When: the run goes on each time
        # Then: the generator is sent it three times, and the fourth goes on to the evaluator
        out, _ = self.stopped()
        self.assertEqual(out["agent"], "turn:generator")
        for agent in ("turn:generator", "turn:generator", "turn:evaluator"):
            self.waited(("turn:generator", CLAIM))
            self.assertEqual(
                self.waited(("turn:first-user", {"items": FIRST_READ}))["agent"], agent
            )

    def test_a_stop_at_an_item_waiting_on_a_question_is_not_sent_back(self):
        # Given: a claim with one item waiting on a question
        # When: the first user stops at that item
        # Then: the evaluator is started
        self.started()
        out = self.made(GOOD, WAITS)
        self.replied("turn:first-user", out["prompt"], {"items": FIRST_READ})
        self.assertEqual(self.next()["agent"], "turn:evaluator")

    def test_the_second_round_starts_the_generator_and_the_first_user_anew(self):
        # Given: a first round whose generator and first user replied, leaving an item without Good
        # When: the run goes on to the second round
        # Then: the generator is started with a prompt, not sent a message, and the round's
        # send-backs are counted anew
        self.stopped()
        self.waited(("turn:generator", CLAIM))
        reading = [FOUND, dict(FOUND, item="B-1")]
        out = self.waited(("turn:first-user", {"items": reading}))
        self.replied("turn:evaluator", out["prompt"], {"items": [EVALUATED]})
        self.next()
        out = self.next({"items": [GOOD, SENT_BACK], "questions": []})
        self.replied("turn:learner", out["prompt"], {"process": [], "checked": CHECKED})
        out = self.next()
        self.assertEqual(out["agent"], "turn:generator")
        self.assertIn("prompt", out)
        kept = self.read_json(RESULT)["running"]
        self.assertFalse({"started", "sent"} & set(kept))


class TestMessageHooks(RoundTest):
    def send(self, to, message, agent_type="turn:up"):
        event = self.event(
            "PreToolUse",
            agent_type,
            tool_name="SendMessage",
            tool_input={"to": to, "message": message, "summary": "go on"},
        )
        self.given_record(ID, json.dumps(CALL))
        return event

    def test_a_message_sent_as_the_script_printed_passes(self):
        # Given: a generator to be sent the first user's stop
        # When: the orchestrator sends it the message to the agent the script printed
        # Then: it goes through
        out, _ = self.stopped()
        self.assertEqual(self.hook(pretooluse, self.send(out["to"], out["message"])), (0, ""))

    def test_a_message_to_another_agent_or_of_other_words_stops(self):
        # Given: a generator to be sent an item back
        # When: the orchestrator sends the message elsewhere, to an agent named by part of its
        # name, or other words
        # Then: it is stopped, saying to send what the script printed
        out, _ = self.stopped()
        for to, message in (
            ("a9", out["message"]),
            ("z9", out["message"]),
            (out["to"][:-1], out["message"]),
            (out["to"], "fix B-1"),
            (out["to"], "{}"),
        ):
            with self.subTest(to=to, message=message):
                code, err = self.hook(pretooluse, self.send(to, message))
                self.assertEqual(code, 2)
                self.assertIn("send only what turn.py printed last", err)

    def test_a_message_when_none_is_due_stops(self):
        # Given: a generator started, whose reply is kept, and no message printed; and a first
        # user to be started next
        # When: the orchestrator sends the generator a message
        # Then: it is stopped
        code, err = self.hook(pretooluse, self.send(ID, self.prompt))
        self.assertEqual(code, 2)
        self.assertIn("send only what turn.py printed last", err)
        self.first_user_read()
        code, err = self.hook(pretooluse, self.send(ID, self.prompt))
        self.assertEqual(code, 2)
        self.assertIn("send only what turn.py printed last", err)

    def test_the_orchestrator_loading_sendmessage_passes(self):
        # Given: a generator to be sent an item back
        # When: the orchestrator loads SendMessage with ToolSearch
        # Then: it goes through
        self.stopped()
        event = self.event(
            "PreToolUse",
            "turn:up",
            tool_name="ToolSearch",
            tool_input={"query": "select:SendMessage", "max_results": 1},
        )
        self.given_record(ID, json.dumps(CALL))
        self.assertEqual(self.hook(pretooluse, event), (0, ""))

    def test_a_message_from_a_role_stops(self):
        # Given: a generator sent an item back by message
        # When: it sends its reply to the orchestrator by message
        # Then: it is stopped, saying to reply with its form
        out, _ = self.stopped()
        for role in ("turn:generator", "turn:first-user", "turn:evaluator", "turn:learner"):
            with self.subTest(role=role):
                code, err = self.hook(pretooluse, self.send(ID, out["message"], role))
                self.assertEqual(code, 2)
                self.assertIn("reply with your form alone", err)

    def test_a_message_to_the_calling_ai_passes(self):
        # Given: a generator to be sent an item back, and one whose reply is kept with no message
        # due
        # When: the orchestrator or a role tells `main`, the calling AI's conversation, what it
        # will do or what is done
        # Then: it goes through
        for due in (True, False):
            if due:
                self.stopped()
            for role in ("turn:up", "turn:generator", "turn:first-user", "turn:learner"):
                with self.subTest(due=due, role=role):
                    event = self.send("main", "generator: will write README.md", role)
                    self.assertEqual(self.hook(pretooluse, event), (0, ""))

    def test_a_message_from_another_agent_or_of_no_run_passes(self):
        # Given: a message sent by an agent that is not turn's orchestrator, and one by an
        # orchestrator whose run is not going
        # When: it is about to be sent
        # Then: it goes through
        self.assertEqual(self.hook(pretooluse, self.send("a9", "hi", "Explore")), (0, ""))
        event = self.send("a9", "hi")
        self.write_json(RESULT, {"returned": True})
        self.assertEqual(self.hook(pretooluse, event), (0, ""))

    def test_starting_a_role_where_a_message_is_due_stops(self):
        # Given: a generator to be sent an item back
        # When: the orchestrator starts a generator anew in its place
        # Then: it is stopped, saying to send the message, as the generator is started already
        out, _ = self.stopped()
        event = self.event(
            "PreToolUse",
            "turn:up",
            tool_name="Agent",
            tool_input={"subagent_type": "turn:generator", "prompt": out["message"]},
        )
        code, err = self.hook(pretooluse, event)
        self.assertEqual(code, 2)
        self.assertIn("send turn:generator what turn.py printed last with SendMessage", err)

    def test_a_reply_of_a_role_not_waited_on_is_not_kept(self):
        # Given: a run whose first user is to be started next
        # When: the generator replies again, or an evaluator replies out of its form
        # Then: each ends, and neither reply is kept as the first user's
        prompt = self.first_user_read()
        self.assertEqual(self.answer("turn:generator", CLAIM), (0, ""))
        self.assertEqual(self.replied("turn:evaluator", prompt, {}), (0, ""))
        self.assertNotIn("reply", self.read_json(RESULT)["running"]["next"])

    def test_only_the_generator_and_the_first_user_are_kept_started(self):
        # Given: a run whose generator, first user and evaluator replied
        # When: the evaluator's reply is kept
        # Then: the run keeps the generator's and the first user's agents alone
        prompt = self.first_user_read()
        reading = [FOUND, dict(FOUND, item="B-1")]
        self.replied("turn:first-user", prompt, {"items": reading}, *READ_SHOWN)
        out = self.next()
        self.replied("turn:evaluator", out["prompt"], {"items": [EVALUATED]})
        started = self.read_json(RESULT)["running"]["started"]
        self.assertEqual(started, {"turn:generator": ID, "turn:first-user": ID})
