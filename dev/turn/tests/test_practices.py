"""How practices.py checks a best practice's form and makes the Markdown a person reads: the check
names each fault and each Markdown not as its JSON makes it, write puts the Markdown beside the
JSON, and sources names each ground whose page is not the one meant."""

import contextlib
import copy
import email.message
import http.client
import io
import json
import os
import runpy
import tempfile
import unittest
import urllib.error
import urllib.request
from typing import Any
from unittest import mock

import helpers  # noqa: F401  (puts turn's scripts on the path)
import practices

G = {"title": "T", "url": "https://x.example/t", "by": "X, 2020", "quote": "y"}
DATA = {
    "goal": "The reader gets it.",
    "parts": [{"id": "a", "what": "A.", "parts": [{"id": "b", "what": "B."}]}],
    "benefits": [
        {"id": "Q1", "about": "a", "what": "Does it?"},
        {"id": "Q2", "about": "b, the whole", "what": "After Q1, does all?"},
    ],
    "practices": [
        {"benefit": "Q1", "thinking": "Think.", "steps": ["Do."], "grounds": [G]},
        {"benefit": "Q2", "thinking": "Then.", "steps": [], "grounds": []},
    ],
}


def changed(change):
    data = copy.deepcopy(DATA)
    change(data)
    return practices.faults(data)


class Faults(unittest.TestCase):
    def test_a_sound_best_practice_has_none(self):
        self.assertEqual(practices.faults(DATA), [])

    def test_questions_out_of_number_order(self):
        def swap(d):
            d["benefits"].reverse()
            d["practices"].reverse()

        self.assertIn("questions are Q2, Q1, not numbered in order from Q1", changed(swap))

    def test_practices_not_in_the_questions_order(self):
        def swap(d):
            d["practices"].reverse()

        expected = "practices meet Q2, Q1, not each question once in its order"
        self.assertEqual(changed(swap), [expected])

    def test_a_question_with_no_method(self):
        def drop(d):
            d["practices"].pop()

        self.assertEqual(changed(drop), ["practices meet Q1, not each question once in its order"])

    def test_about_a_part_that_is_not_there(self):
        def wrong(d):
            d["benefits"][0]["about"] = "c"

        self.assertEqual(changed(wrong), ["Q1 is about c, which is no part"])

    def test_a_part_named_twice(self):
        def twice(d):
            d["parts"].append({"id": "a", "what": "Again."})

        self.assertEqual(changed(twice), ["part a is named more than once"])

    def test_a_ground_missing_a_field_or_with_no_https_link(self):
        def missing(d):
            d["practices"][0]["grounds"] = [dict(G, title=""), dict(G, url="x.example")]

        self.assertEqual(
            changed(missing),
            ["Q1 ground 1 has no title", "Q1 ground 2 links no https page"],
        )

    def test_a_question_named_in_the_text_that_is_not_there(self):
        def name(d):
            d["practices"][1]["thinking"] = "As Q3 says."

        self.assertEqual(changed(name), ["Q3 is named, but there is no such question"])

    def test_a_ground_naming_a_question_is_its_source_s_words(self):
        def quote(d):
            d["practices"][0]["grounds"] = [dict(G, quote="see Q9")]

        self.assertEqual(changed(quote), [])

    def test_a_part_no_question_is_about(self):
        def add(d):
            d["parts"].append({"id": "c", "what": "C."})

        self.assertEqual(changed(add), ["part c has no question about it"])

    def test_no_question_about_the_whole(self):
        def narrow(d):
            d["benefits"][1]["about"] = "b"

        self.assertEqual(changed(narrow), ["no question is about the whole"])

    def test_a_best_practice_of_one_question_about_the_whole(self):
        data = {
            "goal": "G.",
            "benefits": [{"id": "Q1", "about": "the whole", "what": "Does it?"}],
            "practices": [{"benefit": "Q1", "thinking": "T.", "steps": [], "grounds": []}],
        }
        self.assertEqual(practices.faults(data), [])

    def test_two_questions_of_one_number(self):
        def same(d):
            d["benefits"][1]["id"] = "Q1"
            d["practices"][1]["benefit"] = "Q1"

        self.assertIn("questions are Q1, Q1, not numbered in order from Q1", changed(same))

    def test_a_question_numbered_otherwise_is_not_named_as_missing(self):
        def letter(d):
            d["benefits"][0]["id"] = "A"
            d["practices"][0]["benefit"] = "A"

        self.assertEqual(
            changed(letter),
            [
                "questions are A, Q2, not numbered in order from Q1",
                "Q1 is named, but there is no such question",
            ],
        )

    def test_about_a_part_named_after_the_whole_that_is_not_there(self):
        def wrong(d):
            d["benefits"][0]["about"] = "z"

        self.assertEqual(changed(wrong), ["Q1 is about z, which is no part"])

    def test_a_question_named_in_a_benefit_that_is_not_there(self):
        def name(d):
            d["benefits"][0]["what"] = "Before Q3, does it?"

        self.assertEqual(changed(name), ["Q3 is named, but there is no such question"])

    def test_a_value_that_is_no_text_names_no_question(self):
        def number(d):
            d["parts"][0]["level"] = 3

        self.assertEqual(changed(number), [])


