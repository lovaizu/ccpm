"""Tries rn whole as its user goes through it, the acceptance test of its user stories: from
`/rn:up <rough words>` to the pull request marked ready, on a request of about an hour with
documents and code, through the sign-offs, the design's where the purpose needs a document, a
feedback sent back and gone on from in a fresh conversation, and the learnings put one by one. The
real rn and the real turn run, their skills, agents, scripts and hooks as installing makes them, in
a fresh clone of lovaizu/playground, where rn opens its real pull request with the real gh; and the
user is stood in for by a Claude Code conversation of its own that holds what the user truly wants,
written beforehand in wants.json and never shown to rn, and answers each of rn's messages as that
user would, since rn's points come in an order and a number no fixed script can answer.

What it shows: whether rn takes the user from asking to the pull request ready, keeping every move
on its branch and nothing on the default branch, with the changes the user sends back at the
deliverable sign-off (KR1.1) and what the user had to do, beside the minutes it took (KR1.2), the
work being turn's own, made through its rounds and its first user.
What it leaves out: the user's own judgment of the work and of the minutes, as the stand-in is an
AI holding wants written beforehand; the maintainer gives it on reading the run's records and the
clone, which the test keeps.

    python3 dev/rn/trials/acceptance/acceptance.py [--dry | --until plan|design|deliverable]

It runs only where lovaizu/playground holds no open pull request and no branch but `main`, as the
trials there run one at a time; otherwise it stops before anything is made, naming what it found.
Each run makes a folder of its own, `rn/<yyyymmdd>-acceptance-<random>/` in the system's temporary
folder, outside any ccpm clone, so the conversations load none of its instructions, and prints its
path. In it: `repo`, the clone, its origin lovaizu/playground; `rn` and `turn`, the copies of this
working tree's; `bin/gh`, first on the PATH rn runs with, which runs the real gh with the issue rn
sends to lovaizu/ccpm sent to lovaizu/playground, and `gh.jsonl`, each command it ran; `user`, the
empty folder the stand-in user runs in; `rn-<n>.jsonl` and `user-<n>.jsonl`, what Claude Code
printed for message n to rn and for the stand-in's answer to it; `transcript.json`, rewritten after
each message; and `summary.json`.

The test ends when the session is finished with its pull request ready, when the stand-in says
stop or cannot end its reply as asked, after 120 messages to rn, when a run of Claude Code or a
reading of GitHub fails, with --until once that sign-off is shown, or on Ctrl-C. It then prints
and writes the summary: how it ended; each answer at each sign-off; KR1.1, the changes sent back at
the deliverable sign-off; KR1.2, what the stand-in did and its minutes; the issues opened; whether
each message's move kept the rules every move keeps; whether each move of the story was reached;
the minutes, the costs and the tokens of rn and of the stand-in user apart; the records to judge
the run by; and the verdict, PASSED or FAILED, or, with --until, REACHED where the sign-off was
shown with every rule kept. However it ends, it then removes what it made on the playground,
printing each: each open pull request closed, each branch but `main` deleted, and each issue it
opened closed, as an account that can write cannot delete one. The folder, the clone with it,
stays for the maintainer, and the run's minutes, tokens, cost and changes sent back are added to
`results.json` beside this script, to be compared with the runs before.

With --dry, the folder is made and the playground cloned, the first message and the stand-in's
first prompt printed, the rules checked on the starting state, and nothing is sent.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
TRIALS = os.path.dirname(HERE)
# The place is the move trials'; starting Claude Code is what every plugin's trials share, kept in
# lane's.
sys.path.insert(0, os.path.join(TRIALS, "moves"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(TRIALS)), "lane", "trials"))

import trying

# rn's names of the steering, steering.py, the module place loads from rn's scripts.
from place import DEFAULT, RULES, Place, Seen, Stop, costed, kept_learnings, steered, steering

USAGE = (
    "usage: python3 dev/rn/trials/acceptance/acceptance.py"
    " [--dry | --until plan|design|deliverable]"
)
PLAYGROUND = "lovaizu/playground"
# The user's words, in the conversation language their instructions set: a request of about an
# hour, with documents and code, so every stage is passed.
REQUEST = "/rn:up Downloads フォルダを整理するコマンドラインツールが欲しい"
# The minutes a message to rn waits for turn's runs, started in the background, each taking its
# rounds and its first user.
WAIT = 90
# The messages sent to rn at most, past which a run is taken to go round rather than on.
LIMIT = 120
KINDS = ("answer", "approve", "feedback", "stop")
AGAIN = (
    "Your last reply does not end as asked: {}. Reply again, ending with the one line of JSON in"
    " exactly the form given, with nothing after it."
)
UNTIL = "the {} sign-off shown, as --until asked"
# Each run's time, tokens, cost and changes sent back, kept in the repository so runs can be
# compared as they gather, judged by the maintainer against the size of the work.
RESULTS = os.path.join(HERE, "results.json")


def gh(real: str, *args: str) -> str:
    """What the real gh printed for the arguments; stops with what it printed where it fails."""
    done = subprocess.run([real, *args], capture_output=True, text=True, check=False)
    if done.returncode:
        raise Stop(f"gh {' '.join(args[:3])} ... failed: {(done.stdout + done.stderr).strip()}")
    return done.stdout.strip()


def tokens(sessions: list[str]) -> dict[str, int]:
    """The tokens the conversations of the sessions and every agent they started spent, by kind, as
    Claude Code's records give each reply's usage, a reply written over several entries counted
    once."""
    spent: dict[str, int] = {}
    for session in sessions:
        for path in glob.glob(trying.record.conversation(session)) + trying.agents(session):
            seen = set()
            with open(path, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    message = entry.get("message") or {}
                    if entry.get("type") != "assistant" or message.get("id") in seen:
                        continue
                    seen.add(message.get("id"))
                    for kind, count in (message.get("usage") or {}).items():
                        if isinstance(count, int):
                            spent[kind] = spent.get(kind, 0) + count
    return spent


def kept(summary: dict[str, Any], place: str) -> None:
    """Adds the run's time, tokens, cost and changes sent back to RESULTS, with the commit tried."""
    commit = subprocess.run(
        ["git", "-C", HERE, "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    runs = []
    if os.path.isfile(RESULTS):
        with open(RESULTS, encoding="utf-8") as f:
            runs = json.load(f)
    runs.append(
        {
            "commit": commit,
            "folder": place,
            "verdict": summary["verdict"],
            "ended": summary["ended"],
            "minutes": summary["KR1.2"]["minutes"],
            "tokens": summary["tokens"],
            "cost": summary["cost"],
            "changes sent": summary["KR1.2"]["changes sent"],
            "changes at the deliverable sign-off": summary["KR1.1"][
                "changes at the deliverable sign-off"
            ],
        }
    )
    with open(RESULTS, "w", encoding="utf-8") as f:
        json.dump(runs, f, ensure_ascii=False, indent=1)
        f.write("\n")


def left(real: str) -> tuple[list[str], list[str]]:
    """The URL of each open pull request on the playground, and each branch there but `main`."""
    prs = gh(real, "pr", "list", "--repo", PLAYGROUND, "--state", "open", "--json", "url")
    names = gh(real, "api", f"repos/{PLAYGROUND}/branches", "--paginate", "--jq", ".[].name")
    return [p["url"] for p in json.loads(prs)], [b for b in names.split() if b != DEFAULT]


class Playground(Place):
    """The run's folder as a move trial's case folder is laid out, with the real turn, the real gh
    behind the one first on the PATH, and the repository a clone of the playground."""

    def __init__(self, folder: str, real: str) -> None:
        super().__init__(folder)
        self.real = real

    def clone(self) -> None:
        """Makes the copies, the gh first on the PATH, and the clone, in the folder made
        already."""
        self.copy()
        self.put_gh(os.path.join(HERE, "gh.py"), self.real)
        url = f"https://github.com/{PLAYGROUND}.git"
        self.run("git", "clone", "-q", url, self.repo, cwd=self.folder)
        self.name()
        self.default = self.git("rev-parse", DEFAULT)

    def opened(self) -> list[str]:
        """The URL of each issue the run opened, as gh.jsonl keeps the commands rn ran."""
        try:
            with open(os.path.join(self.folder, "gh.jsonl"), encoding="utf-8") as f:
                ran = [json.loads(line) for line in f]
        except FileNotFoundError:
            return []
        made = [r for r in ran if r["ran"][:2] == ["issue", "create"] and r["code"] == 0]
        return [r["printed"].split()[-1] for r in made if r["printed"].split()]

    def github(self) -> dict[str, Any]:
        """What GitHub holds of the session, read with the real gh: the pull requests of the
        checked-out branch, none on `main`, and each issue the run opened."""
        branch = self.git("branch", "--show-current")
        fields = "number,url,headRefName,baseRefName,title,body,isDraft,state"
        listed = ("pr", "list", "--repo", PLAYGROUND, "--head", branch, "--state", "all")
        prs = json.loads(gh(self.real, *listed, "--json", fields))
        viewed = ("issue", "view", "--json", "url,title,body,state")
        return {
            "prs": prs,
            "issues": [json.loads(gh(self.real, *viewed, u)) for u in self.opened()],
        }

    def removed(self) -> list[str]:
        """Removes what the run made on the playground, all there is beside `main` as the trials
        there run one at a time: each open pull request closed, each branch but `main` deleted, and
        each issue the run opened closed; gives a line for each, what was removed or what failed."""
        done: list[str] = []
        try:
            prs, branches = left(self.real)
        except Stop as failed:
            prs, branches = [], []
            done.append(f"not read: {failed}; remove the pull requests and branches by hand")
        ref = f"repos/{PLAYGROUND}/git/refs/heads/"
        steps = [(f"pull request {u}", "closed", ("pr", "close", u)) for u in prs]
        steps += [(f"branch {b}", "deleted", ("api", "-X", "DELETE", ref + b)) for b in branches]
        steps += [(f"issue {u}", "closed", ("issue", "close", u)) for u in self.opened()]
        for what, how, args in steps:
            try:
                gh(self.real, *args)
                done.append(f"removed: {what}, {how}")
            except Stop as failed:
                done.append(f"not removed: {what}: {failed}; do it by hand")
        return done


def judged(reply: str) -> tuple[dict[str, Any] | None, str]:
    """The stand-in's answer, the JSON its reply ends with, and "" where it is in its form; None
    and what is wrong where it is not."""
    lines = [line for line in reply.strip().splitlines() if line.strip()]
    try:
        answer = json.loads(lines[-1]) if lines else None
    except ValueError:
        answer = None
    if not isinstance(answer, dict):
        return None, "its last line is not a JSON object"
    says, kind, changes, read = (answer.get(k) for k in ("says", "kind", "changes", "read"))
    if not isinstance(says, str) or not isinstance(answer.get("fresh"), bool):
        return None, '"says" must be text and "fresh" true or false'
    if kind not in KINDS:
        return None, f'"kind" must be one of {", ".join(KINDS)}'
    lists = (changes, read)
    if not all(isinstance(v, list) and all(isinstance(x, str) for x in v) for v in lists):
        return None, '"changes" and "read" must each be a list of texts'
    if kind != "stop" and not says.strip():
        return None, '"says" is empty'
    if kind == "approve" and says.strip() != "/rn:ty":
        return None, 'an "approve" says `/rn:ty` alone'
    if kind == "feedback" and not (says.startswith("/rn:gm ") and changes):
        return None, 'a "feedback" says `/rn:gm <feedback>` and names each change in "changes"'
    return answer, ""


def stood(seen: Seen) -> dict[str, Any]:
    """Where the session stands after a move: the steering's stage and sign-off waiting, the
    session's learnings counted, and its pull request on GitHub, none before rn opens it."""
    steered_now = steered(seen)
    keys = steered_now.keys if steered_now else {}
    return {
        "stage": keys.get("stage"),
        "signoff": keys.get("signoff"),
        "learnings": len(kept_learnings(seen)) if steered_now else 0,
        "pr": (seen.gh["prs"] or [None])[0],
    }


def rules(seen: Seen) -> dict[str, bool]:
    """Whether the move kept what every move keeps, as the move trials check after each."""
    return {rule: holds(seen) for rule, holds in RULES.items()}


class Trial:
    """A run of the test in its folder, and what it has seen so far; until is the sign-off it ends
    at once shown, "" to go to the end."""

    def __init__(self, place: str, real: str, until: str) -> None:
        self.place = place
        self.p = Playground(place, real)
        self.until = until
        self.user = os.path.join(place, "user")
        self.words = REQUEST.partition(" ")[2]
        self.transcript: dict[str, list] = {"rn": [], "user": []}
        self.answers: list[dict[str, Any]] = []
        self.costs: dict[str, dict[str, float]] = {"rn": {}, "user": {}}
        # The stand-in's conversation, one for the whole run, as the user is the same person;
        # rn's, made again for each fresh conversation the stand-in asks for.
        self.standin = trying.Conversation([], cwd=self.user)
        self.rn = self.fresh()
        self.last: dict[str, Any] = {}
        self.start = time.time()

    def make(self) -> None:
        """Makes the place, the clone with the copies, and the stand-in's empty folder."""
        self.p.clone()
        os.makedirs(self.user)

    def prompt(self, words: list[str], now: dict[str, Any]) -> str:
        """What the stand-in is told of rn's message: rn's words, where the session stands and the
        pull request."""
        pr = now["pr"]["url"] if now["pr"] else "not opened yet"
        return (
            "rn said:\n\n" + "\n\n".join(words) + "\n\n"
            f"stage: {now['stage'] or 'no session yet'},"
            f" sign-off waiting: {now['signoff'] or 'none'}"
            f"\npull request: {pr}\nEnd your reply with the one line of JSON."
        )

    def first(self, words: list[str], now: dict[str, Any]) -> str:
        """The stand-in's first prompt: user.md with the request, then rn's first message."""
        with open(os.path.join(HERE, "user.md"), encoding="utf-8") as f:
            asked = f.read()
        with open(os.path.join(HERE, "wants.json"), encoding="utf-8") as f:
            wants = json.load(f)
        filled = asked.format(
            words=self.words,
            wants="\n".join(f"- {w}" for w in wants),
            repo=self.p.repo,
            pr=now["pr"]["url"] if now["pr"] else "not opened yet",
        )
        return filled + "\n" + self.prompt(words, now)

    def write(self) -> None:
        """Rewrites transcript.json with every message so far."""
        with open(os.path.join(self.place, "transcript.json"), "w", encoding="utf-8") as f:
            json.dump(self.transcript, f, ensure_ascii=False, indent=1)

    def asked(self, n: int, prompt: str) -> dict[str, Any] | None:
        """The stand-in's answer to rn's message n, asked again once where its reply does not end
        with its JSON line; None where it fails twice."""
        sessions = self.costs["user"]
        for attempt in (1, 2):
            started = time.time()
            name = f"user-{n}.jsonl" if attempt == 1 else f"user-{n}-again.jsonl"
            record = os.path.join(self.place, name)
            end = self.standin.send(prompt, record)
            session = end["session_id"]
            sessions[session] = end.get("total_cost_usd") or 0
            answer, wrong = judged(end.get("result") or "")
            self.transcript["user"].append(
                {
                    "n": n,
                    "attempt": attempt,
                    "session": session,
                    "prompt": prompt,
                    "reply": end.get("result") or "",
                    "answer": answer,
                    "wrong": wrong,
                    "minutes": round((time.time() - started) / 60, 1),
                    "cost": sessions[session],
                }
            )
            self.write()
            if answer:
                return answer
            prompt = AGAIN.format(wrong)
        return None

    def loop(self) -> str:
        """Sends rn each message, the first the request, each after it what the stand-in says,
        until the test ends; gives how it ended. Stops where reading GitHub fails."""
        message, fresh, answer = REQUEST, True, None
        before = stood(self.p.seen(self.p.head(), ""))
        for n in range(1, LIMIT + 1):
            started, head = time.time(), self.p.head()
            record = os.path.join(self.place, f"rn-{n}.jsonl")
            entry = {"n": n, "fresh": fresh, "says": message, "user": answer}
            entry.update(stage_before=before["stage"], signoff_before=before["signoff"])
            self.transcript["rn"].append(entry)
            if fresh:
                self.rn.close()
                self.rn = self.fresh()
            try:
                end = self.rn.send(message, record)
            except (SystemExit, OSError, ValueError) as failed:
                entry["failed"] = str(failed)
                self.write()
                return f"rn's run of message {n} failed: {failed}"
            session = end["session_id"]
            self.costs["rn"][session] = end.get("total_cost_usd") or 0
            seen = self.p.seen(head, end.get("result") or "", record)
            now = self.last = stood(seen)
            entry.update(session=session, stage_after=now["stage"], signoff_after=now["signoff"])
            words = seen.said or [seen.reply]
            entry.update(said=words, rules=rules(seen))
            entry.update(minutes=round((time.time() - started) / 60, 1))
            entry["cost"] = self.costs["rn"][session]
            self.write()
            if now["stage"] == "finished" and now["pr"] and not now["pr"]["isDraft"]:
                return "done: the session finished, its pull request ready"
            if self.until and now["signoff"] == self.until:
                return UNTIL.format(self.until)
            prompt = self.first(words, now) if n == 1 else self.prompt(words, now)
            try:
                answer = self.asked(n, prompt)
            except (SystemExit, OSError, ValueError) as failed:
                return f"the stand-in's run on message {n} failed: {failed}"
            if answer is None:
                return f"the stand-in did not end its reply with its JSON line, twice, at {n}"
            self.answers.append(
                {"n": n, "stage": now["stage"], "signoff": now["signoff"], **answer}
            )
            if answer["kind"] == "stop":
                return f"the stand-in stopped at message {n}: {answer['says']}"
            message, fresh, before = answer["says"], answer["fresh"], now
        return f"{LIMIT} messages sent to rn"

    def fresh(self) -> trying.Conversation:
        """A fresh conversation with rn, as the user starts one in the repository."""
        return trying.Conversation(self.p.plugins, self.p.repo, WAIT, self.p.env)

    def close(self) -> None:
        """Ends rn's conversation and the stand-in's."""
        self.rn.close()
        self.standin.close()

    def reached(self) -> dict[str, bool]:
        """Whether the run reached each move of the story."""
        sent = self.transcript["rn"]
        shown = {
            s: [e["n"] for e in sent if e.get("signoff_after") == s] for s in steering.SIGNOFFS
        }
        fed = [a["n"] for a in self.answers if a["kind"] == "feedback" and a["signoff"] == "plan"]
        fresh = [e["n"] for e in sent if e["fresh"] and fed and e["n"] > fed[0] + 1]
        put = [a for a in self.answers if a["kind"] == "answer" and a["stage"] == "learnings"]
        pr = self.last.get("pr")
        # rn moves from design to build without the design sign-off only where the design stage
        # made no document, so a stage after design reached without it is the design stage gone
        # through; one message can carry the session past build, as it does where the build's
        # last action leads straight to the deliverable sign-off.
        later = steering.STAGES[steering.STAGES.index(steering.DESIGN) + 1 :]
        designed = bool(shown["design"]) or any(e.get("stage_after") in later for e in sent)
        return {
            "the plan sign-off shown": bool(shown["plan"]),
            (
                "the design sign-off shown, or build reached without it as no document was made"
            ): designed,
            "the deliverable sign-off shown": bool(shown["deliverable"]),
            "a feedback at the plan sign-off kept, gone on from in a fresh conversation, and the"
            " plan sign-off shown again": bool(fresh) and any(k >= fresh[0] for k in shown["plan"]),
            # Counted by the answers given at the learnings stage, as no record names which
            # learning a message put.
            "each learning put to the user": 0 < self.last.get("learnings", 0) <= len(put),
            "the pull request marked ready": bool(pr) and not pr["isDraft"],
        }

    def summary(self, ended: str) -> dict[str, Any]:
        """What the run came to, for the maintainer to judge it by."""
        given = [a for a in self.answers if a["kind"] in ("approve", "feedback")]
        signoffs = {
            s: [
                {"n": a["n"], "kind": a["kind"], "changes": a["changes"]}
                for a in given
                if a["signoff"] == s
            ]
            for s in steering.SIGNOFFS
        }
        late = [c for a in signoffs["deliverable"] for c in a["changes"]]
        sent = self.transcript["rn"]
        broken = [
            {"n": e["n"], "broke": [r for r, held in e["rules"].items() if not held]}
            for e in sent
            if "rules" in e and not all(e["rules"].values())
        ]
        reached = self.reached()
        if ended.startswith("done") and not broken and all(reached.values()):
            verdict = "PASSED"
        elif self.until and ended == UNTIL.format(self.until) and not broken:
            verdict = f"REACHED {self.until}"
        else:
            verdict = "FAILED"
        sessions = [*self.costs["rn"], *self.costs["user"]]
        records = sorted(glob.glob(os.path.join(self.place, "*.jsonl")))
        for s in sessions:
            records += glob.glob(trying.record.conversation(s))
            records += sorted(trying.agents(s))
        return {
            "verdict": verdict,
            "ended": ended,
            "signoffs": signoffs,
            "KR1.1": {"changes at the deliverable sign-off": len(late), "changes": late},
            # What the user spends from asking to the purpose achieved, counted by what the
            # stand-in did, as an AI's minutes are not a person's, beside the minutes themselves.
            "KR1.2": {
                "points answered": len([a for a in self.answers if a["kind"] == "answer"]),
                "proposals read": len(given),
                "changes sent": {
                    s: sum(len(a["changes"]) for a in signoffs[s]) for s in steering.SIGNOFFS
                },
                "fresh conversations": len([a for a in self.answers if a["fresh"]]),
                "minutes": {
                    "whole": round((time.time() - self.start) / 60, 1),
                    "rn": round(sum(e.get("minutes", 0) for e in sent), 1),
                    "stand-in": round(sum(e["minutes"] for e in self.transcript["user"]), 1),
                },
            },
            "issues": self.p.github()["issues"],
            "rules broken": broken,
            "reached": reached,
            "cost": {"rn": costed(self.costs["rn"]), "stand-in": costed(self.costs["user"])},
            "tokens": {
                "rn": tokens([*self.costs["rn"]]),
                "stand-in": tokens([*self.costs["user"]]),
            },
            "records": records,
        }


def dry(trial: Trial) -> int:
    """Prints the first message, the stand-in's first prompt and the rules on the starting state,
    sending nothing; gives 0 where every rule holds."""
    seen = trial.p.seen(trial.p.head(), "")
    print("first message to rn:", REQUEST, sep="\n")
    print("\nthe stand-in's first prompt:\n" + trial.first(["<rn's first reply>"], stood(seen)))
    held = rules(seen)
    print("\nthe rules on the starting state:")
    print("\n".join(f"  {'ok' if h else 'FAIL'} {r}" for r, h in held.items()))
    print(f"\nnothing was sent; {trial.place} kept")
    return 0 if all(held.values()) else 1


def run(trial: Trial) -> int:
    """Runs the test to its end, prints and writes the summary, then removes what the run made on
    the playground, however it ended; gives 0 where the verdict is PASSED or REACHED."""
    ended, verdict = "stopped by Ctrl-C", "FAILED"
    try:
        ended = trial.loop()
    except KeyboardInterrupt:
        pass
    except Stop as failed:
        ended = f"reading GitHub failed: {failed}"
    except Exception as failed:
        ended = f"the test failed: {failed!r}"
        raise
    finally:
        try:
            trial.close()
            summary = trial.summary(ended)
            verdict = summary["verdict"]
            with open(os.path.join(trial.place, "summary.json"), "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=1)
            print(json.dumps(summary, ensure_ascii=False, indent=1))
            kept(summary, trial.place)
        finally:
            print("\n".join(trial.p.removed()))
            print(f"kept: {trial.place}, holding the clone {trial.p.repo} with the work")
            print(f"summary: {os.path.join(trial.place, 'summary.json')}")
            print(f"transcript: {os.path.join(trial.place, 'transcript.json')}")
            print(verdict)
    return 0 if verdict != "FAILED" else 1


def main(argv: list[str]) -> int:
    """Runs the test in a folder of its own where the playground holds no other run's work; prints
    the usage and gives 1 on any other arguments, and what stops it where gh is missing, fails or
    finds another run's work."""
    if argv in (["-h"], ["--help"]):
        print(f"{__doc__}\n{USAGE}")
        return 0
    until = argv[1] if argv[:1] == ["--until"] and len(argv) == 2 else ""
    if argv not in ([], ["--dry"]) and until not in steering.SIGNOFFS:
        print(USAGE)
        return 1
    real = shutil.which("gh")
    if not real:
        print(
            "acceptance: gh is not on the PATH; install it, logged in to an account that can push"
            f" to {PLAYGROUND}, and run this again"
        )
        return 1
    try:
        prs, branches = left(real)
    except Stop as failed:
        print(f"acceptance: {PLAYGROUND} could not be read: {failed}; fix it as gh says")
        return 1
    if prs or branches:
        print(
            f"acceptance: {PLAYGROUND} holds another run's work, and its trials run one at a"
            " time; once that run is over, remove what it left, or have it removed, and run this"
            " again:"
        )
        print(
            "\n".join(
                [*(f"  open pull request {u}" for u in prs), *(f"  branch {b}" for b in branches)]
            )
        )
        return 1
    place = trying.folder("rn", "acceptance")
    trial = Trial(place, real, until)
    try:
        trial.make()
    except Stop as failed:
        print(f"acceptance: the folder could not be made: {failed}")
        return 1
    return dry(trial) if argv == ["--dry"] else run(trial)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
