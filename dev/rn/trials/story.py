#!/usr/bin/env python3
"""The README's story end to end: `/rn:on move src/account to TypeScript` on the practice repository's
`main`, answered by the stand-in, until the pull request is ready, the session is finished, or the run
gives out. Records what the user spent: how long each turn kept them waiting, how many lines they
read, and each time they were called.

Run it with any rn, so a rebuilt rn is set beside the last one that runs to the end (rn 0.8.0)."""
import argparse
import json
import os
import subprocess
import sys
import time

from common import ACCOUNT_PART, REPO, clone

START = "/rn:on move src/account to TypeScript"
# Installed copies would answer in place of the plugins under test.
SETTINGS = json.dumps({"enabledPlugins": {"rn@ccpm": False, "writ@ccpm": False, "pith@ccpm": False}})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rn", required=True, help="the rn plugin directory under test")
    ap.add_argument("--writ", help="the writ plugin directory, when this rn uses it")
    ap.add_argument("--pith", help="the pith plugin directory, when this rn uses it")
    ap.add_argument("--out", required=True,
                    help="a new directory for the clone and record, or one a run stopped at the usage "
                         "limit left, to go on from there")
    ap.add_argument("--max-calls", type=int, default=40)
    ap.add_argument("--max-hours", type=float, default=6)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    work = os.path.join(out, "work")
    left = load(out)
    if left is None:
        if os.path.exists(out):
            sys.exit(f"{out} exists and holds no stopped run; give a new directory")
        os.makedirs(out)
        clone(work)
    dirs = []
    for d in (a.rn, a.writ, a.pith):
        if d:
            dirs += ["--plugin-dir", os.path.abspath(d)]
    story = Story(out, work, dirs, left)
    try:
        story.run(a.max_calls, a.max_hours * 3600)
    except Limit:
        story.log("trial", "Stopped at the usage limit; run again with the same --out to go on.")
        sys.exit(3)
    story.close_pull_request()
    print(os.path.join(out, "spent.json"))


class Limit(Exception):
    """Claude Code's usage limit: the run is kept, pull request and all, to go on later."""


def load(out):
    """What a run stopped at the usage limit left: its calls, conversation, and what rn said last."""
    try:
        with open(os.path.join(out, "spent.json")) as f:
            left = json.load(f)
    except (OSError, ValueError):
        return None
    return left if left.get("stopped_at_limit") else None


class Story:
    def __init__(self, out, work, dirs, left=None):
        self.out, self.work, self.dirs = out, work, dirs
        left = left or {}
        self.calls = left.get("calls", [])
        self.started = time.time() - left.get("total", {}).get("wall_s", 0)
        self.began = left.get("began", time.time())
        self.sid, self.said, self.prompt = left.get("sid"), left.get("said"), left.get("prompt")

    def run(self, max_calls, max_seconds):
        if self.prompt:
            said, sid = self.turn(self.prompt, self.sid)
        elif self.said:
            said, sid = self.turn(self.stand_in(self.said), self.sid)
        else:
            said, sid = self.turn(START, None)
        while len(self.calls) < max_calls and time.time() - self.started < max_seconds:
            if self.finished():
                self.log("trial", "Finished: the pull request is ready or the session is finished.")
                break
            said, sid = self.turn(self.stand_in(said), sid)
        else:
            self.log("trial", "Stopped: the run gave out before the session finished.")
        self.save()

    def turn(self, prompt, sid):
        self.prompt = prompt
        cmd = ["claude", "-p", prompt, "--output-format", "json", "--model", "opus", *self.dirs,
               "--settings", SETTINGS, "--dangerously-skip-permissions"]
        if sid:
            cmd += ["--resume", sid]
        self.log("user", prompt)
        began = time.time()
        p = subprocess.run(cmd, cwd=self.work, capture_output=True, text=True)
        waited = time.time() - began
        try:
            j = json.loads(p.stdout)
            said, sid = j.get("result", ""), j.get("session_id", sid)
            cost = j.get("total_cost_usd")
        except ValueError:
            said, cost = p.stdout[-4000:] + "\nSTDERR:" + p.stderr[-2000:], None
        if "hit your" in said and "limit" in said:
            self.save(stopped=True)
            raise Limit()
        self.sid, self.said, self.prompt = sid, said, None
        lines = [l for l in said.splitlines() if l.strip()]
        self.calls.append({"said_by_user": prompt, "waited_s": round(waited), "lines_read": len(lines),
                           "sign_off": "/rn:ty" in said, "cost_usd": cost})
        self.log(f"rn (waited {round(waited)} s, {len(lines)} lines)", said)
        self.save()
        return said, sid

    def stand_in(self, said):
        prompt = (ACCOUNT_PART + "\n\nrn just said:\n\n" + said +
                  "\n\nReply as the user would, in Japanese, or with the command you would type. "
                  "Output only your reply.")
        r = subprocess.run(["claude", "-p", prompt, "--model", "opus", "--settings", SETTINGS],
                           cwd=self.out, capture_output=True, text=True)
        reply = r.stdout.strip()
        if "hit your" in reply and "limit" in reply:
            self.save(stopped=True)
            raise Limit()
        return reply

    def finished(self):
        branch = self.git("branch", "--show-current").strip()
        if not branch or branch == "main":
            return False
        # An earlier run may have left a closed pull request on a branch of the same name.
        r = subprocess.run(["gh", "pr", "list", "-R", REPO, "--head", branch, "--state", "all",
                            "--json", "isDraft,state,createdAt"], cwd=self.work, capture_output=True,
                           text=True)
        try:
            prs = json.loads(r.stdout)
        except ValueError:
            return False
        since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.began))
        prs = [pr for pr in prs if pr.get("createdAt", "") >= since]
        if any(pr.get("state") != "OPEN" or not pr.get("isDraft") for pr in prs):
            return True
        found = self.git("grep", "-l", "-E", "^status: finished|Status\\*\\*: finished", "HEAD", "--", ".rn")
        return bool(found.strip())

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.work, capture_output=True, text=True).stdout

    def log(self, who, text):
        with open(os.path.join(self.out, "transcript.md"), "a") as f:
            f.write(f"\n## {who} ({time.strftime('%H:%M:%S')})\n\n{text}\n")

    def save(self, stopped=False):
        total = {
            "calls": len(self.calls),
            "waited_s": sum(c["waited_s"] for c in self.calls),
            "lines_read": sum(c["lines_read"] for c in self.calls),
            "sign_offs": sum(c["sign_off"] for c in self.calls),
            "wall_s": round(time.time() - self.started),
            "cost_usd": round(sum(c["cost_usd"] or 0 for c in self.calls), 2),
        }
        with open(os.path.join(self.out, "spent.json"), "w") as f:
            json.dump({"total": total, "calls": self.calls, "stopped_at_limit": stopped,
                       "sid": self.sid, "said": self.said, "prompt": self.prompt, "began": self.began},
                      f, indent=2, ensure_ascii=False)

    def close_pull_request(self):
        """Close the run's pull request and delete its branch, so the practice repository keeps only
        main; the clone keeps all."""
        branch = self.git("branch", "--show-current").strip()
        if branch and branch != "main":
            subprocess.run(["gh", "pr", "close", branch, "-R", REPO, "--delete-branch"],
                           cwd=self.work, capture_output=True, text=True)


if __name__ == "__main__":
    main()
