#!/usr/bin/env python3
"""Run the mock plugin on fw as its user would, with a stand-in user, clear the conversation partway,
come back, and finish; meanwhile another session works in the same repository. Then check fw's flow
by code from the JSONL of every conversation and role, and from the CCS (checks.py).

    python3 dev/fw/trials/story.py --mode p --out <new dir outside the repository>
    python3 dev/fw/trials/story.py --mode pty --out <new dir outside the repository>

`p` runs each user turn with `claude -p`, and clears the conversation by ending it once the sum
is fixed. `pty` drives a real interactive session (session.py), where the user tells the conductor
to stop for the day at that point and then types /clear. Everything lands in <out>/; the JSONL in
~/.claude/projects/<the run's repository, encoded>/. A run takes many minutes.
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid

TRIALS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TRIALS)))
sys.path.insert(0, TRIALS)
sys.path.insert(0, os.path.join(REPO, "fw", "scripts"))

import ccs  # noqa: E402
import checks  # noqa: E402
from session import Session, clean_env  # noqa: E402

PLUGINS = ["--plugin-dir", os.path.join(REPO, "fw"), "--plugin-dir", os.path.join(TRIALS, "mock")]
OPENING = "/mock:up Answer two questions for my friend Sam."
RESUME = "/mock:up"
PAUSE = "Let's stop here for today. I will clear the conversation and come back to it later."
OTHER = ("Write the file notes/open/01-report-notes.md with the single line 'hi'. Then start an "
         "Explore agent in the background to list the files under notes/, and when it has replied, send "
         "it a message with SendMessage asking how many files it found. Report its two answers.")
STAND_IN = """You asked a tool, in English, to answer two questions for your friend Sam, with these words:

{opening}

You know only that, and you have no wishes about the questions or how the answers are written:
whatever the tool proposes for those is fine with you. Reply to what the tool just said as that user
would: approve a plan or steering that answers two questions for Sam; when asked whether to
send something as an issue, answer no. When the tool
asks you nothing and only reports what it did, output exactly DONE. Output only your reply.

The tool just said:

{said}"""
MAX_TURNS = 8
# The conductor's roles run on a small model, even where the conductor names one: the trial checks the flow.
ROLES = {"CLAUDE_CODE_SUBAGENT_MODEL": "haiku", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"}


def settings(out, name="settings.json", log_turns=True):
    """Allow only what the run needs; deny the rest without asking. The hook logs the turn ends of
    the session under test for the interactive driver; the other session gets none, so its turn ends
    are never taken for the driven session's."""
    log = f"python3 -c \"import sys; open('{out}/events.jsonl','a').write(sys.stdin.read().replace(chr(10),' ')+chr(10))\""
    data = {
        "permissions": {"defaultMode": "dontAsk", "allow": [
            "Read", "Write", "Edit", "Glob", "Grep", "Agent", "SendMessage", "TaskStop", "Skill", "ToolSearch",
            "Bash(git:*)", "Bash(python3:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(mkdir:*)", "Bash(rm:*)"]},
        "enabledPlugins": {"writ@ccpm": False, "rn@ccpm": False, "pith@ccpm": False, "fw@ccpm": False},
        "hooks": {"Stop": [{"hooks": [{"type": "command", "command": log}]}]} if log_turns else {},
    }
    path = os.path.join(out, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def setup(out):
    if os.path.exists(out):
        sys.exit(f"{out} exists; give a new directory")
    repo = os.path.join(out, "repo")
    os.makedirs(repo)
    with open(os.path.join(repo, "README.md"), "w") as f:
        f.write("# Cards\n\nCards for friends.\n")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "Start"]):
        subprocess.run(["git", *args], cwd=repo, check=True, env=clean_env())
    return repo


def made_twice(repo):
    path = os.path.join(repo, ".mock", "sum", "make.yaml")
    return os.path.isfile(path) and sum(1 for e in ccs.load(path)["retrieved_artifacts"] if e[0] == "made") >= 2


