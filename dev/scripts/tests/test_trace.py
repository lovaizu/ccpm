"""The tests of dev/scripts/trace.py: it reads the elements of a plugin's architecture, the key
results of its product vision, and the names that each of its test cases supports, and reports each
case that names nothing one level up and each element that no integration case names; it reads
each double's records and the lines the double names, and the pages that the lines taken from the
documentation name, as the Integration tests of each architecture's Test strategy set. Each test
runs it as check.sh or quality.sh does, on a plugin `p` that the test sets up in its own folder."""

from __future__ import annotations

import http.server
import json
import os
import subprocess
import sys
import threading

from helpers import TOP, FolderTest

SCRIPT = os.path.join(TOP, "dev", "scripts", "trace.py")
USAGE = "usage: trace.py check <plugin> | doubles | sources"

ARCHITECTURE = """\
# `p` architecture

This document says how the parts of `p` give what its README promises.

## User stories

- S1: the user wants to type `/p:up`, so that they get the work. It carries the request.
- S2: the user wants to stop, so that they lose nothing. It carries the pause.

## Components

![p's components](images/components.svg)

What each decides alone:

- user\\
  The goal.
- tree.py\\
  The tree's form.

The choices made, and why:

- One generator over several\\
  It's quicker. The cost: none.

## Data model

![p's data](images/data-model.svg)

- Cut\\
  The part of the tree that a role starts with.

## Principles

`p` builds on the plugin guide, and adds these rules, which every part keeps.

### The repository holds the work

Every part keeps the state in the run's folder.

*Why*: work kept in a conversation is lost.

## Sequences

### S1: a request

## Test strategy

- Tries: each story.
"""

DATA_MODEL = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
  <text class="frame-name" x="1" y="1">the design tree</text>
  <text class="name" x="1" y="2" text-anchor="middle">Cut</text>
  <text class="label small halo" x="1" y="3">cut from</text>
  <text class="name" x="1" y="4">Lack&#x27;s kept</text>
</svg>
"""

PRODUCT_VISION = """\
# Product vision of p

## Objectives and key results

- O1: the user gets each deliverable they mean.
  - KR1.1: the share of the deliverables that its people couldn't use. Lower is better.
  - KR1.2: the time from the request to the deliverable. Shorter is better.
"""

# Every element of ARCHITECTURE and DATA_MODEL, as an integration case names it.
ELEMENTS = ["S1", "S2", "user", "tree.py", "Cut", "Lack's kept", "The repository holds the work"]


def case(name: str, *supports: str) -> str:
    """A test function of the name, marked as supporting each name given."""
    marks = "".join(f"@pytest.mark.supports({each!r})\n" for each in supports)
    return f"{marks}def {name}():\n    pass\n\n\n"


def principle_case(name: str, principle: str, body: str = "assert not broken") -> str:
    """A test function of the name that supports the principle and takes the fixture `broken`,
    with the body."""
    return f"@pytest.mark.supports({principle!r})\ndef {name}(broken):\n    {body}\n\n\n"


def cases_file(*cases: str) -> str:
    """A test file that holds the cases."""
    return "import pytest\n\n\n" + "".join(cases)


# The fixture `broken` of the plugin guide's form, which here takes out nothing and only says
# whether trace.py runs the case with the part taken out.
BROKEN = """\
import os

import pytest


@pytest.fixture
def broken():
    return os.environ.get("TRACE_BROKEN") == "1"
"""
PRINCIPLE = "The repository holds the work"


class TraceTest(FolderTest):
    """A plugin `p` whose architecture, product vision, and data model the test may change, and
    whose cases it writes."""

    def setUp(self) -> None:
        super().setUp()
        self.write("dev/p/architecture.md", ARCHITECTURE)
        self.write("dev/p/images/data-model.svg", DATA_MODEL)
        self.write("dev/p/product-vision.md", PRODUCT_VISION)

    def every_element_named(self) -> None:
        """Writes an integration case for each element, so that only what a test adds fails."""
        named = [case(f"test_{n}", each) for n, each in enumerate(ELEMENTS) if each != PRINCIPLE]
        named.append(principle_case("test_principle", PRINCIPLE))
        self.write("dev/p/tests/integration/test_all.py", cases_file(*named))
        self.write("dev/p/tests/integration/conftest.py", BROKEN)

    def trace(self, *argv: str) -> subprocess.CompletedProcess[str]:
        """What `trace.py` gives, run from the top of the test's repository."""
        command = [sys.executable, SCRIPT, *(argv or ("check", "p"))]
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def fails_with(self, code: int, *words: str) -> str:
        """Runs `trace.py check p`, and checks that it exits with the code and says each word."""
        result = self.trace()
        self.assertEqual(result.returncode, code, result.stderr)
        for word in words:
            self.assertIn(word, result.stderr)
        return result.stderr