class Plain(unittest.TestCase):
    def test_reads_a_page_as_its_words(self):
        page = "<p>A <b>Bold</b> &amp; <code>`x`</code> \u201cquoted\u201d \u2014 "
        page += "it\u2019s <i>so</i> .</p>"
        self.assertEqual(practices.plain(page), 'a bold & x "quoted" - it\'s so.')

    def test_leaves_out_the_styles_and_scripts_a_browser_does_not_show(self):
        page = (
            '<h4>The product</h4><style>.a{b:c}</style><SCRIPT type="x">var d;</SCRIPT><p>helps</p>'
        )
        self.assertEqual(practices.plain(page), "the product helps")

    def test_joins_the_text_of_inline_tags_as_a_browser_shows_it(self):
        page = (
            '<pre><var class="var">program</var>:<var>file</var>:<code>n</code>: <em>m</em></pre>'
        )
        self.assertEqual(practices.plain(page), "program:file:n: m")
        page = '<a href="x">li</a><span>nk</span> <b>b</b><i>i</i><strong>s</strong>'
        self.assertEqual(practices.plain(page), "link bis")

    def test_keeps_the_text_of_blocks_apart(self):
        self.assertEqual(
            practices.plain("<p>one</p><p>two</p><li>three<br>four"), "one two three four"
        )


def response(kind, body):
    """What urlopen gives for a page of the kind and body, as a context manager."""
    answer = mock.MagicMock()
    answer.__enter__.return_value.headers.get.return_value = kind
    answer.__enter__.return_value.read.return_value = body
    return answer


def refused(test, code):
    """A server's refusal with the code, closed when the test ends, as urlopen's caller would."""
    error = urllib.error.HTTPError("https://x.example/t", code, "no", email.message.Message(), None)
    test.addCleanup(error.close)
    return error


class Fetch(unittest.TestCase):
    def setUp(self):
        practices.fetch.cache_clear()
        self.addCleanup(practices.fetch.cache_clear)
        self.sleep = mock.patch.object(practices.time, "sleep").start()
        self.addCleanup(mock.patch.stopall)

    def opened(self, *answers):
        return mock.patch.object(urllib.request, "urlopen", side_effect=answers)

    def test_gives_the_type_and_the_body_opening_each_page_once(self):
        with self.opened(response("text/html", b"page")) as urlopen:
            self.assertEqual(practices.fetch("https://x.example/t"), ("text/html", b"page"))
            self.assertEqual(practices.fetch("https://x.example/t"), ("text/html", b"page"))
        self.assertEqual(urlopen.call_count, 1)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://x.example/t")
        self.assertEqual(request.get_header("User-agent"), practices.AGENT)
        self.assertIn("practices.py", practices.AGENT)

    def test_reads_a_file_on_github_as_its_own_text(self):
        with self.opened(response("text/plain", b"file")) as urlopen:
            practices.fetch("https://github.com/o/r/blob/main/a/b.md")
        expected = "https://raw.githubusercontent.com/o/r/main/a/b.md"
        self.assertEqual(urlopen.call_args.args[0].full_url, expected)

    def test_asks_again_after_a_longer_wait_each_time_it_is_asked_to(self):
        page = response("text/html", b"page")
        with self.opened(*[refused(self, 429) for _ in range(3)], page) as urlopen:
            self.assertEqual(practices.fetch("https://x.example/t"), ("text/html", b"page"))
        self.assertEqual(urlopen.call_count, practices.TRIES)
        self.assertEqual(
            self.sleep.call_args_list,
            [
                mock.call(practices.WAIT),
                mock.call(2 * practices.WAIT),
                mock.call(3 * practices.WAIT),
            ],
        )

    def test_gives_up_after_its_tries(self):
        with (
            self.opened(*[refused(self, 429) for _ in range(practices.TRIES)]),
            self.assertRaises(urllib.error.HTTPError),
        ):
            practices.fetch("https://x.example/t")
        self.assertEqual(self.sleep.call_count, practices.TRIES - 1)

    def test_any_other_refusal_is_not_asked_again(self):
        for code in (404, 500):
            with self.subTest(code=code):
                practices.fetch.cache_clear()
                with (
                    self.opened(refused(self, code)) as urlopen,
                    self.assertRaises(urllib.error.HTTPError),
                ):
                    practices.fetch("https://x.example/t")
                self.assertEqual((urlopen.call_count, self.sleep.call_count), (1, 0))

    def test_waits_15_seconds_first_and_gives_a_page_30_seconds(self):
        page = response("text/html", b"page")
        with self.opened(refused(self, 429), page) as urlopen:
            practices.fetch("https://x.example/t")
        self.assertEqual(self.sleep.call_args_list, [mock.call(15)])
        self.assertEqual(urlopen.call_args.kwargs, {"timeout": 30})


