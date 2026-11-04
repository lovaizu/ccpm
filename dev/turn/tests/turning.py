"""What Turn's trials stand on: the repository of `tidy`, a tool that sorts a Downloads folder;
copies of Turn and pin for each run; an interactive session of Claude Code, as Turn's roles run in
the background and `claude -p` does not start `up` again once a role it started has ended; the
person, stood in for by an AI that answers from an intent written beforehand and never shown Turn,
and says of each message what it put to them; and the run judged from its records and its work,
the work by the stand-in as the person would judge it."""

from __future__ import annotations

import datetime
import json
import os
import shutil
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "dev", "lane", "trials"))

import trying

PLUGINS = {name: os.path.join(ROOT, "plugins", name) for name in ("turn", "pin")}
# The most messages put to the person before a run is stopped as one that does not end.
TURNS = 40
# `tidy`: tidy.py moves each file of a folder into a folder named after its kind, by its extension,
# and shows what it would move with --dry-run; a file of no extension, or one whose name its folder
# holds already, stays where it is, so tidy never deletes a file.
TIDY_PY = """\"\"\"tidy: `python3 tidy.py [--dry-run] <folder>` moves each file of the folder into a
folder named after its kind.\"\"\"

import argparse
import os
import shutil
import sys

KINDS = {".jpg": "images", ".png": "images", ".pdf": "documents", ".zip": "archives"}


def main(argv):
    parser = argparse.ArgumentParser(prog="tidy")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("folder")
    args = parser.parse_args(argv)
    for name in sorted(os.listdir(args.folder)):
        path = os.path.join(args.folder, name)
        extension = os.path.splitext(name)[1].lower()
        if not extension or os.path.isdir(path):
            continue
        kind = KINDS.get(extension, "other")
        if os.path.exists(os.path.join(args.folder, kind, name)):
            print(f"{name} stays: {kind}/{name} is there already")
            continue
        print(f"{name} -> {kind}/")
        if not args.dry_run:
            os.makedirs(os.path.join(args.folder, kind), exist_ok=True)
            shutil.move(path, os.path.join(args.folder, kind, name))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
"""
# The MIT License whole, so the repository's terms are settled as a tool's are.
MIT = """MIT License

Copyright (c) 2026 the tidy authors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
TIDY = {
    "tidy.py": TIDY_PY,
    "LICENSE": MIT,
}
FINDS = trying.finds(
    """You stand in for the person an AI is making a work for. Here is who you are and what you
truly want; the AI cannot see it:""",
    """- "answer": your answer to the message, as you would write it, or "" where it asks you
  nothing;
- "asks": true where the message asks you anything or waits for your answer; otherwise false;
"""
    + trying.POINTS
    + """
- "asks_fact": true where it asks you something about the repository that the AI could read for
  itself, rather than showing you what it found for you to confirm; otherwise false;
- "asks_settled": true where it asks you again something you are said, above, to have settled
  already, or something you already answered in this conversation; otherwise false;
- "not_yours": true where it asks you to decide something your wants above show you do not care
  about and that follows from what you want and the repository; otherwise false, as where it
  asks what only you can know, such as what lies outside the repository;
- "finished": true where the message says the work is done and asks you nothing; otherwise
  false.""",
)
JUDGES = """You stand in for the person an AI made a work for. Here is who you are and what you
truly want:

{intent}

The work, each file as it is:

{work}

Judge the work as that person, about to put it to use. Give only one JSON object, with no other
text: {{"changes": [each change you would make or ask for before you put it to use, in a short
sentence each; none where you would use it as it is]}}."""


asked = trying.stand_in


def made(place: str, files: dict[str, str] | None = None) -> tuple[str, dict[str, str]]:
    """The repository of the run, `tidy` in its folder, with the files given beside tidy's and all
    committed, and a copy of Turn and of pin beside it; gives the repository and the copies'
    folders by name."""
    repo = os.path.join(place, "tidy")
    trying.committed(repo, {**TIDY, **(files or {})})
    copies = {}
    for name, source in PLUGINS.items():
        copies[name] = os.path.join(place, "plugins", name)
        # Lane's code lies in Turn through a link into the marketplace; the copy takes it whole.
        shutil.copytree(source, copies[name], symlinks=False)
    return repo, copies


def talked(
    first: str, plugins: list[str], repo: str, place: str, intent: str, minutes: int = 180
) -> tuple[str, list[dict[str, Any]]]:
    """An interactive session of Claude Code on the plugins, in the repository, as trying.py's
    interactive runs it, from the first message until Turn says the work is done; and each message
    the main conversation put to the person, with what the person said of it. The person answers
    from the intent, in a folder of its own in the run's folder, and so too where Claude Code asks
    them to allow a call; a stop that asks the person nothing, as where Turn is still at work, is
    waited past."""
    alone = os.path.join(place, "person")
    os.makedirs(alone, exist_ok=True)
    said: list[str] = []
    turns: list[dict[str, Any]] = []

    def answer(message: str) -> str | None:
        if len(turns) == TURNS:
            raise SystemExit(f"the conversation did not end in {TURNS} messages")
        heard = trying.heard(FINDS, intent, said, message, alone)
        turns.append({"message": message, **heard})
        print(f"  AI: {message[:300]!r}")
        print(f"  person: {str(heard.get('answer'))[:200]!r} {heard_of(heard)}", flush=True)
        if heard.get("finished"):
            return None
        if not heard.get("asks"):
            return ""
        said.extend([f"AI: {message}", f"You: {heard['answer']}"])
        return str(heard["answer"]) or "yes"

    def permit(screen: str) -> str:
        return trying.permitted(intent, screen, alone)

    done = trying.interactive(first, plugins, repo, place, minutes, answer, permit)
    return done["session_id"], turns


def heard_of(heard: dict[str, Any]) -> str:
    """What the person said of a message, in a few words."""
    keys = ("asks", "points", "asks_fact", "asks_settled", "not_yours", "finished")
    return " ".join(f"{k}={heard.get(k)}" for k in keys)


def asked_wrong(turns: list[dict[str, Any]]) -> list[str]:
    """What the person finds wrong in the messages put to them: more than one point, a fact asked,
    a settled point asked again, or a point not theirs."""
    wrong = []
    for n, t in enumerate(turns, 1):
        if int(t.get("points") or 0) > 1:
            wrong.append(f"message {n} put {t['points']} points to the person")
        for key, what in (
            ("asks_fact", "asked the person a fact of the repository"),
            ("asks_settled", "asked again what was settled"),
            ("not_yours", "asked the person a point not theirs"),
        ):
            if t.get(key):
                wrong.append(f"message {n} {what}")
    return wrong


def work_wrong(repo: str, paths: list[str], place: str, intent: str) -> list[str]:
    """Each change the person would make to the work before using it, as the stand-in judges the
    work's files."""
    shown = []
    for path in paths:
        try:
            with open(os.path.join(repo, path), encoding="utf-8") as f:
                shown.append(f"<file path={path!r}>\n{f.read()}</file>")
        except OSError:
            shown.append(f"<file path={path!r}>(not there)</file>")
    judged = asked(
        JUDGES.format(intent=intent, work="\n\n".join(shown)), os.path.join(place, "person")
    )
    return [f"the person would change: {c}" for c in judged.get("changes", [])]