class CommandTest(TraceTest):
    """trace.py takes `check <plugin>` alone, and refuses what it can't read, as no check passes
    what it didn't check."""

    def test_every_element_named_and_every_name_found_gives_0(self):
        self.every_element_named()
        result = self.trace()
        self.assertEqual((result.returncode, result.stderr), (0, ""))

    def test_a_command_it_does_not_take_gives_2_with_its_usage(self):
        for argv in (
            ("fix", "p"),
            ("check",),
            ("check", "p", "q"),
            ("doubles", "p"),
            ("sources", "p"),
        ):
            result = self.trace(*argv)
            self.assertEqual((result.returncode, result.stderr), (2, f"{USAGE}\n"), argv)

    def test_a_plugin_without_an_architecture_gives_2(self):
        result = self.trace("check", "q")
        self.assertEqual(result.returncode, 2)
        self.assertIn("dev/q/architecture.md", result.stderr)

    def test_an_architecture_without_a_section_gives_2(self):
        self.write("dev/p/architecture.md", ARCHITECTURE.replace("## Principles", "## Rules"))
        self.fails_with(2, "dev/p/architecture.md", "## Principles")

    def test_components_without_the_list_of_what_each_decides_gives_2(self):
        self.write("dev/p/architecture.md", ARCHITECTURE.replace("What each decides alone:", ""))
        self.fails_with(2, "dev/p/architecture.md", "What each decides alone:")

    def test_a_missing_data_model_gives_2(self):
        os.remove("dev/p/images/data-model.svg")
        self.fails_with(2, "dev/p/images/data-model.svg")

    def test_a_data_model_that_is_not_xml_gives_2(self):
        self.write("dev/p/images/data-model.svg", "<svg><text class='name'>Cut</svg>")
        self.fails_with(2, "dev/p/images/data-model.svg")

    def test_a_missing_product_vision_gives_2(self):
        os.remove("dev/p/product-vision.md")
        self.fails_with(2, "dev/p/product-vision.md")

    def test_a_test_file_that_python_cannot_parse_gives_2(self):
        self.every_element_named()
        self.write("dev/p/tests/unit/test_x.py", "def test_x(:\n")
        self.fails_with(2, "dev/p/tests/unit/test_x.py:1")


class ElementTest(TraceTest):
    """Every story, principle, component, and kind of data of the architecture has an integration
    test that names it, as each architecture's Integration tests set."""

    def test_without_any_case_every_element_is_reported(self):
        stderr = self.fails_with(1, *(f"{each} has no integration test" for each in ELEMENTS))
        self.assertEqual(stderr.count("has no integration test"), len(ELEMENTS), stderr)

    def test_a_story_that_no_case_names_is_reported_at_its_line(self):
        self.every_element_named()
        self.write("dev/p/architecture.md", ARCHITECTURE.replace("- S2:", "- S3: more.\n- S2:"))
        self.fails_with(1, "dev/p/architecture.md:8: story S3 has no integration test")

    def test_a_principle_that_no_case_names_is_reported(self):
        self.every_element_named()
        added = ARCHITECTURE.replace("## Sequences", "### One source\n\nA rule.\n\n## Sequences")
        self.write("dev/p/architecture.md", added)
        self.fails_with(1, "principle One source has no integration test")

    def test_a_component_that_no_case_names_is_reported(self):
        self.every_element_named()
        added = ARCHITECTURE.replace("- tree.py\\", "- guard\\\n  Each call.\n- tree.py\\")
        self.write("dev/p/architecture.md", added)
        self.fails_with(1, "component guard has no integration test")

    def test_components_without_choices_are_each_read(self):
        self.every_element_named()
        choices = "The choices made, and why:\n\n- One generator over several\\\n"
        bare = ARCHITECTURE.replace(choices + "  It's quicker. The cost: none.\n\n", "")
        last = bare.replace("## Data model", "- guard\\\n  Each call.\n\n## Data model")
        self.write("dev/p/architecture.md", last)
        self.fails_with(1, "component guard has no integration test")

    def test_a_kind_of_data_that_no_case_names_is_reported(self):
        self.every_element_named()
        added = DATA_MODEL.replace("</svg>", '<text class="name">Place</text></svg>')
        self.write("dev/p/images/data-model.svg", added)
        self.fails_with(1, "dev/p/images/data-model.svg: kind of data Place has no integration")

    def test_a_frame_label_or_choice_is_no_element(self):
        self.every_element_named()
        added = DATA_MODEL.replace("</svg>", '<text class="name">Place</text></svg>')
        self.write("dev/p/images/data-model.svg", added)
        stderr = self.fails_with(1, "Place")
        for word in ("the design tree", "cut from", "One generator"):
            self.assertNotIn(word, stderr)

    def test_a_case_of_another_level_names_no_element(self):
        named = [case(f"test_{n}", each) for n, each in enumerate(ELEMENTS)]
        self.write("dev/p/tests/e2e/test_all.py", cases_file(*named))
        self.fails_with(1, "story S1 has no integration test")