class Run:
    def __init__(self, out, mode):
        self.out, self.mode = os.path.realpath(out), mode
        self.repo = setup(self.out)
        self.settings = settings(self.out)
        self.log = {"mode": mode, "conversations": [], "cut": None, "talk": []}

    def args(self):
        return [*PLUGINS, "--model", "opus", "--settings", self.settings, "--setting-sources", "project,local"]

    def say(self, who, text):
        self.log["talk"].append({"who": who, "text": text, "at": time.time()})
        self.save()

    def save(self):
        with open(os.path.join(self.out, "run.json"), "w") as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

    def stand_in(self, said):
        r = subprocess.run(["claude", "-p", STAND_IN.format(opening=OPENING, said=said), "--model", "opus",
                            "--tools", "", "--setting-sources", "", "--no-session-persistence"], cwd=self.out, capture_output=True,
                           text=True, env=clean_env(), stdin=subprocess.DEVNULL)
        return r.stdout.strip()

    def snapshot(self):
        """The record at the cut, and the state of each task in it."""
        cut = os.path.join(self.out, "cut")
        shutil.copytree(os.path.join(self.repo, ".mock"), cut)
        tasks = {t: ccs.state(os.path.join(cut, t)) for t in sorted(os.listdir(cut))
                 if os.path.isdir(os.path.join(cut, t)) and t != "open"}
        self.log["cut"] = {"at": time.time(), "states": tasks}
        self.save()

    # claude -p

    def p_turn(self, message, sid, new, watch=False):
        cmd = ["claude", "-p", message, "--output-format", "json", *self.args(),
               "--session-id" if new else "--resume", sid]
        self.say("user", message)
        proc = subprocess.Popen(cmd, cwd=self.repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                env={**clean_env(), **ROLES}, stdin=subprocess.DEVNULL, start_new_session=True)
        while proc.poll() is None:
            if watch and made_twice(self.repo):
                time.sleep(10)
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait()
                self.snapshot()
                self.say("trial", "The conversation was ended here, as if cleared, once the sum was fixed.")
                return None
            time.sleep(3)
        out, err = proc.communicate()
        try:
            said = json.loads(out).get("result", "")
        except ValueError:
            said = f"(no JSON) {out[-2000:]} {err[-2000:]}"
        self.say("conductor", said)
        return said

    def p_conversation(self, opening, watch):
        sid = str(uuid.uuid4())
        self.log["conversations"].append(sid)
        said = self.p_turn(opening, sid, True, watch)
        for _ in range(MAX_TURNS):
            if said is None:
                return
            reply = self.stand_in(said)
            if reply == "DONE":
                self.say("user", "DONE")
                return
            said = self.p_turn(reply, sid, False, watch and not self.log["cut"])

    # interactive

    def pty_conversation(self):
        sid = str(uuid.uuid4())
        self.log["conversations"].append(sid)
        session = Session(self.repo, [*self.args(), "--session-id", sid], os.path.join(self.out, "events.jsonl"),
                          checks.project_dir(self.repo), ROLES)
        message = OPENING
        try:
            for _ in range(2 * MAX_TURNS):
                self.say("user", message)
                session.type(message)
                cut = not self.log["cut"] and message != RESUME
                why = session.wait(3 * 3600, poll=(lambda: made_twice(self.repo)) if cut else None)
                if why == "polled":
                    self.say("user", PAUSE)
                    session.type(PAUSE)
                    session.wait(3600)
                    self.snapshot()
                    self.say("conductor", session.last_reply(self.newest()))
                    self.say("user", "/clear")
                    session.type("/clear")
                    time.sleep(5)
                    message = RESUME
                    continue
                said = session.last_reply(self.newest())
                self.say("conductor", said)
                if why == "timeout":
                    return
                reply = self.stand_in(said)
                if reply == "DONE":
                    self.say("user", "DONE")
                    return
                message = reply
        finally:
            session.close()

    def newest(self):
        """The conversation's JSONL: after /clear, the interactive session writes a new one."""
        folder = checks.project_dir(self.repo)
        files = [os.path.join(folder, n) for n in os.listdir(folder)
                 if n.endswith(".jsonl") and n != f"{self.log.get('other')}.jsonl"]
        return max(files, key=os.path.getmtime)

    def other(self):
        """Another session in the same repository, with the same plugins, doing work of its own."""
        self.log["other"] = str(uuid.uuid4())
        self.save()
        args = [a if a != self.settings else settings(self.out, "other-settings.json", False) for a in self.args()]
        cmd = ["claude", "-p", OTHER, "--output-format", "json", *args, "--session-id", self.log["other"]]
        return subprocess.Popen(cmd, cwd=self.repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                env=clean_env(), stdin=subprocess.DEVNULL)

    def main(self):
        if self.mode == "p":
            self.p_conversation(OPENING, watch=True)
            other = self.other()
            self.p_conversation(RESUME, watch=False)
        else:
            other = self.other()
            self.pty_conversation()
        out, _ = other.communicate()
        try:
            self.log["other_said"] = json.loads(out).get("result")
        except ValueError:
            self.log["other_said"] = out[-2000:]
        self.save()
        report = checks.run(self.repo, self.log)
        with open(os.path.join(self.out, "checks.md"), "w") as f:
            f.write(report)
        print(report)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["p", "pty"], required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.realpath(a.out).startswith(REPO + os.sep):
        sys.exit("--out must be outside the repository")
    Run(a.out, a.mode).main()