def run_folder(repo: str) -> str:
    """The one run's folder Turn made under `.turn/` in the repository, or ""."""
    found = (
        sorted(
            os.path.join(repo, ".turn", n)
            for n in os.listdir(os.path.join(repo, ".turn"))
            if n != "best-practices" and os.path.isdir(os.path.join(repo, ".turn", n))
        )
        if os.path.isdir(os.path.join(repo, ".turn"))
        else []
    )
    return found[-1] if found else ""


def read_json(path: str) -> Any:
    """The JSON at the path, or None where it is not there."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# How the stand-in for the person answers, the same in every trial.
HOW = """How you answer: briefly, as a busy person, in the language the AI writes to you in.
Answer what you are asked from what you want above. Where a fact is shown to you, say whether it
is right. Where you are asked something your wants above do not settle, say the AI may decide it.
Where you are shown the whole design and asked to approve it, say yes where it holds what you
want above, and otherwise say what is to change."""
# Each role's start that may follow the start of another, as Turn's routes give them.
FOLLOWS = {
    "planner": {"designer"},
    "designer": {"builder"},
    "builder": {"evaluator", "designer"},
    "evaluator": {"designer", "refactorer"},
    "refactorer": {"proofreader"},
    "proofreader": {"refactorer", "designer"},
}


def starts(session: str) -> list[tuple[str, str, float, float]]:
    """Each run of a role of Turn the session started, by its agent type, its record, and the
    times of its first and last entries, in the order they started."""
    found = []
    for file in trying.agents(session):
        kind = trying.record.agent_type(file)
        if not kind.startswith("turn:") or kind == "turn:up":
            continue
        times = [
            datetime.datetime.fromisoformat(str(e["timestamp"]).replace("Z", "+00:00")).timestamp()
            for e in trying.record.read(file) or []
            if e.get("timestamp")
        ]
        if times:
            found.append((kind.split(":", 1)[1], file, min(times), max(times)))
    return sorted(found, key=lambda s: s[2])


def routes_wrong(runs: list[tuple[str, str, float, float]]) -> list[str]:
    """Each start of a role that no route leads to from the role started before it, a step's runs
    started at once counted as one; and a run that did not start with planner."""
    roles = [r for r, *_ in runs]
    steps = [r for n, r in enumerate(roles) if n == 0 or roles[n - 1] != r]
    wrong = [] if steps[:1] == ["planner"] else ["the run did not start with planner"]
    for before, after in zip(steps, steps[1:]):
        if after not in FOLLOWS.get(before, set()):
            wrong.append(f"{after} was started after {before}, which no route leads to")
    if steps[-1:] != ["proofreader"]:
        wrong.append(f"the run ended at {steps[-1:] or 'no role'}, not at proofreader")
    return wrong


def overlapped(runs: list[tuple[str, str, float, float]], role: str) -> bool:
    """Whether two runs of the role went at the same time."""
    spans = sorted((a, b) for r, _, a, b in runs if r == role)
    return any(spans[n + 1][0] < spans[n][1] for n in range(len(spans) - 1))


def judged(
    session: str, turns: list[dict[str, Any]], repo: str, place: str, intent: str, paths: list[str]
) -> list[str]:
    """What is wrong in a run that handed back the work at the paths: in the messages put to the
    person, in the order the roles started, and in the work as the person would judge it."""
    wrong = asked_wrong(turns) + routes_wrong(starts(session))
    return wrong + work_wrong(repo, paths, place, intent)


verdict = trying.verdict
main = trying.main