class NameTest(TraceTest):
    """Every test names an element or a case one level up that exists, and every unit case names an
    integration case, as each architecture's Integration tests set."""

    def test_a_case_without_a_mark_names_nothing(self):
        self.every_element_named()
        self.write("dev/p/tests/integration/test_x.py", "def test_bare():\n    pass\n")
        self.fails_with(1, "dev/p/tests/integration/test_x.py:1: test_bare names nothing")

    def test_an_integration_case_naming_no_element_is_reported(self):
        self.every_element_named()
        self.write("dev/p/tests/integration/test_x.py", cases_file(case("test_x", "S9")))
        self.fails_with(1, "test_x.py:4: test_x names S9, which is no story, principle")

    def test_a_unit_case_naming_an_integration_case_passes(self):
        self.every_element_named()
        for level in ("unit", "properties", "prompts"):
            self.write(f"dev/p/tests/{level}/test_x.py", cases_file(case("test_x", "test_0")))
        self.assertEqual(self.trace().returncode, 0, self.trace().stderr)

    def test_a_unit_case_naming_an_element_is_reported(self):
        self.every_element_named()
        for level in ("unit", "properties", "prompts"):
            self.write(f"dev/p/tests/{level}/test_x.py", cases_file(case("test_x", "S1")))
        stderr = self.fails_with(1, "names S1, which is no integration case")
        for level in ("unit", "properties", "prompts"):
            self.assertIn(f"dev/p/tests/{level}/test_x.py:4", stderr)

    def test_an_e2e_case_naming_a_key_result_passes(self):
        self.every_element_named()
        self.write("dev/p/tests/e2e/test_x.py", cases_file(case("test_x", "KR1.2")))
        self.assertEqual(self.trace().returncode, 0, self.trace().stderr)

    def test_an_e2e_case_naming_no_key_result_is_reported(self):
        self.every_element_named()
        self.write("dev/p/tests/e2e/test_x.py", cases_file(case("test_x", "KR2.1")))
        self.fails_with(1, "names KR2.1, which is no key result of dev/p/product-vision.md")

    def test_a_case_naming_two_reports_each_that_leads_nowhere(self):
        self.every_element_named()
        self.write("dev/p/tests/integration/test_x.py", cases_file(case("test_x", "S1", "S9")))
        stderr = self.fails_with(1, "names S9")
        self.assertNotIn("names S1", stderr)

    def test_a_case_in_a_class_is_read_and_a_helper_is_not(self):
        self.every_element_named()
        body = (
            "import pytest\n\n\nclass TestX:\n    def helper(self):\n        pass\n\n"
            "    @pytest.mark.supports('S9')\n    def test_x(self):\n        pass\n"
        )
        self.write("dev/p/tests/integration/test_x.py", body)
        stderr = self.fails_with(1, "test_x.py:8: test_x names S9")
        self.assertNotIn("helper", stderr)

    def test_a_mark_from_mark_alone_is_read(self):
        self.every_element_named()
        body = "from pytest import mark\n\n\n@mark.supports('S9')\ndef test_x():\n    pass\n"
        self.write("dev/p/tests/integration/test_x.py", body)
        self.fails_with(1, "test_x.py:4: test_x names S9")

    def test_another_mark_or_decorator_names_nothing(self):
        self.every_element_named()
        body = (
            "import functools\nimport pytest\n\n\n@pytest.mark.slow\n@functools.cache\n"
            "@pytest.mark.parametrize('S1', [1])\ndef test_x():\n    pass\n"
        )
        self.write("dev/p/tests/integration/test_x.py", body)
        self.fails_with(1, "test_x.py:5: test_x names nothing")

    def test_a_mark_whose_name_is_not_written_out_is_reported(self):
        self.every_element_named()
        body = "import pytest\n\nS = 'S1'\n\n\n@pytest.mark.supports(S)\ndef test_x():\n    pass\n"
        self.write("dev/p/tests/integration/test_x.py", body)
        self.fails_with(1, "test_x.py:6: test_x names a value that isn't written out")

    def test_a_test_file_outside_every_level_is_reported(self):
        self.every_element_named()
        self.write("dev/p/tests/test_x.py", cases_file(case("test_x", "S1")))
        self.write("dev/p/tests/misc/test_y.py", cases_file(case("test_y", "S1")))
        self.write("dev/p/tests/integration/helpers.py", "def test_like():\n    pass\n")
        stderr = self.fails_with(1, "dev/p/tests/test_x.py: lies in no level's folder")
        self.assertIn("dev/p/tests/misc/test_y.py: lies in no level's folder", stderr)
        self.assertNotIn("helpers.py", stderr)


