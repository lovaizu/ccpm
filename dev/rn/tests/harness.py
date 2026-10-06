"""A repository with an rn session in it, and a way to run rn's hooks on it with the JSON Claude
Code sends, through their entry files."""
import json
import os
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "..", "..", "..", "rn")
HOOKS = os.path.join(PLUGIN, "hooks")

STEERING = """---
rn: 0.9.0
pr: https://github.com/you/repo/pull/1
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

A wrong type fails the build.

# Acceptance criteria

## Attractive quality

- A1: Code reproducing each bug fails the build

## Must-be quality

- M1: The app builds as before

# Assumptions

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off
"""

VERIFICATION = """# verification

## Scenes

### A1: Code reproducing each bug fails the build

- A scene.

    Passes when it fails the build, and M1 holds.

## Machine checks
"""

SDIR = ".rn/20261003-typescript"


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.remote = os.path.join(self.tmp.name, "remote.git")
        self.dir = os.path.join(self.tmp.name, "work")
        self.data = os.path.join(self.tmp.name, "data")
        sh(self.tmp.name, "git", "init", "-q", "--bare", "-b", "main", self.remote)
        sh(self.tmp.name, "git", "clone", "-q", self.remote, self.dir)
        sh(self.dir, "git", "config", "user.name", "t")
        sh(self.dir, "git", "config", "user.email", "t@example.com")
        self.write("README.md", "app\n")
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", "init")
        sh(self.dir, "git", "push", "-qu", "origin", "main")
        sh(self.dir, "git", "remote", "set-head", "origin", "main")
        sh(self.dir, "git", "switch", "-qc", "session")
        self.write(f"{SDIR}/steering.md", STEERING)
        self.write("docs/verification.md", VERIFICATION)
        self.commit("rn: start\n\n● plan ── started → working out the plan")
        sh(self.dir, "git", "push", "-qu", "origin", "session")

    def write(self, rel, text):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
        return p

    def commit(self, msg):
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", msg)

    def hook(self, entry, **data):
        data.setdefault("cwd", self.dir)
        data.setdefault("session_id", "s1")
        env = dict(os.environ, CLAUDE_PLUGIN_DATA=self.data)
        r = subprocess.run(["python3", os.path.join(HOOKS, entry + ".py")], input=json.dumps(data),
                           cwd=self.dir, capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr

    def after_commit(self):
        return self.hook("posttooluse", tool_name="Bash", tool_input={"command": "git commit -F m"})


PROPOSE = "rn: propose\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off"
FEEDBACK = ("rn: feedback\n\n● #1 Plan sign-off ── feedback in 01-feedback-plan.md → working out "
            "the plan again")
PAUSE = "rn: pause\n\n● #3 cart ── half → paused at #3 cart"
REPORT = "# Report\n\nDoing as written, the build failed at cart.ts:3.\n"
PROPOSAL = ("rn: propose\n\n### What you get\n- Good A1: the build stops each bug, at a.ts:3\n"
            "- More: the key is unchecked, at b.ts:9\n\n"
            "● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
FINISHED = STEERING.replace("status: running", "status: finished") \
    .replace("### [ ] #1:", "### [x] #1:").replace("### [ ] #2:", "### [x] #2:")
QUOTING = STEERING.replace("### [ ] #2: Design sign-off",
                           "### [x] #2: Design sign-off\n### [ ] #3: Apply the discount before "
                           "the coupon\n\nServes: A1, M1")
PAUSED_MAP = ("── typescript: A wrong type fails the build. ──\n"
              "✅ #1 Plan sign-off / #2 Design sign-off\n"
              "👉 #3 Apply the discount before the coupon ── ここで一時停止\n\n"
              "● #3 Apply the discount before the coupon ── half → paused at #3 Apply the discount "
              "before the coupon\n\n次: /clear してから /rn:up")


class Session(unittest.TestCase):
    def setUp(self):
        self.r = Repo()

    def tearDown(self):
        self.r.tmp.cleanup()

    def post_write(self, rel):
        return self.r.hook("posttooluse", tool_name="Write",
                           tool_input={"file_path": os.path.join(self.r.dir, rel)})

    def settle_report_whole(self):
        self.r.write(f"{SDIR}/open/01-report-task-3.md", REPORT)
        self.r.commit("rn: report\n\n● #3 cart ── report in → settle")
        os.remove(os.path.join(self.r.dir, SDIR, "open/01-report-task-3.md"))
        self.r.commit("rn: settle\n\n01-report-task-3.md:\n    # Report\n\n    Doing as written, the "
                      "build failed at cart.ts:3.\n\n● #3 cart ── purpose fulfilled → #4")

    def move_main_ahead(self):
        sh(self.r.dir, "git", "switch", "-q", "main")
        self.r.write("b.txt", "b\n")
        self.r.commit("main moves")
        sh(self.r.dir, "git", "push", "-q", "origin", "main")
        sh(self.r.dir, "git", "switch", "-q", "session")

    def pause_after_dn(self):
        self.r.hook("userpromptexpansion", command_name="rn:dn")
        self.r.write("a.txt", "a\n")
        self.r.commit(PAUSE)
        self.r.after_commit()
        sh(self.r.dir, "git", "commit", "-q", "--amend", "-m",
           "rn: pause at #3\n\n● #3 cart ── half → paused at #3 cart")

    def commit_quoting_record_and_push(self):
        self.r.write(f"{SDIR}/steering.md", QUOTING)
        self.r.commit("rn: pause\n\n● #3 Apply the discount before the coupon ── half → paused at #3 "
                      "Apply the discount before the coupon")
        sh(self.r.dir, "git", "push", "-q")

    def first_user_write(self, path):
        return self.r.hook("pretooluse", agent_type="rn:first-user", agent_id="f1", tool_name="Write",
                           tool_input={"file_path": path})

    def first_user_pre(self, tool, inp):
        return self.r.hook("pretooluse", agent_type="rn:first-user", agent_id="f2", tool_name=tool,
                           tool_input=inp)
