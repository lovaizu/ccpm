"""Tries rn's flow whole as its user goes through it, an acceptance test of its user story: from
`/rn:up <rough words>` to the pull request marked ready, through the sign-offs, the design's where
the purpose needs a document, a feedback sent back and gone on from in a fresh conversation, and the
learnings put one by one. The real rn runs, its skills and scripts as installing makes them; gh is
stood in for, as in the move trials; turn by an agent that makes each work itself from the CCS rn
hands it, as no fixed work can keep the decisions the stand-in user takes in its own words; and the
user by a Claude Code conversation of its own that holds what the user truly wants, written
beforehand in wants.json and never shown to rn, and answers each of rn's messages as that user
would, since rn's points come in an order and a number no fixed script can answer.

What it shows: whether rn takes the user from asking to the pull request ready, keeping every move
on its branch and nothing on the default branch, with the changes the user sends back at the
deliverable sign-off (KR1.1) and what the user had to do, beside the minutes it took (KR1.2).
What it leaves out, on the user's decision: the quality of what turn makes, as the stand-in turn
makes each work once, without turn's rounds or first user, keeping only the decisions the CCS
holds.

    python3 dev/rn/trials/flow/flow.py [--dry]

Each run makes a folder of its own, `rn/<yyyymmdd>-flow-<random>/` in the system's temporary
folder, outside any ccpm clone, so the conversations load none of its instructions, and prints its
path. It is made as each move trial's case folder is (dev/rn/trials/moves/place.py): `repo`, the
small project with its bare origin `origin.git`; `rn` and `turn`, the copies, turn's turn:up the
stand-in, the agent of up.md with write.py, which makes each work from its CCS; `bin/gh` and
`gh.json`, the stand-in gh and the pull request and issues it keeps. Beside them, `user`, the empty
folder the stand-in user runs in; `rn-<n>.jsonl` and `user-<n>.jsonl`, what Claude Code printed for
message n to rn and for the stand-in's answer to it; `transcript.json`, rewritten after each
message; and `summary.json`. The trial removes nothing.

The trial ends when the session is finished with its pull request ready, when the stand-in says
stop or cannot end its reply as asked, after 120 messages to rn, when a run of Claude Code fails,
or on Ctrl-C. It then prints and writes the summary: how it ended; each answer at each sign-off;
KR1.1, the changes sent back at the deliverable sign-off; KR1.2, what the stand-in did and its
minutes; the issues
kept; whether each message's move kept the rules every move keeps; whether each move of the story
was reached; the minutes, the costs of rn and of the stand-in user apart; the records to judge the
run by; and the verdict, PASSED or FAILED.

With --dry, the folder is made, the first message and the stand-in's first prompt printed, the
rules checked on the starting state, and nothing is sent.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import time
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
TRIALS = os.path.dirname(HERE)
# The place, the stand-in gh and the greeting session's request are the move trials';
# starting Claude Code is what every plugin's trials share, kept in lane's.
sys.path.insert(0, os.path.join(TRIALS, "moves"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(TRIALS)), "lane", "trials"))

import cases
import trying
from place import RULES, Place, Seen, costed, kept_learnings, steered

USAGE = "usage: python3 dev/rn/trials/flow/flow.py [--dry]"
# The minutes a message to rn waits for the stand-in turn, started in the background.
WAIT = 30
# The messages sent to rn at most, past which a run is taken to go round rather than on.
LIMIT = 120
KINDS = ("answer", "approve", "feedback", "stop")
SIGNOFFS = cases.steering.SIGNOFFS
AGAIN = (
    "Your last reply does not end as asked: {}. Reply again, ending with the one line of JSON in"
    " exactly the form given, with nothing after it."
)


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
    session's learnings counted, and the pull request the stand-in gh keeps, none before rn opens
    it."""
    steering = steered(seen)
    keys = steering.keys if steering else {}
    return {
        "stage": keys.get("stage"),
        "signoff": keys.get("signoff"),
        "learnings": len(kept_learnings(seen)) if steering else 0,
        "pr": (seen.gh["prs"] or [None])[0],
    }


def rules(seen: Seen) -> dict[str, bool]:
    """Whether the move kept what every move keeps, as the move trials check after each."""
    return {rule: holds(seen) for rule, holds in RULES.items()}


