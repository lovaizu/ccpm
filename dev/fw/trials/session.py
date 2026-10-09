"""Drive a real interactive Claude Code session from Python's standard library, as a user at a
terminal would: type a message, and know when the turn has truly ended.

`claude -p` behaves differently from the interactive session, where roles run in the background and
the user can type while they work. The session runs in a pseudo-terminal. A Stop and a SubagentStop
hook, given in the run's settings file, append each event to a file; a turn has ended when a Stop has
come and no background work is left running.

The inherited CLAUDE* environment variables are removed: with them the session runs as a child of
the caller's own session and writes no JSONL.
"""
import json
import os
import pty
import re
import select
import subprocess
import threading
import time

TRUST = re.compile(r"Yes,?Itrustthisfolder", re.I)


def clean_env():
    return {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}


class Session:
    def __init__(self, cwd, args, events):
        self.events, self.screen, self.alive = events, "", True
        master, slave = pty.openpty()
        self.proc = subprocess.Popen(["claude", *args], cwd=cwd, env={**clean_env(), "TERM": "xterm-256color"},
                                     stdin=slave, stdout=slave, stderr=slave, start_new_session=True)
        os.close(slave)
        self.master = master
        threading.Thread(target=self._read, daemon=True).start()
        self._answer_trust()

    def _read(self):
        while self.alive:
            ready, _, _ = select.select([self.master], [], [], 0.5)
            if ready:
                try:
                    chunk = os.read(self.master, 65536)
                except OSError:
                    return
                self.screen = (self.screen + chunk.decode("utf-8", "replace"))[-200000:]

    def _answer_trust(self):
        """A new folder asks once whether its files are trusted; the trial's own folder is."""
        deadline = time.time() + 60
        while time.time() < deadline:
            plain = re.sub(r"\s", "", re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", self.screen))
            if TRUST.search(plain):
                os.write(self.master, b"\x1b[B")  # the first choice is "No, exit"
                time.sleep(0.5)
                os.write(self.master, b"\r")
                self.screen = ""
                time.sleep(5)
                return
            if "forshortcuts" in plain:
                time.sleep(2)
                return
            time.sleep(0.5)

    def type(self, text):
        """Type a message and press Enter."""
        self.mark = self._count()
        os.write(self.master, text.encode())
        time.sleep(1.0)
        os.write(self.master, b"\r")

    def _read_events(self):
        try:
            with open(self.events) as f:
                return [json.loads(line) for line in f if line.strip()]
        except OSError:
            return []

    def _count(self):
        return len(self._read_events())

    def ended(self):
        """Whether the turn begun by the last message has ended: a Stop since it, with nothing left
        running in the background, and no event for a few seconds after."""
        events = self._read_events()[self.mark:]
        stops = [e for e in events if e.get("hook_event_name") == "Stop"]
        if not stops or events[-1].get("hook_event_name") != "Stop":
            return False
        running = [t for t in stops[-1].get("background_tasks") or [] if t.get("status") == "running"]
        return not running and time.time() - os.path.getmtime(self.events) > 5

    def wait(self, timeout, poll=None):
        """Wait for the turn to end; `poll` is called every few seconds and may return True to stop
        waiting early."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.ended():
                return "ended"
            if poll and poll():
                return "polled"
            time.sleep(3)
        return "timeout"

    def last_reply(self, transcript):
        """The assistant's last text in the session's JSONL."""
        said = ""
        try:
            with open(transcript) as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant":
                        content = entry["message"].get("content") or []
                        text = "\n".join(b.get("text", "") for b in content if b.get("type") == "text")
                        said = text or said
        except OSError:
            pass
        return said

    def close(self):
        """Leave as a user would, then make sure the process is gone."""
        try:
            os.write(self.master, b"/exit\r")
            self.proc.wait(timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            self.proc.terminate()
            try:
                self.proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        self.alive = False
        os.close(self.master)