def page(body, kind="text/html; charset=utf-8"):
    return lambda url: (kind, body.encode("utf-8"))


def failing(error):
    def get(url):
        raise error

    return get


class Sources(unittest.TestCase):
    def test_a_page_holding_its_title_and_words_is_the_one_meant(self):
        data = copy.deepcopy(DATA)
        data["practices"][0]["grounds"] = [dict(G, quote="it\u2019s so")]
        self.assertEqual(practices.sources(data, page("<title>T</title><p>It's so.</p>")), [])

    def test_a_page_not_holding_its_title_or_its_words(self):
        where = "Q1 ground 1 (https://x.example/t)"
        self.assertEqual(
            practices.sources(DATA, page("<p>none</p>")),
            [f"{where} does not hold its title", f"{where} does not hold its quote"],
        )

    def test_a_page_that_is_no_html_or_text_is_not_checked(self):
        where = "Q1 ground 1 (https://x.example/t)"
        self.assertEqual(
            practices.sources(DATA, page("", "application/pdf")),
            [f"{where} not checked: the page is application/pdf"],
        )
        self.assertEqual(
            practices.sources(DATA, page("", "")), [f"{where} not checked: the page is of no type"]
        )

    def test_a_page_of_xhtml_is_checked(self):
        self.assertEqual(practices.sources(DATA, page("T y", "application/xhtml+xml")), [])

    def test_each_way_a_page_fails_to_open(self):
        for error in (
            refused(self, 404),
            urllib.error.URLError("no such host"),
            TimeoutError("timed out"),
            ConnectionResetError("reset"),
            http.client.IncompleteRead(b""),
            http.client.InvalidURL("bad"),
        ):
            with self.subTest(error=error):
                found = practices.sources(DATA, failing(error))
                self.assertEqual(
                    found, [f"Q1 ground 1 (https://x.example/t) does not open: {error}"]
                )

    def test_each_ground_after_one_not_checked_is_checked(self):
        data = copy.deepcopy(DATA)
        data["practices"][0]["grounds"] = [G, dict(G, url="https://x.example/u")]
        for first, said in (
            (failing(TimeoutError("timed out")), "does not open: timed out"),
            (page("", "application/pdf"), "not checked: the page is application/pdf"),
        ):
            with self.subTest(said=said):

                def get(url, first=first):
                    return first(url) if url.endswith("/t") else ("text/html", b"<p>none</p>")

                found = practices.sources(data, get)
                self.assertEqual(found[0], f"Q1 ground 1 (https://x.example/t) {said}")
                self.assertIn("Q1 ground 2 (https://x.example/u) does not hold its title", found)

    def test_a_fault_of_the_script_is_not_taken_for_a_page_that_fails_to_open(self):
        with self.assertRaises(TypeError):
            practices.sources(DATA, failing(TypeError("a bug")))


