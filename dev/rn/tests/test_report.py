from helpers import RepoTest

EVIDENCE = ".turn/setup"
TRACE = [{"evidence": EVIDENCE + "/list.json"}]
UNMET = "doc B-2 (Is the reader...): say where the logs go"
NOT_MET = {"id": "doc B-2", "title": "No question left"}


class TestReport(RepoTest):
    def turn(self, list_=None, orchestrator=None, **parts):
        ccs = {
            "focal_entities": [],
            "retrieved_artifacts": [],
            "semantic_gist": [],
            "episodic_trace": TRACE,
            **parts,
        }
        self.write_json("back.json", ccs)
        self.write_json(EVIDENCE + "/list.json", list_ or {"checklists": [], "items": []})
        self.write_json(EVIDENCE + "/orchestrator.json", orchestrator or {})

    def report(self, judgments):
        self.write_json("judgments.json", judgments)
        return self.rn("report", "back.json", "judgments.json")

    def test_decided_for_you_lists_each_point_question_item_rule_and_change(self):
        # Given: turn's CCS with a question, an item not met and a rule, and judgments with a
        #   point decided, the question and the item judged and a change made after turn
        # When: rn makes the report
        # Then: under Decided for you it lists the point, the question, the item with turn's way,
        #   the rule and the change
        self.turn(
            list_={"checklists": [], "items": [NOT_MET]},
            semantic_gist=[
                {"question": "Which port?"},
                {"unmet": UNMET},
                {"rule": "name the port in every example"},
            ],
        )
        _, out = self.report(
            {
                "decided": [{"point": "Port 8080", "ground": "the Makefile uses it"}],
                "questions": [{"question": "Which port?", "judged": "8080, from the Makefile"}],
                "unmet": [{"item": "doc B-2", "judged": "left for the user"}],
                "changed": [{"lines": "4", "why": "the port put in"}],
            }
        )
        self.assertEqual(
            out.split("\n\n")[0],
            "Decided for you\n"
            "  Port 8080: the Makefile uses it\n"
            "  Question: Which port?: 8080, from the Makefile\n"
            "  Not met: doc B-2 No question left: left for the user\n"
            "    turn: say where the logs go\n"
            "  Rule from turn: name the port in every example\n"
            "  Changed after turn: 4: the port put in",
        )

    def test_each_checklist_is_shown_with_its_items_met_ones_with_their_lines(self):
        # Given: two checklists, the first with an item met and one not, the second with one met
        # When: rn makes the report
        # Then: after Decided for you, each checklist is shown with its version and, under it,
        #   its own items, those met marked done with their lines, the other marked not done
        self.turn(
            list_={
                "checklists": [
                    {"checklist": "doc", "version": "0.2.0"},
                    {"checklist": "readme", "version": "0.3.0"},
                ],
                "items": [
                    {"id": "doc B-1", "title": "Purpose first"},
                    NOT_MET,
                    {"id": "readme B-1", "title": "First result"},
                ],
            },
            orchestrator={
                "doc B-1": {"met": True, "lines": "1-3"},
                "doc B-2": {"met": False},
                "readme B-1": {"met": True, "lines": "5, 9"},
            },
        )
        _, out = self.report({})
        self.assertEqual(
            out.split("\n\n")[1:3],
            [
                "doc 0.2.0\n  ✅ B-1 Purpose first: 1-3\n  ⬜ B-2 No question left",
                "readme 0.3.0\n  ✅ B-1 First result: 5, 9",
            ],
        )

    def test_the_list_and_the_orchestrators_decisions_are_read_from_the_folder_of_the_list(self):
        # Given: turn's CCS naming, before the list, other evidence in a folder of its own
        # When: rn makes the report
        # Then: it shows the checklist and the item of the list, as the orchestrator decided it
        self.turn(
            list_={
                "checklists": [{"checklist": "doc", "version": "0.2.0"}],
                "items": [{"id": "doc B-1", "title": "Purpose first"}],
            },
            orchestrator={"doc B-1": {"met": True, "lines": "1-3"}},
            episodic_trace=[{"evidence": ".turn/other/first-user.json"}, *TRACE],
        )
        _, out = self.report({})
        self.assertEqual(out.split("\n\n")[1], "doc 0.2.0\n  ✅ B-1 Purpose first: 1-3")

    def test_the_report_ends_with_the_document_and_its_content_file(self):
        # Given: turn's CCS for a document of two files and its content file
        # When: rn makes the report
        # Then: it ends with the document's files and the content file, and ends well
        self.turn(
            focal_entities=[{"deliverable": "README.md"}, {"deliverable": "docs/use.md"}],
            retrieved_artifacts=[{"content": "notes/README.content.md"}],
        )
        code, out = self.report({})
        self.assertEqual(code, 0)
        self.assertTrue(
            out.endswith(
                "\n\nThe document: README.md, docs/use.md\n"
                "What it says, item by item: notes/README.content.md\n"
            )
        )

    def test_a_report_with_nothing_for_the_caller_says_nothing_was_decided(self):
        # Given: turn's CCS with no question, item not met or rule, and empty judgments
        # When: rn makes the report
        # Then: under Decided for you it says Nothing
        self.turn()
        _, out = self.report({})
        self.assertEqual(out.split("\n\n")[0], "Decided for you\n  Nothing.")

    def test_an_item_turn_found_not_met_is_shown_unmet_whatever_the_judgments_say(self):
        # Given: an item turn found not met, judged by the caller as met after all
        # When: rn makes the report
        # Then: the item is shown unmet, without lines
        self.turn(
            list_={"checklists": [{"checklist": "doc", "version": "0.2.0"}], "items": [NOT_MET]},
            orchestrator={"doc B-2": {"met": False}},
            semantic_gist=[{"unmet": UNMET}],
        )
        _, out = self.report({"unmet": [{"item": "doc B-2", "judged": "met"}]})
        self.assertIn("\n  ⬜ B-2 No question left\n", out)

    def test_a_file_that_is_not_json_stops(self):
        # Given: turn's CCS or the judgments that is not JSON
        # When: rn is asked for the report
        # Then: rn stops, naming the file that is not JSON
        for broken, ccs in [("back.json", "not json\n"), ("judgments.json", "{}\n")]:
            with self.subTest(broken=broken):
                self.write("back.json", ccs)
                self.write("judgments.json", "not json\n")
                self.assertEqual(
                    self.rn("report", "back.json", "judgments.json"),
                    (1, f"{broken} is not JSON; give the file as turn or the conductor wrote it\n"),
                )

    def test_a_ccs_naming_no_evidence_stops(self):
        # Given: turn's CCS whose trace names no evidence
        # When: rn is asked for the report
        # Then: rn stops, saying turn was stopped, so there is no report to make
        self.write_json("back.json", {"episodic_trace": []})
        self.assertEqual(
            self.report({}),
            (
                1,
                "back.json names no evidence; turn was stopped, so there is no report to make; call turn again to get one\n",
            ),
        )

    def test_a_question_left_unjudged_stops(self):
        # Given: turn's CCS with a question the judgments do not judge
        # When: rn is asked for the report
        # Then: rn stops, saying to judge that question first
        self.turn(semantic_gist=[{"question": "Which port?"}])
        self.assertEqual(self.report({}), (1, "judge the question first: Which port?\n"))

    def test_an_item_left_unjudged_stops(self):
        # Given: turn's CCS with an item not met that the judgments do not judge
        # When: rn is asked for the report
        # Then: rn stops, saying to judge that item first
        self.turn(semantic_gist=[{"unmet": UNMET}])
        self.assertEqual(self.report({}), (1, "judge the item first: doc B-2\n"))