class BrokenTest(TraceTest):
    """Each test of a principle fails where its fixture `broken` takes out the part that holds the
    principle, which trace.py runs, as each architecture's Integration tests set."""

    def test_a_principle_case_that_fails_with_the_part_taken_out_passes(self):
        self.every_element_named()
        self.write(
            "dev/p/tests/integration/test_x.py", cases_file(principle_case("test_x", PRINCIPLE))
        )
        result = self.trace()
        self.assertEqual((result.returncode, result.stderr), (0, ""))

    def test_a_principle_case_that_passes_with_the_part_taken_out_is_reported(self):
        self.every_element_named()
        passing = principle_case("test_x", PRINCIPLE, "pass")
        self.write("dev/p/tests/integration/test_x.py", cases_file(passing))
        self.fails_with(1, "test_x.py:4: test_x doesn't fail with TRACE_BROKEN=1")

    def test_a_principle_case_marked_xfail_that_passes_with_the_part_taken_out_is_reported(self):
        self.every_element_named()
        marked = "pytestmark = pytest.mark.xfail(strict=True, reason='unbuilt')\n\n\n"
        passing = principle_case("test_x", PRINCIPLE, "assert broken")
        self.write("dev/p/tests/integration/test_x.py", cases_file(marked, passing))
        self.fails_with(1, "test_x.py:7: test_x doesn't fail with TRACE_BROKEN=1")

    def test_a_principle_case_marked_xfail_that_fails_with_the_part_taken_out_passes(self):
        self.every_element_named()
        marked = "pytestmark = pytest.mark.xfail(strict=True, reason='unbuilt')\n\n\n"
        self.write(
            "dev/p/tests/integration/test_x.py",
            cases_file(marked, principle_case("test_x", PRINCIPLE)),
        )
        result = self.trace()
        self.assertEqual((result.returncode, result.stderr), (0, ""))

    def test_a_principle_case_without_the_fixture_is_reported(self):
        self.every_element_named()
        self.write("dev/p/tests/integration/test_x.py", cases_file(case("test_x", PRINCIPLE)))
        self.fails_with(1, "test_x.py:4: test_x names a principle but takes no fixture broken")

    def test_a_principle_case_in_a_class_is_run_by_its_class(self):
        self.every_element_named()
        body = (
            "import pytest\n\n\nclass TestX:\n    @pytest.mark.supports(" + repr(PRINCIPLE) + ")\n"
            "    def test_x(self, broken):\n        pass\n"
        )
        self.write("dev/p/tests/integration/test_x.py", body)
        self.fails_with(1, "test_x.py:5: test_x doesn't fail with TRACE_BROKEN=1")

    def test_a_principle_case_that_pytest_cannot_run_gives_2(self):
        self.every_element_named()
        file = "import nowhere\n" + cases_file(principle_case("test_x", PRINCIPLE))
        self.write("dev/p/tests/integration/test_x.py", file)
        self.fails_with(2, "dev/p/tests/integration/test_x.py::test_x", "pytest")

    def test_a_principle_case_without_pytest_to_run_it_gives_2(self):
        self.every_element_named()
        self.write("nopytest/pytest/__init__.py", "")
        self.write("nopytest/pytest/__main__.py", "raise SystemExit(1)\n")
        command = [sys.executable, SCRIPT, "check", "p"]
        env = dict(os.environ, PYTHONPATH=os.path.join(self.base, "nopytest"))
        result = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("test_all.py::test_principle: pytest couldn't run it, exit 1", result.stderr)


