import json

from helpers import (
    CALL,
    ID,
    SCRIPT,
    RepoTest,
    agents,
    call_given,
    no_commit,
    role_given,
    start_as_called,
)

# Tool names sorting before and after each name a check looks for, so a check takes that tool
# alone.
OTHER_TOOLS = ("A", "Write")


class CheckTest(RepoTest):
    def tool(self, agent_type, tool_name, **tool_input):
        return self.event("PreToolUse", agent_type, tool_name=tool_name, tool_input=tool_input)


class TestRuns(CheckTest):
    def test_a_command_runs_the_step_it_names_alone(self):
        # Given: commands running turn's script for one step
        # When: each is asked whether it runs another step
        # Then: it does not
        for step, other in (("start", "next"), ("next", "start"), ("record", "next")):
            with self.subTest(step=step):
                self.assertTrue(agents.runs(f"{SCRIPT} {step} r.json", step))
                self.assertFalse(agents.runs(f"{SCRIPT} {step} r.json", other))


class TestCallGiven(CheckTest):
    def test_only_a_call_to_turn_up_is_checked(self):
        # Given: a call turn cannot take, given to another tool or to another agent
        # When: it is about to be used
        # Then: it goes through, as only a call to turn:up is turn's
        prompt = json.dumps({"ccs": "none.json"})
        for tool in OTHER_TOOLS:
            with self.subTest(tool=tool):
                event = self.tool(None, tool, subagent_type="turn:up", prompt=prompt)
                self.assertEqual(call_given.check(event), [])
        for agent in ("Explore", "zzz"):
            with self.subTest(agent=agent):
                event = self.tool(None, "Agent", subagent_type=agent, prompt=prompt)
                self.assertEqual(call_given.check(event), [])


class TestNoCommit(CheckTest):
    def test_only_a_command_run_by_bash_is_checked(self):
        # Given: one of turn's agents using a tool other than Bash, whose input holds a commit
        # When: it is about to be used
        # Then: it goes through, as nothing is run
        for tool in ("Agent", "Write"):
            with self.subTest(tool=tool):
                event = self.tool("turn:up", tool, command="git commit -m x")
                self.assertEqual(no_commit.check(event), [])


class TestRoleGiven(CheckTest):
    def test_only_a_role_started_by_agent_is_checked(self):
        # Given: another tool whose input names a role and no prompt turn.py printed
        # When: it is about to be used
        # Then: it goes through
        for tool in OTHER_TOOLS:
            with self.subTest(tool=tool):
                event = self.tool("turn:up", tool, subagent_type="turn:generator", prompt="x")
                self.assertEqual(role_given.check(event), [])

    def test_a_role_started_with_another_roles_prompt_stops(self):
        # Given: a run whose generator is to be started next
        # When: the first user or the learner, whose names sort before and after the generator's,
        # is started with the generator's prompt
        # Then: it is stopped, naming the generator
        prompt = self.started()
        for agent in ("turn:first-user", "turn:learner"):
            with self.subTest(agent=agent):
                event = self.tool("turn:up", "Agent", subagent_type=agent, prompt=prompt)
                self.assertEqual(
                    role_given.check(event),
                    ["start turn:generator with what turn.py printed last as its prompt, as it is"],
                )

    def test_a_prompt_naming_no_run_by_its_path_stops(self):
        # Given: a run going
        # When: a role is started with a prompt whose run is not a path, or that is not an object
        # Then: it is stopped, told to start it with what turn.py printed
        self.started()
        for prompt in ({"run": 3}, ["run"]):
            with self.subTest(prompt=prompt):
                event = self.tool(
                    "turn:up", "Agent", subagent_type="turn:generator", prompt=json.dumps(prompt)
                )
                self.assertEqual(
                    role_given.check(event),
                    ["start turn:generator with what turn.py printed last as its prompt, as it is"],
                )


class TestStartAsCalled(CheckTest):
    def start(self, agent_type, tool, call):
        return self.tool(agent_type, tool, command=f"{SCRIPT} start '{json.dumps(call)}'")

    def test_only_the_orchestrator_starting_by_bash_is_checked(self):
        # Given: a call, and a role or another tool starting a run with a call that differs
        # When: it is about to be used
        # Then: it goes through, as only the orchestrator's start is checked
        self.given_record(ID, json.dumps(CALL))
        changed = dict(CALL, result="x.json")
        self.assertEqual(start_as_called.check(self.start("turn:generator", "Bash", changed)), [])
        for tool in ("Agent", "Write"):
            with self.subTest(tool=tool):
                self.assertEqual(start_as_called.check(self.start("turn:up", tool, changed)), [])

    def test_the_call_is_read_wherever_it_ends_in_the_command(self):
        # Given: an orchestrator called with a call
        # When: it starts the run with that call, its last brace at an odd place or an even one
        # Then: it goes through
        self.given_record(ID, json.dumps(CALL))
        for space in ("", " "):
            with self.subTest(space=space):
                command = f"{SCRIPT} start {space}'{json.dumps(CALL)}'"
                event = self.tool("turn:up", "Bash", command=command)
                self.assertEqual(start_as_called.check(event), [])
