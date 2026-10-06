"""What every trial shares: the practice repository, a turn of rn, the stand-in, and the record.

A trial runs rn as its user would, through `claude -p`, and writes the conversation to
`<out>/transcript.md` for the first user to read with the clone it ran in.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

RN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn"))
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
REPO = "lovaizu/rn-try"
MAX_TURNS = 60

ACCOUNT_PART = """You are the user of a small shop backend, talking with a tool called rn in Japanese.
You started with: /rn:on move src/account to TypeScript
- Why you want this, said only when asked why: users who signed up with only an email see
  "undefined undefined" as their name, and support keeps getting tickets about it.
- What you know, said only when asked: in a user record, nickname, firstName, and lastName can each
  be missing, null, or "".
- What you want for a user with no name, when asked: something that tells users apart and gives away
  nothing private. Asked to choose among ways, you choose by what each gives and costs, and ask back
  when no way gives what you want or the question leaves out what they cost.
- You do not know whether every record has an email and cannot find out before the release; when
  asked, you say to go on as if every record has one.
- At a sign-off (rn shows a map with 👉 and asks for /rn:ty or /rn:gm), you approve with /rn:ty when
  the proposal shows nothing against your reason and decisions, and otherwise give /rn:gm followed by
  what you saw.
- When rn says to say "go on", you say: go on
You never look at the code or the pull request yourself. You know nothing else; when asked something
you do not know, say you do not know."""

COUPON_PART = """You are the user of a small shop backend, talking with a tool called rn in Japanese.
You started a session to make every coupon a discount, so no coupon makes an order cost more than it
would without one; you approved its plan and design earlier.
- Why you want this, said only when asked why: a coupon once took an order's total below 0, and money
  went back to the customer by mistake.
- What you decide, when asked what to do with a coupon that is not a discount: such a coupon refuses
  the order.
- At a sign-off (rn shows a map with 👉 and asks for /rn:ty or /rn:gm), you approve with /rn:ty when
  the proposal shows nothing against your reason and decisions, and otherwise give /rn:gm followed by
  what you saw.
- When rn says to say "go on", you say: go on
You never look at the code or the pull request yourself. You know nothing else; when asked something
you do not know, say you do not know."""


class Stop(Exception):
    """The run cannot go on, such as at the usage limit."""


class Trial:
    def __init__(self, description):
        ap = argparse.ArgumentParser(description=description)
        ap.add_argument("--writ", required=True, help="the writ plugin directory")
        ap.add_argument("--out", required=True, help="a new directory for the clone and record")
        a = ap.parse_args()
        if os.path.exists(a.out):
            sys.exit(f"{a.out} exists; give a new directory")
        os.makedirs(a.out)
        self.out = os.path.abspath(a.out)
        self.writ = os.path.abspath(a.writ)
        self.work = os.path.join(self.out, "work")
        self.record = os.path.join(self.out, "transcript.md")
        self.dirs = ["--plugin-dir", RN, "--plugin-dir", self.writ]
        clone(self.work)

    def log(self, who, text):
        with open(self.record, "a") as f:
            f.write(f"\n## {who} ({time.strftime('%H:%M:%S')})\n\n{text}\n")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.work, capture_output=True, text=True).stdout

    def turn(self, prompt, sid=None, stop_when=None):
        """One turn of rn; `stop_when`, checked every 15 seconds, interrupts it as a user would."""
        cmd = ["claude", "-p", prompt, "--output-format", "json", "--model", "opus", *self.dirs,
               "--dangerously-skip-permissions"]
        if sid:
            cmd += ["--resume", sid]
        self.log("stand-in → rn", prompt)
        p = subprocess.Popen(cmd, cwd=self.work, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
        stopped = False
        while p.poll() is None:
            time.sleep(15)
            if stop_when and stop_when():
                os.killpg(p.pid, signal.SIGINT)
                time.sleep(10)
                if p.poll() is None:
                    os.killpg(p.pid, signal.SIGTERM)
                stopped = True
                break
        out, err = p.communicate()
        try:
            j = json.loads(out)
            said, sid = j.get("result", ""), j.get("session_id", sid)
            if not said:
                said = "(no result) " + json.dumps({k: v for k, v in j.items() if k != "result"})
        except ValueError:
            said = out[-4000:] + "\nSTDERR:" + err[-2000:]
        self.log("rn" + (" (stopped by the trial)" if stopped else ""), said)
        if re.search(r"hit your \w+ limit", said):
            raise Stop("usage limit")
        return said, sid, stopped

    def stand_in(self, part, said):
        prompt = (part + "\n\nrn just said:\n\n" + said +
                  "\n\nReply as the user would, in Japanese, or with the command you would type. "
                  "Output only your reply.")
        r = subprocess.run(["claude", "-p", prompt, "--model", "opus"], cwd=self.out,
                           capture_output=True, text=True)
        return r.stdout.strip()

    def waiting_for(self):
        """The sign-off rn stops at, from the decision line of its last commit, which keeps
        `waiting for #N <name>` in the artifact language whatever the conversation's."""
        m = re.search(r"waiting for #\d+ ([^\n]*sign-off)", self.git("log", "-1", "--format=%B"))
        return m.group(1) if m else None

    def start_from(self, fixture):
        """Commit a fixture on its session branch and open the session's draft pull request."""
        here = os.path.join(FIXTURES, fixture)
        shutil.copytree(os.path.join(here, "tree"), self.work, dirs_exist_ok=True)
        branch = read(os.path.join(here, "branch.txt")).strip()
        message = read(os.path.join(here, "commit.txt"))
        self.git("checkout", "-q", "-b", branch)
        self.git("add", "-A")
        self.commit(message)
        self.git("push", "-q", "-u", "origin", branch)
        url = subprocess.run(["gh", "pr", "create", "-R", REPO, "--draft", "--base", "main",
                              "--head", branch, "--title", f"Fixture {fixture}", "--body",
                              f"Fixture {fixture}"],
                             cwd=self.work, capture_output=True, text=True).stdout.strip()
        for root, _, files in os.walk(os.path.join(self.work, ".rn")):
            for name in files:
                path = os.path.join(root, name)
                text = read(path)
                if "PR_URL" in text:
                    with open(path, "w") as f:
                        f.write(text.replace("PR_URL", url))
        self.git("add", "-A")
        self.commit(message.replace("PR_URL", url), "--amend")
        self.git("push", "-q", "-f")
        self.log("trial", f"Started from fixture `{fixture}` on {branch}: {url}")

    def commit(self, message, *args):
        subprocess.run(["git", "commit", "-q", *args, "-F", "-"], cwd=self.work, input=message,
                       text=True, check=True)

    def head(self):
        return self.git("rev-parse", "HEAD").strip()

    def run(self, scene):
        try:
            scene()
        except Stop as e:
            self.log("trial", f"Stopped: {e}.")
            sys.exit(3)
        finally:
            self.close_pull_request()
        print(self.record)

    def close_pull_request(self):
        """Close the run's pull request and delete its branch, so the practice repository keeps only
        main and the next run starts where the verification document says; the clone keeps all."""
        branch = self.git("branch", "--show-current").strip()
        if branch and branch != "main":
            subprocess.run(["gh", "pr", "close", branch, "-R", REPO, "--delete-branch"],
                           cwd=self.work, capture_output=True, text=True)


def read(path):
    with open(path) as f:
        return f.read()


def clone(path):
    subprocess.run(["git", "clone", "-q", f"https://github.com/{REPO}.git", path], check=True)