# A double of the test's own, which takes each line by `line` or `lines`, its record by a name the
# module sets or as a string.
DOUBLE = """\
RUN = "thing-1.0.jsonl"


def line(record, event):
    pass


def lines(record, first, last):
    pass


def act():
    line(RUN, "it starts")
    lines("thing-1.0.jsonl", "it starts", "it ends")
    line("thing-reference.jsonl", "a call's input")
"""
RUN_RECORD = [{"event": "it starts", "payload": {}}, {"event": "it ends", "payload": {}}]
SHOWS = "Edit Replaces a string in an existing file."
REFERENCE_LINE = {
    "event": "a call's input",
    "source": "https://example.com/docs/hooks#input",
    "shows": SHOWS,
    "tool_input": {},
}


class RecordedTest(TraceTest):
    """A double of the test's own beside its records, a recorded run and lines taken from the
    documentation."""

    def setUp(self) -> None:
        super().setUp()
        self.write("dev/tests/claude_code.py", DOUBLE)
        self.record("thing-1.0.jsonl", *RUN_RECORD)
        self.record("thing-reference.jsonl", REFERENCE_LINE)

    def record(self, name: str, *found: dict) -> None:
        """Writes the lines as the record of the name in dev/tests/recorded/."""
        self.write(f"dev/tests/recorded/{name}", "".join(json.dumps(r) + "\n" for r in found))