class Trial:
    """A run of the trial in its folder, and what it has seen so far."""

    def __init__(self, place: str) -> None:
        self.place = place
        self.p = Place(place)
        self.user = os.path.join(place, "user")
        self.words = cases.REQUEST.partition(" ")[2]
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
        """Makes the place as a move trial's case folder, with no replies set, turn:up the agent
        that makes each work itself, and the stand-in's empty folder."""
        self.p.make({})
        turn = self.p.turn
        shutil.copyfile(os.path.join(HERE, "up.md"), os.path.join(turn, "agents", "up.md"))
        shutil.copyfile(os.path.join(HERE, "write.py"), os.path.join(turn, "scripts", "write.py"))
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
        until the trial ends; gives how it ended."""
        message, fresh, answer = cases.REQUEST, True, None
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
        shown = {s: [e["n"] for e in sent if e.get("signoff_after") == s] for s in SIGNOFFS}
        fed = [a["n"] for a in self.answers if a["kind"] == "feedback" and a["signoff"] == "plan"]
        fresh = [e["n"] for e in sent if e["fresh"] and fed and e["n"] > fed[0] + 1]
        put = [a for a in self.answers if a["kind"] == "answer" and a["stage"] == "learnings"]
        pr = self.last.get("pr")
        # rn moves from design to build without the design sign-off only where the design stage
        # made no document, so a stage after design reached without it is the design stage gone
        # through; one message can carry the session past build, as it does where the build's
        # last action leads straight to the deliverable sign-off.
        later = cases.steering.STAGES[cases.steering.STAGES.index(cases.steering.DESIGN) + 1 :]
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
            for s in SIGNOFFS
        }
        late = [c for a in signoffs["deliverable"] for c in a["changes"]]
        sent = self.transcript["rn"]
        broken = [
            {"n": e["n"], "broke": [r for r, held in e["rules"].items() if not held]}
            for e in sent
            if "rules" in e and not all(e["rules"].values())
        ]
        reached = self.reached()
        passed = ended.startswith("done") and not broken and all(reached.values())
        with open(os.path.join(self.place, "gh.json"), encoding="utf-8") as f:
            issues = json.load(f)["issues"]
        sessions = [*self.costs["rn"], *self.costs["user"]]
        records = sorted(glob.glob(os.path.join(self.place, "*.jsonl")))
        for s in sessions:
            records += glob.glob(trying.record.conversation(s))
            records += sorted(trying.agents(s))
        return {
            "verdict": "PASSED" if passed else "FAILED",
            "ended": ended,
            "signoffs": signoffs,
            "KR1.1": {"changes at the deliverable sign-off": len(late), "changes": late},
            # What the user spends from asking to the purpose achieved, counted by what the
            # stand-in did, as an AI's minutes are not a person's, beside the minutes themselves.
            "KR1.2": {
                "points answered": len([a for a in self.answers if a["kind"] == "answer"]),
                "proposals read": len(given),
                "changes sent": {s: sum(len(a["changes"]) for a in signoffs[s]) for s in SIGNOFFS},
                "fresh conversations": len([a for a in self.answers if a["fresh"]]),
                "minutes": {
                    "whole": round((time.time() - self.start) / 60, 1),
                    "rn": round(sum(e.get("minutes", 0) for e in sent), 1),
                    "stand-in": round(sum(e["minutes"] for e in self.transcript["user"]), 1),
                },
            },
            "issues": issues,
            "rules broken": broken,
            "reached": reached,
            "cost": {"rn": costed(self.costs["rn"]), "stand-in": costed(self.costs["user"])},
            "records": records,
        }


def main(argv: list[str]) -> int:
    """Runs the trial in a folder of its own; prints the usage and gives 1 on any other
    arguments."""
    if argv in (["-h"], ["--help"]):
        print(f"{__doc__}\n{USAGE}")
        return 0
    dry = argv == ["--dry"]
    if argv and not dry:
        print(USAGE)
        return 1
    place = trying.folder("rn", "flow")
    trial = Trial(place)
    trial.make()
    if dry:
        seen = trial.p.seen(trial.p.head(), "")
        print("first message to rn:", cases.REQUEST, sep="\n")
        print("\nthe stand-in's first prompt:\n" + trial.first(["<rn's first reply>"], stood(seen)))
        held = rules(seen)
        print("\nthe rules on the starting state:")
        print("\n".join(f"  {'ok' if h else 'FAIL'} {r}" for r, h in held.items()))
        print(f"\nnothing was sent; {place} kept")
        return 0 if all(held.values()) else 1
    ended = "stopped by Ctrl-C"
    try:
        ended = trial.loop()
    except KeyboardInterrupt:
        pass
    finally:
        trial.close()
        summary = trial.summary(ended)
        with open(os.path.join(place, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
        print(json.dumps(summary, ensure_ascii=False, indent=1))
        print(f"kept: {place}, holding the repository {trial.p.repo} with the work on its branch")
        print(f"summary: {os.path.join(place, 'summary.json')}")
        print(f"transcript: {os.path.join(place, 'transcript.json')}")
        print(summary["verdict"])
    return 0 if summary["verdict"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
