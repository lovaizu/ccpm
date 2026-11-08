"""The cases of laid.py's contract: the lanes and routes as a proposal gives them and as
`hooks/lanes.json` keeps them, and whether each can stand."""

from helpers import laid, testing

WRITER = {
    "name": "writer",
    "steps": [
        {"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]},
        {"step": 3, "lanes": [{"lane": "write_only", "takes": ["CHANGELOG.md"]}]},
    ],
}


class TestParsed(testing.FolderTest):
    def test_each_lane_of_a_role_is_kept_with_its_step(self):
        found = laid.parsed({"subagents": [WRITER]})
        self.assertEqual(
            found.roles[0].lanes,
            (
                laid.Lane(2, "run_only", ("git log --oneline",), None),
                laid.Lane(3, "write_only", ("CHANGELOG.md",), None),
            ),
        )

    def test_a_role_keeps_its_adapters_and_results(self):
        given = {**WRITER, "adapter": "a.py", "steps_adapter": "s.py", "results": ["done"]}
        role = laid.parsed({"subagents": [given]}).roles[0]
        self.assertEqual(
            (role.adapter, role.steps_adapter, role.results), ("a.py", "s.py", ("done",))
        )

    def test_a_role_is_found_by_its_name(self):
        found = laid.parsed({"subagents": [WRITER]})
        self.assertEqual(found.role("writer"), found.roles[0])

    def test_a_name_no_role_has_finds_none(self):
        self.assertIsNone(laid.parsed({"subagents": [WRITER]}).role("reviewer"))

    def test_lanes_with_routes_alone_have_no_roles(self):
        routes = {"orchestrator": "write", "routes": []}
        found = laid.parsed({"routes": routes})
        self.assertEqual((found.roles, found.routes), ((), routes))


class TestFaults(testing.FolderTest):
    def test_lanes_that_can_all_stand_have_no_fault(self):
        self.assertEqual(laid.faults(laid.parsed({"subagents": [WRITER]})), [])

    def test_a_lane_that_cannot_stand_is_named_with_its_step_and_role(self):
        given = {
            "name": "writer",
            "steps": [{"step": 1, "lanes": [{"lane": "in_form", "takes": ["a"]}]}],
        }
        self.assertEqual(
            laid.faults(laid.parsed({"subagents": [given]})),
            [
                (
                    "step 1 of writer: in_form takes a thing for each of its places, output and"
                    " form, and is given 1"
                )
            ],
        )

    def test_an_adapter_on_a_lane_that_reads_no_port_is_a_fault(self):
        lane = {"lane": "write_only", "takes": ["a"], "adapter": "hooks/adapters/items-a.py"}
        given = {"name": "writer", "steps": [{"step": 1, "lanes": [lane]}]}
        self.assertEqual(
            laid.faults(laid.parsed({"subagents": [given]})),
            ["step 1 of writer: write_only reads no port, so it takes no adapter"],
        )

    def test_two_roles_of_one_name_are_a_fault(self):
        self.assertEqual(
            laid.faults(laid.parsed({"subagents": [WRITER, WRITER]})),
            ["writer is given twice"],
        )

    def test_a_step_given_twice_is_a_fault(self):
        given = {"name": "writer", "steps": [WRITER["steps"][0], WRITER["steps"][0]]}
        self.assertEqual(
            laid.faults(laid.parsed({"subagents": [given]})),
            ["writer gives step 2 twice"],
        )


class TestRead(testing.FolderTest):
    def test_the_lanes_laid_are_read_from_hooks_lanes_json(self):
        self.write_json("hooks/lanes.json", {"subagents": [WRITER]})
        self.assertEqual(laid.read(self.base).roles[0].name, "writer")

    def test_a_plugin_with_no_lanes_laid_is_refused(self):
        with self.assertRaisesRegex(laid.Unlaid, r"holds no hooks/lanes\.json"):
            laid.read(self.base)

    def test_lanes_laid_that_are_no_json_are_refused(self):
        self.write("hooks/lanes.json", "{")
        with self.assertRaisesRegex(laid.Unlaid, r"hooks/lanes\.json is no JSON: "):
            laid.read(self.base)

    def test_lanes_laid_out_of_their_form_are_refused(self):
        self.write_json("hooks/lanes.json", {"subagents": [{"name": "writer"}]})
        with self.assertRaisesRegex(
            laid.Unlaid,
            r"hooks/lanes\.json is out of its form: \$\.subagents\[0\]: expected the key \"steps\"",
        ):
            laid.read(self.base)

    def test_lanes_laid_holding_the_plugin_folder_are_out_of_their_form(self):
        self.write_json("hooks/lanes.json", {"plugin": "x", "subagents": [WRITER]})
        with self.assertRaisesRegex(laid.Unlaid, r"\$\.plugin: expected no such key"):
            laid.read(self.base)

    def test_lanes_laid_with_a_fault_are_refused(self):
        self.write_json("hooks/lanes.json", {"subagents": [WRITER, WRITER]})
        with self.assertRaisesRegex(laid.Unlaid, r"hooks/lanes\.json: writer is given twice"):
            laid.read(self.base)