class TestLinesAsTheyStand(RepoTest):
    """The lines an item names are shown as they stand in the document handed back, mapped through
    what the conductor changed after turn."""

    def turn(self, kept, now, lines):
        self.write_json(
            "back.json",
            {
                "focal_entities": [{"deliverable": "README.md"}],
                "retrieved_artifacts": [],
                "semantic_gist": [],
                "episodic_trace": TRACE,
            },
        )
        self.write_json(
            EVIDENCE + "/list.json",
            {
                "checklists": [{"checklist": "doc", "version": "0.2.0"}],
                "items": [{"id": "doc B-1", "title": "Purpose first"}],
            },
        )
        self.write_json(EVIDENCE + "/orchestrator.json", {"doc B-1": {"met": True, "lines": lines}})
        if kept is not None:
            self.write(EVIDENCE + "/kept/README.md", kept)
        self.write("README.md", now)
        self.write_json("judgments.json", {})
        return self.rn("report", "back.json", "judgments.json")[1]

    def test_lines_below_an_insertion_move_down(self):
        # Given: the document as turn kept it, and a line put in above the item's lines since
        # When: rn makes the report
        # Then: the item's lines are shown where they now stand
        out = self.turn("a\nb\nc\n", "x\na\nb\nc\n", "2-3")
        self.assertIn("  ✅ B-1 Purpose first: 3-4\n", out)

    def test_lines_in_a_block_deleted_since_say_changed(self):
        # Given: the item's lines all taken out of the document since turn kept it
        # When: rn makes the report
        # Then: the item says its lines changed after turn
        out = self.turn("a\nb\nc\n", "a\n", "2-3")
        self.assertIn("  ✅ B-1 Purpose first: changed after turn\n", out)

    def test_lines_partly_deleted_show_what_survives(self):
        # Given: one of the item's lines taken out and the other left
        # When: rn makes the report
        # Then: the item shows the surviving line where it now stands
        out = self.turn("a\nb\nc\n", "a\nc\n", "2-3")
        self.assertIn("  ✅ B-1 Purpose first: 2\n", out)

    def test_an_unchanged_document_keeps_its_lines(self):
        # Given: the document as turn kept it, unchanged
        # When: rn makes the report
        # Then: the lines are as turn gave them, with a path kept when it named one
        out = self.turn("a\nb\nc\n", "a\nb\nc\n", "README.md:1-3")
        self.assertIn("  ✅ B-1 Purpose first: README.md:1-3\n", out)

    def test_without_the_kept_copy_lines_are_as_turn_read_them_and_the_report_says_so(self):
        # Given: no copy of the document as turn kept it
        # When: rn makes the report
        # Then: the lines are as turn gave them, and one line says so
        out = self.turn(None, "x\na\nb\nc\n", "2-3")
        self.assertIn("  Lines are as turn read the document.\n", out)
        self.assertIn("  ✅ B-1 Purpose first: 2-3\n", out)
