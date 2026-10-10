"""A repository, a conversation's JSONL as Claude Code writes it, and a way to run turn's hook and
scripts on them as Claude Code does."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TURN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "turn"))
sys.path[:0] = [os.path.join(TURN, "scripts"), os.path.join(TURN, "hooks")]

RECORD = '''focal_entities:
  - work: "SETUP.md"
  - receiver: "a newcomer"
goal_orientation:
  - acceptance: "the app starts"
  - use: "follow it from the top"
constraints:
  - language: "English"
'''
ARGS = "in: .caller/1.yaml\nout: .caller/2.yaml\ndomain: /plugin/domain"


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.realpath(self.tmp.name)
        self.home = os.path.join(self.dir, "home")
        self.work = os.path.join(self.dir, "work")
        os.makedirs(self.work)
        subprocess.run(["git", "init", "-q"], cwd=self.work, check=True)
        self.write(".caller/1.yaml", RECORD)
        self.sid = "s1"
        self.transcript = os.path.join(self.home, "projects", "p", self.sid + ".jsonl")
        os.makedirs(os.path.dirname(self.transcript))
        self.lines = []
        self.n = 0

    def close(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        path = os.path.join(self.work, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.work, rel)) as f:
            return f.read()

    def add(self, entry):
        self.lines.append(json.dumps(entry))
        with open(self.transcript, "w") as f:
            f.write("\n".join(self.lines + ["not json"]) + "\n")

    def tool(self, name, inp, result=None):
        """The assistant calls a tool; with result, the tool's result names an agent ID."""
        self.n += 1
        tid = f"t{self.n}"
        self.add({"type": "assistant", "message": {"content": [
            {"type": "text", "text": "."}, {"type": "tool_use", "id": tid, "name": name, "input": inp}]}})
        if result:
            self.add({"type": "user", "toolUseResult": {"agentId": result},
                      "message": {"content": [{"type": "tool_result", "tool_use_id": tid}]}})
        return tid

    def turn_up(self, args=ARGS):
        self.tool("Skill", {"skill": "turn:up", "args": args})

    def agent(self, what, aid, acts=()):
        """turn's agent `what` is called, and does `acts`, each (tool, input)."""
        self.tool("Agent", {"subagent_type": "turn:" + what, "prompt": "p"}, result=aid)
        path = os.path.join(self.transcript[:-len(".jsonl")], "subagents", f"agent-{aid}.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            for tool, inp in acts:
                f.write(json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": tool, "input": inp}]}}) + "\n")

    def env(self):
        return dict(os.environ, CLAUDE_CODE_SESSION_ID=self.sid, CLAUDE_CONFIG_DIR=self.home)

    def hook(self, tool, inp, **extra):
        data = dict({"tool_name": tool, "tool_input": inp, "cwd": self.work,
                     "transcript_path": self.transcript}, **extra)
        return subprocess.run([sys.executable, os.path.join(TURN, "hooks", "pretooluse.py")],
                              input=json.dumps(data), capture_output=True, text=True)

    def script(self, name, *args, env=None):
        return subprocess.run([sys.executable, os.path.join(TURN, "scripts", name), *args],
                              cwd=self.work, capture_output=True, text=True,
                              env=env or self.env())
