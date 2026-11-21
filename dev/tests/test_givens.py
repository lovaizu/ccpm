"""The cases of the keeping of Givens: a Given played once for a bench root and its arguments, and
its bench's files and what it gave given back to each case after."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from dataclasses import dataclass
from typing import Any

from givens import kept


@dataclass
class Bench:
    root: str
    givens: str | None


@kept
def written(bench: Bench, text: str) -> dict[str, Any]:
    """Writes the text to note.txt under the bench's root, and counts each play in plays.txt
    beside the bench, which no copy of the bench holds."""
    with open(os.path.join(bench.root, "note.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    with open(os.path.join(os.path.dirname(bench.root), "plays.txt"), "a", encoding="utf-8") as f:
        f.write(f"{text}\n")
    return {"text": text}


class KeptTest(unittest.TestCase):
    def bench(self, keeps: bool = True) -> Bench:
        top = os.path.realpath(tempfile.mkdtemp(prefix="givens-"))
        self.addCleanup(shutil.rmtree, top)
        os.makedirs(os.path.join(top, "bench"))
        return Bench(os.path.join(top, "bench"), os.path.join(top, "givens") if keeps else None)

    def plays(self, bench: Bench) -> str:
        with open(os.path.join(os.path.dirname(bench.root), "plays.txt"), encoding="utf-8") as f:
            return f.read()

    def note(self, bench: Bench) -> str:
        with open(os.path.join(bench.root, "note.txt"), encoding="utf-8") as f:
            return f.read()

    def test_a_given_taken_again_with_the_same_arguments_is_played_once(self):
        bench = self.bench()
        written(bench, "same")

        written(bench, "same")

        self.assertEqual(self.plays(bench), "same\n", "one play for the two")

    def test_a_given_taken_again_puts_back_the_files_as_it_left_them(self):
        bench = self.bench()
        written(bench, "left")
        with open(os.path.join(bench.root, "note.txt"), "w", encoding="utf-8") as f:
            f.write("changed by the case")
        with open(os.path.join(bench.root, "more.txt"), "w", encoding="utf-8") as f:
            f.write("added by the case")

        written(bench, "left")

        self.assertEqual(self.note(bench), "left", "the file as the Given left it")
        self.assertEqual(os.listdir(bench.root), ["note.txt"], "nothing the case added")

    def test_a_given_taken_again_gives_a_copy_of_what_it_gave(self):
        bench = self.bench()
        first = written(bench, "given")
        first["text"] = "changed by the case"

        again = written(bench, "given")

        self.assertEqual(again, {"text": "given"}, "what the Given gave, not the case's change")

    def test_a_given_taken_with_other_arguments_is_played_again(self):
        bench = self.bench()
        written(bench, "first")

        written(bench, "second")

        self.assertEqual(self.plays(bench), "first\nsecond\n", "a play for each")
        self.assertEqual(self.note(bench), "second", "the files of the second")

    def test_a_given_of_a_bench_that_keeps_none_is_played_each_time(self):
        bench = self.bench(keeps=False)
        written(bench, "each")

        written(bench, "each")

        self.assertEqual(self.plays(bench), "each\neach\n", "a play for each")


if __name__ == "__main__":
    unittest.main()