class Markdown(unittest.TestCase):
    def test_holds_each_part_question_and_method_under_its_question(self):
        text = practices.markdown("kind", DATA)
        expected = ["# kind", "The reader gets it.", "## Parts", "- **a**: A.", "  - **b**: B."]
        expected += ["- **Q1** (a): Does it?", "### Q1: Does it?", "**Thinking**: Think."]
        expected += ["1. Do.", '- [T](https://x.example/t), X, 2020: "y"']
        for line in expected:
            self.assertIn(line, text)
        self.assertLess(text.index("## Benefits"), text.index("## Practices"))

    def test_sets_each_part_under_the_one_it_is_in(self):
        c: dict[str, Any] = {"id": "c", "what": "C."}
        b: dict[str, Any] = {"id": "b", "what": "B.", "parts": [c]}
        data = {**DATA, "parts": [{"id": "a", "what": "A.", "parts": [b]}]}
        lines = practices.markdown("kind", data).splitlines()
        start = lines.index("## Parts") + 2
        self.assertEqual(
            lines[start : start + 3], ["- **a**: A.", "  - **b**: B.", "    - **c**: C."]
        )

    def test_leaves_out_what_a_best_practice_has_none_of(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        text = practices.markdown("kind", data)
        self.assertNotIn("## Parts", text)
        self.assertEqual(text.count("**Steps**"), 1)
        self.assertEqual(text.count("**Grounds**"), 1)


class Main(unittest.TestCase):
    def test_check_fails_until_write_makes_the_markdown(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            self.assertEqual(practices.main(["check", path]), 1)
            self.assertEqual(practices.main(["write", path]), 0)
            self.assertEqual(practices.main(["check", path]), 0)

    def test_check_fails_on_a_fault_of_the_form(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            data = copy.deepcopy(DATA)
            data["practices"].pop()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            practices.main(["write", path])
            self.assertEqual(practices.main(["check", path]), 1)

    def test_check_fails_on_a_markdown_changed_by_hand(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            practices.main(["write", path])
            with open(os.path.join(folder, "kind.md"), "a", encoding="utf-8") as f:
                f.write("More.\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(practices.main(["check", path]), 1)
            self.assertIn("kind.md is not as its JSON makes it; run write", err.getvalue())

    def test_sources_fails_on_a_ground_whose_page_is_not_the_one_meant(self):
        practices.fetch.cache_clear()
        self.addCleanup(practices.fetch.cache_clear)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            err = io.StringIO()
            with (
                mock.patch.object(
                    urllib.request, "urlopen", return_value=response("text/html", b"T")
                ),
                contextlib.redirect_stderr(err),
            ):
                self.assertEqual(practices.main(["sources", path]), 1)
            expected = (
                f"practices.py: {path}: Q1 ground 1 (https://x.example/t) does not hold its quote"
            )
            self.assertEqual(err.getvalue(), expected + "\n")
            practices.fetch.cache_clear()
            with mock.patch.object(
                urllib.request, "urlopen", return_value=response("text/html", b"T y")
            ):
                self.assertEqual(practices.main(["sources", path]), 0)

    def written(self, folder, *names):
        """The paths of best practices of the names, DATA each, written in the folder."""
        paths = []
        for name in names:
            path = os.path.join(folder, f"{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            paths.append(path)
        return paths

    def test_write_and_check_take_each_best_practice_given(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = self.written(folder, "one", "two")
            self.assertEqual(practices.main(["write", *paths]), 0)
            for name in ("one", "two"):
                with open(os.path.join(folder, f"{name}.md"), encoding="utf-8") as f:
                    self.assertTrue(f.read().startswith(f"# {name}\n"))
            self.assertEqual(practices.main(["check", *paths]), 0)

    def test_check_fails_on_a_markdown_cut_short(self):
        with tempfile.TemporaryDirectory() as folder:
            (path,) = self.written(folder, "kind")
            practices.main(["write", path])
            md = os.path.join(folder, "kind.md")
            with open(md, encoding="utf-8") as f:
                text = f.read()
            with open(md, "w", encoding="utf-8") as f:
                f.write(text[:-2])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(practices.main(["check", path]), 1)

    def test_sources_takes_each_best_practice_given(self):
        practices.fetch.cache_clear()
        self.addCleanup(practices.fetch.cache_clear)
        with tempfile.TemporaryDirectory() as folder:
            paths = self.written(folder, "one", "two")
            err = io.StringIO()
            with (
                mock.patch.object(
                    urllib.request, "urlopen", return_value=response("text/html", b"T")
                ),
                contextlib.redirect_stderr(err),
            ):
                self.assertEqual(practices.main(["sources", *paths]), 1)
            for path in paths:
                self.assertIn(f"practices.py: {path}: ", err.getvalue())

    def test_refuses_an_unknown_command_or_one_given_no_best_practice(self):
        with tempfile.TemporaryDirectory() as folder:
            (path,) = self.written(folder, "kind")
            for argv in (["print"], ["check"], ["print", path]):
                with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(practices.main(argv), 2)

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        with tempfile.TemporaryDirectory() as folder:
            (path,) = self.written(folder, "kind")
            practices.main(["write", path])
            with (
                mock.patch.object(practices.sys, "argv", ["practices.py", "check", path]),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit) as end,
            ):
                runpy.run_path(practices.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
