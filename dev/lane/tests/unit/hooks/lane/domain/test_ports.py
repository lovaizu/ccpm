"""The cases of ports.py's contract: a text of the plugin read at the values, items, and steps
ports, in Lane's own form or through the plugin's adapter, as plugins/lane/docs/lanes.md gives the
ports."""

import json
import os

from helpers import ports, testing

ECHO = "import json, sys\nprint(json.dumps({given}))\n"


class AdapterTest(testing.FolderTest):
    def adapter(self, name, body):
        path = os.path.join(self.base, "hooks", "adapters", name)
        self.write(path, body)
        return f"hooks/adapters/{name}"


class TestValues(AdapterTest):
    def test_each_json_object_a_text_holds_gives_its_values(self):
        self.assertEqual(
            ports.values(['{"work": "a.md", "files": ["b", "c"]}']),
            {"work": ["a.md"], "files": ["b", "c"]},
        )

    def test_each_line_of_a_text_that_is_an_object_gives_its_values(self):
        self.assertEqual(ports.values(['Do it.\n{"work": "a.md"}\nThanks.']), {"work": ["a.md"]})

    def test_a_later_text_takes_the_place_of_an_earlier_one(self):
        self.assertEqual(ports.values(['{"work": "a"}', '{"work": "b"}']), {"work": ["b"]})

    def test_a_value_of_null_is_kept_as_null(self):
        self.assertEqual(ports.values(['{"work": null}']), {"work": None})

    def test_a_value_of_another_type_is_none_of_lanes(self):
        self.assertEqual(ports.values(['{"work": 1, "a": [1], "b": "x"}']), {"b": ["x"]})

    def test_a_text_that_holds_no_object_gives_none(self):
        self.assertEqual(ports.values(["Write the entries.", "[1]"]), {})

    def test_an_adapter_gives_the_values_in_place_of_lanes_own_form(self):
        path = self.adapter(
            "values-w.py",
            "import json, sys\n"
            't = json.load(sys.stdin)["texts"]\n'
            'print(json.dumps({"values": {"work": t}}))\n',
        )
        self.assertEqual(ports.values(["p", "m"], self.base, path), {"work": ["p", "m"]})


class TestItems(AdapterTest):
    def test_lanes_own_form_reads_the_items_of_the_text(self):
        self.assertEqual(ports.items("r.md", "- B-1 x\n", {}), ["B-1"])

    def test_an_adapter_is_given_the_input_its_text_and_the_values(self):
        body = (
            "import json, sys\n"
            "g = json.load(sys.stdin)\n"
            'print(json.dumps({"items": [g["input"], g["text"], *g["values"]["v"]]}))\n'
        )
        path = self.adapter("items-w.py", body)
        self.assertEqual(
            ports.items("r.md", "t", {"v": ["x"]}, self.base, path), ["r.md", "t", "x"]
        )


class TestSteps(AdapterTest):
    def test_an_adapter_gives_its_step_lists(self):
        lists = {
            "lists": [
                {
                    "list": "Q1",
                    "steps": [{"says": "Run.", "lanes": [{"lane": "run_step", "takes": ["make"]}]}],
                }
            ]
        }
        path = self.adapter("steps-w.py", ECHO.format(given=repr(lists)))
        self.assertEqual(ports.steps({}, self.base, path), lists["lists"])