class DoublesTest(RecordedTest):
    """Each result of a double names the recorded run or the page of the documentation that shows
    it, which trace.py checks against that source, as each architecture's Integration tests set:
    the part that needs no network, which check.sh runs."""

    def doubles(self, code: int, *words: str) -> str:
        """Runs `trace.py doubles`, and checks that it exits with the code and says each word."""
        result = self.trace("doubles")
        self.assertEqual(result.returncode, code, result.stderr)
        for word in words:
            self.assertIn(word, result.stderr)
        return result.stderr

    def test_every_line_named_and_every_source_named_gives_0(self):
        self.assertEqual(self.doubles(0), "")

    def test_an_event_that_the_record_lacks_is_reported(self):
        self.write("dev/tests/claude_code.py", DOUBLE.replace('(RUN, "it starts")', '(RUN, "x")'))
        self.doubles(1, "dev/tests/claude_code.py:13: names 'x', which", "holds no line of")

    def test_each_event_of_a_run_of_lines_is_checked(self):
        self.write("dev/tests/claude_code.py", DOUBLE.replace('"it ends")', '"it stops")'))
        self.doubles(1, "claude_code.py:14: names 'it stops'")

    def test_a_record_that_is_not_there_is_reported(self):
        self.write(
            "dev/tests/claude_code.py", DOUBLE.replace('RUN = "thing-1.0', 'RUN = "thing-2.0')
        )
        self.doubles(1, "claude_code.py:13: names dev/tests/recorded/thing-2.0.jsonl, which isn't")

    def test_a_name_not_written_out_is_reported(self):
        self.write("dev/tests/claude_code.py", DOUBLE.replace('(RUN, "it starts")', "(RUN, act)"))
        self.doubles(1, "claude_code.py:13: names a record or an event that isn't written out")

    def test_a_call_with_the_wrong_number_of_names_is_reported(self):
        self.write("dev/tests/claude_code.py", DOUBLE.replace('(RUN, "it starts")', "(RUN)"))
        self.doubles(1, "claude_code.py:13: line takes a record and an event")

    def test_a_test_file_beside_the_records_is_no_double(self):
        self.write("dev/tests/test_claude_code.py", 'line("thing-1.0.jsonl", "x")\n')
        self.assertEqual(self.doubles(0), "")

    def test_a_double_of_a_plugins_own_tests_is_read(self):
        self.write("dev/p/tests/integration/gh.py", 'line("gh-2.0.jsonl", "x")\n')
        self.write("dev/p/tests/integration/recorded/gh-2.0.jsonl", '{"event": "y"}\n')
        self.doubles(1, "dev/p/tests/integration/gh.py:1: names 'x'")

    def test_a_line_that_is_not_a_json_object_is_reported(self):
        self.write("dev/tests/recorded/thing-1.0.jsonl", '{"event": "it starts"}\n[1]\n{\n')
        stderr = self.doubles(1, "dev/tests/recorded/thing-1.0.jsonl:2: isn't a JSON object")
        self.assertIn("thing-1.0.jsonl:3: isn't a JSON object", stderr)

    def test_a_line_without_an_event_is_reported(self):
        self.record("thing-1.0.jsonl", *RUN_RECORD, {"payload": {}})
        self.doubles(1, "thing-1.0.jsonl:3: names no event")

    def test_two_lines_of_one_event_are_reported(self):
        self.record("thing-1.0.jsonl", *RUN_RECORD, RUN_RECORD[0])
        self.doubles(1, "thing-1.0.jsonl:3: names the event 'it starts', as line 1 does")

    def test_a_line_outside_a_run_without_its_source_is_reported(self):
        self.record("thing-reference.jsonl", {"event": "a call's input", "tool_input": {}})
        self.doubles(1, "thing-reference.jsonl:1: comes from no recorded run")

    def test_a_source_that_is_not_a_url_is_reported(self):
        self.record("thing-reference.jsonl", dict(REFERENCE_LINE, source="the hooks reference"))
        self.doubles(1, "thing-reference.jsonl:1: its source isn't a URL")

    def test_a_source_without_its_words_is_reported(self):
        self.record("thing-reference.jsonl", dict(REFERENCE_LINE, shows=""))
        self.doubles(1, "thing-reference.jsonl:1: carries no shows")


class Page(http.server.BaseHTTPRequestHandler):
    """A page of documentation, which shows the words in a table, as the hooks reference does."""

    def do_GET(self) -> None:
        body = (
            b"<html><script>var x = 1;</script><h2>Edit</h2>\n<p>Replaces a string in an\n"
            b"<em>existing</em> file.</p></html>"
        )
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


class SourcesTest(RecordedTest):
    """Each line taken from the documentation shows words that its page holds, which trace.py
    sources checks in CI, as quality.sh runs it."""

    def setUp(self) -> None:
        super().setUp()
        server = http.server.HTTPServer(("127.0.0.1", 0), Page)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.url = f"http://127.0.0.1:{server.server_address[1]}/docs#input"

    def sources(self, code: int, *words: str) -> str:
        """Runs `trace.py sources`, and checks that it exits with the code and says each word."""
        result = self.trace("sources")
        self.assertEqual(result.returncode, code, result.stderr)
        for word in words:
            self.assertIn(word, result.stderr)
        return result.stderr

    def test_words_that_the_page_shows_give_0(self):
        self.record("thing-reference.jsonl", dict(REFERENCE_LINE, source=self.url))
        self.assertEqual(self.sources(0), "")

    def test_words_that_the_page_does_not_show_are_reported(self):
        self.record("thing-reference.jsonl", dict(REFERENCE_LINE, source=self.url, shows="Read"))
        self.sources(1, f"thing-reference.jsonl:1: {self.url} doesn't show 'Read'")

    def test_a_page_that_cannot_be_read_gives_2(self):
        gone = "http://127.0.0.1:9/docs"
        self.record("thing-reference.jsonl", dict(REFERENCE_LINE, source=gone))
        self.sources(2, f"trace.py: {gone}: can't be read")

    def test_each_line_from_one_page_is_checked(self):
        other = dict(REFERENCE_LINE, event="another input", source=self.url, shows="Read")
        self.record("thing-reference.jsonl", dict(REFERENCE_LINE, source=self.url), other)
        self.sources(1, f"thing-reference.jsonl:2: {self.url} doesn't show 'Read'")
