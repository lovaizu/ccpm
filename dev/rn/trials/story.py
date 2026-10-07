#!/usr/bin/env python3
"""The README's story end to end, at the size it promises: the user asks rn for a Claude Code plugin
that turns a pull request's commits and review comments into rules and their checks, on the practice
repository, whose `main` is first set to `fixtures/start/`. A stand-in answers, clears the
conversation after each approval and comes back with `/rn:up`, until the pull request is ready, the
session is finished, or the run gives out. Records what the user spent: how long each turn kept them
waiting, how many lines they read, and each time they were called.

Run it with any rn, so a rebuilt rn is set beside the version in use (rn 0.8.0); runs share the
practice repository, so run them one at a time.

    python3 dev/rn/trials/story.py --rn rn --writ writ --pith pith --out <new dir>
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
START_TREE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "start")
REPO = "lovaizu/rn-try"
START = ("/rn:on PRの事実（コミット履歴、レビューコメント）から意図を抜き出してルールにし、"
         "そのルールを検査するコードか観点を作るプラグインを作りたい")
# Installed copies would answer in place of the plugins under test.
SETTINGS = json.dumps({"enabledPlugins": {"rn@ccpm": False, "writ@ccpm": False, "pith@ccpm": False}})

PART = """You lead a team that builds software with AI help, and you are talking with a tool called rn in
Japanese. You started with: /rn:on PRの事実（コミット履歴、レビューコメント）から意図を抜き出してルールにし、
そのルールを検査するコードか観点を作るプラグインを作りたい
- Why you want this, said only when asked why: the same remarks keep coming back in review, and the
  commit history shows the same slips fixed again and again. You want each turned into a rule, and
  the rule checked automatically, by code, or by viewpoints an AI review uses, so the author catches
  it in a self-check before review.
- What you know, said only when asked: the pull requests to learn from are on GitHub; as the example
  to build and try it on, use pydantic/pydantic-ai #3611 ("Add `tool_choice` setting", 166 commits,
  about 250 review threads), and to see whether the rules prevent mistakes in another pull request,
  pydantic/pydantic-ai #5143. The plugin goes in this repository, which holds the team's Claude Code
  plugins. About a week of work is worth it to you; more is not.
- Asked whether to create a repository, fork, or push anywhere outside this repository: no; try it on a
  local clone, since you do not want anything made under your account for this.
- Asked to choose among ways, you choose by what each gives and costs, and ask back when no way gives
  what you want or the question leaves out what they cost.
- When asked something you do not know, say you do not know.
- At a sign-off (rn shows a map with 👉 and asks for /rn:ty or /rn:gm), you approve with /rn:ty when
  the proposal shows nothing against your reason and decisions, and otherwise give /rn:gm followed by
  what you saw.
- Right after rn records your approval, you stop for the day: reply exactly /clear
You never look at the code or the pull request yourself."""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rn", required=True, help="the rn plugin directory under test")
    ap.add_argument("--writ", help="the writ plugin directory, when this rn uses it")
    ap.add_argument("--pith", help="the pith plugin directory, when this rn uses it")
    ap.add_argument("--out", required=True,
                    help="a new directory for the clone and record, or one a run stopped at the usage "
                         "limit left, to go on from there")
    ap.add_argument("--max-calls", type=int, default=60)
    ap.add_argument("--max-hours", type=float, default=10)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    work = os.path.join(out, "work")
    left = load(out)
    if left is None:
        if os.path.exists(out):
            sys.exit(f"{out} exists and holds no stopped run; give a new directory")
        os.makedirs(out)
        subprocess.run(["git", "clone", "-q", f"https://github.com/{REPO}.git", work], check=True)
        set_main(work)
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


def set_main(work):
    """Put the starting tree on the practice repository's main, as one commit on top, so every run starts
    from the same tree with no earlier session's plan or code in it."""
    for name in os.listdir(work):
        if name != ".git":
            path = os.path.join(work, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    shutil.copytree(START_TREE, work, dirs_exist_ok=True)
    subprocess.run(["git", "add", "-A"], cwd=work, check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=work).returncode:
        subprocess.run(["git", "commit", "-qm", "Start: the team's plugins"], cwd=work, check=True)
        subprocess.run(["git", "push", "-q", "origin", "main"], cwd=work, check=True)


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
            said, sid = self.reply(self.said, self.sid)
        else:
            said, sid = self.turn(START, None)
        while len(self.calls) < max_calls and time.time() - self.started < max_seconds:
            if self.finished():
                self.log("trial", "Finished: the pull request is ready or the session is finished.")
                break
            said, sid = self.reply(said, sid)
        else:
            self.log("trial", "Stopped: the run gave out before the session finished.")
        self.save()

    def reply(self, said, sid):
        """The stand-in's answer; after /clear the user comes back in a fresh conversation."""
        answer = self.stand_in(said)
        if answer.strip() == "/clear":
            self.log("user", "/clear")
            return self.turn("/rn:up", None)
        return self.turn(answer, sid)

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
        prompt = (PART + "\n\nrn just said:\n\n" + said +
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