class TestAdapterFaults(AdapterTest):
    def test_an_adapter_that_fails_cannot_be_read(self):
        path = self.adapter("values-w.py", "import sys\nsys.exit('broken')\n")
        with self.assertRaisesRegex(
            ports.Unported, r"hooks/adapters/values-w\.py exited with 1: broken"
        ):
            ports.values([], self.base, path)

    def test_an_adapter_that_gives_no_json_cannot_be_read(self):
        path = self.adapter("values-w.py", "print('hi')\n")
        with self.assertRaisesRegex(ports.Unported, r"values-w\.py gave no JSON: "):
            ports.values([], self.base, path)

    def test_an_adapter_answering_out_of_its_port_cannot_be_read(self):
        path = self.adapter("values-w.py", "print('{\"values\": 1}')\n")
        with self.assertRaisesRegex(
            ports.Unported,
            r"values-w\.py answered out of the values port: \$\.values: expected an object,"
            r" found 1",
        ):
            ports.values([], self.base, path)

    def test_an_adapter_that_isnt_there_cannot_be_read(self):
        with self.assertRaisesRegex(ports.Unported, r"hooks/adapters/gone\.py isn't there"):
            ports.values([], self.base, "hooks/adapters/gone.py")

    def test_an_adapter_with_no_answer_in_time_cannot_be_read(self):
        path = self.adapter("values-w.py", "import time\ntime.sleep(5)\n")
        with self.assertRaisesRegex(
            ports.Unported, r"values-w\.py gave no answer within 0\.2 seconds"
        ):
            ports.run(self.base, path, "values", {"texts": []}, 0.2)

    def test_an_adapter_finds_the_plugin_by_its_folder(self):
        body = (
            "import json, os\n"
            'print(json.dumps({"values": {"root": [os.environ["CLAUDE_PLUGIN_ROOT"]]}}))\n'
        )
        path = self.adapter("values-w.py", body)
        self.assertEqual(ports.values([], self.base, path), {"root": [self.base]})


class TestCases(AdapterTest):
    def cases(self, cases):
        self.write(os.path.join(self.base, "hooks", "adapters", "values-w.json"), json.dumps(cases))

    def test_an_adapter_that_gives_each_case_has_no_fault(self):
        path = self.adapter(
            "values-w.py",
            "import json, sys\n"
            'given = json.load(sys.stdin)["texts"]\n'
            'print(json.dumps({"values": {"a": ["b"]} if given else {}}))\n',
        )
        self.cases(
            [
                {"given": {"texts": ["x"]}, "gives": {"values": {"a": ["b"]}}},
                {"given": {"texts": []}, "gives": {"values": {}}},
            ]
        )
        self.assertEqual(ports.tried(self.base, path)[1], [])

    def test_a_case_the_adapter_gives_otherwise_is_a_fault(self):
        path = self.adapter("values-w.py", "print('{\"values\": {}}')\n")
        self.cases(
            [
                {"given": {"texts": ["x"]}, "gives": {"values": {"a": ["b"]}}},
                {"given": {"texts": []}, "gives": {"values": {}}},
            ]
        )
        self.assertEqual(
            ports.tried(self.base, path)[1],
            [
                (
                    'hooks/adapters/values-w.py gives {"values": {}} for case 1, where its cases'
                    " say"
                    ' {"values": {"a": ["b"]}}'
                )
            ],
        )

    def test_a_case_the_adapter_fails_on_is_a_fault(self):
        path = self.adapter("values-w.py", "import sys\nsys.exit(2)\n")
        self.cases([{"given": {"texts": []}, "gives": {"values": {}}}])
        self.assertEqual(
            ports.tried(self.base, path)[1], ["hooks/adapters/values-w.py exited with 2: "]
        )

    def test_cases_with_none_that_gives_nothing_are_a_fault(self):
        path = self.adapter("values-w.py", 'print(\'{"values": {"a": ["b"]}}\')\n')
        self.cases([{"given": {"texts": ["x"]}, "gives": {"values": {"a": ["b"]}}}])
        self.assertEqual(
            ports.tried(self.base, path)[1],
            ["hooks/adapters/values-w.json holds no case that gives nothing"],
        )

    def test_an_adapter_with_no_cases_is_a_fault(self):
        path = self.adapter("values-w.py", "")
        self.assertEqual(
            ports.tried(self.base, path)[1],
            ["hooks/adapters/values-w.json isn't there, which holds the adapter's cases"],
        )

    def test_cases_out_of_their_form_are_a_fault(self):
        path = self.adapter("values-w.py", "")
        self.cases([{"given": {"texts": 1}, "gives": {"values": {}}}])
        self.assertEqual(
            ports.tried(self.base, path)[1],
            [
                (
                    "hooks/adapters/values-w.json is out of its form: $[0].given.texts: expected an"
                    " array, found 1"
                )
            ],
        )

    def test_an_adapter_named_for_no_port_is_a_fault(self):
        self.assertEqual(
            ports.tried(self.base, "hooks/adapters/w.py")[1],
            [
                (
                    "hooks/adapters/w.py isn't named hooks/adapters/<port>-<name>.py for the"
                    " values,"
                    " items or steps port"
                )
            ],
        )
