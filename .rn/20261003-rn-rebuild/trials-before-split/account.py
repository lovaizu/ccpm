#!/usr/bin/env python3
"""Drive one verification session of rn with a stand-in user (scratch harness for task #6)."""
import json, os, re, subprocess, sys, time, signal

HERE = os.path.dirname(os.path.abspath(__file__))
RN = "/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/rebuild-rn/rn"
WRIT = os.path.join(HERE, "writ-src", "writ")
WORK = os.path.join(HERE, "work")
LOG = os.path.join(HERE, "transcript.md")
READER = os.path.join(HERE, "reader")
MAX_TURNS = 60

ACCOUNT_PART = """You are the user of a small shop backend, talking with a tool called rn in Japanese.
You started with: /rn:on move src/account to TypeScript
- Why you want this, said only when asked why: users who signed up with only an email see
  "undefined undefined" as their name, and support keeps getting tickets about it.
- What you know, said only when asked: in a user record, nickname, firstName, and lastName can each
  be missing, null, or "".
- What you want for a user with no name, when asked: something that tells users apart and gives away
  nothing private. You choose among the ways the question offers by what each gives and costs, and
  ask back when the question offers no ways or leaves out what they cost.
- Whether every record has an email you do not know and cannot find out before the release; when
  asked, you say to go on as if every record has one.
- At a sign-off (rn shows a map with 👉 and asks for /rn:ty or /rn:gm), you approve with /rn:ty when
  the proposal shows nothing against your reason and decisions, and otherwise give /rn:gm followed by
  what you saw.
- When rn says to say "go on", you say: go on
You never look at the code or the pull request yourself. You know nothing else; when asked something
you do not know, say you do not know."""


def log(who, text):
    with open(LOG, "a") as f:
        f.write(f"\n## {who} ({time.strftime('%H:%M:%S')})\n\n{text}\n")


def rn_turn(prompt, sid=None, watch=None):
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--model", "opus",
           "--plugin-dir", RN, "--plugin-dir", WRIT, "--dangerously-skip-permissions"]
    if sid:
        cmd += ["--resume", sid]
    log("stand-in → rn", prompt)
    p = subprocess.Popen(cmd, cwd=WORK, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         start_new_session=True)
    killed = False
    while p.poll() is None:
        time.sleep(15)
        if watch and watch():
            os.killpg(p.pid, signal.SIGINT)
            time.sleep(10)
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGTERM)
            killed = True
            break
    out, err = p.communicate()
    try:
        j = json.loads(out)
        res, sid2 = j.get("result", ""), j.get("session_id", sid)
    except Exception:
        res, sid2 = out[-4000:] + "\nSTDERR:" + err[-2000:], sid
    log("rn" + (" (stopped by the harness)" if killed else ""), res)
    if "hit your session limit" in res or "hit your usage limit" in res:
        log("harness", "Usage limit: run stopped.")
        sys.exit(3)
    return res, sid2, killed


def stand_in(part, message):
    prompt = (part + "\n\nrn just said:\n\n" + message +
              "\n\nReply as the user would, in Japanese, or with the command you would type. "
              "Output only your reply.")
    r = subprocess.run(["claude", "-p", prompt, "--model", "opus"], cwd=HERE, capture_output=True,
                       text=True)
    return r.stdout.strip()


PR_READER = """You decide this sign-off by reading the real thing, not rn's message: the pull request
{url} (use gh pr view / gh pr diff, and read the files on its branch in this clone; run
git fetch and git checkout of the branch first if needed). Read the plan (.rn/*/steering.md), the
README, docs/design.md, docs/verification.md, and the code as far as you need to decide. Do not
change, commit, or push anything. You know only your part above.

The sign-off now waiting is: {signoff}.

Reply with /rn:ty if what is on the pull request shows nothing against your reason and decisions,
and otherwise /rn:gm followed by what you saw. Then, after a line '---', list in a few lines what on
the pull request you based it on."""


def pr_reader(part, signoff, message):
    m = re.search(r"https://github\.com/\S+/pull/\d+", message)
    url = m.group(0) if m else "(the open pull request of lovaizu/rn-try)"
    prompt = part.replace("You never look at the code or the pull request yourself.", "") + \
        "\n\n" + PR_READER.format(url=url, signoff=signoff)
    r = subprocess.run(["claude", "-p", prompt, "--model", "opus", "--allowedTools",
                        "Bash(gh:*) Bash(git fetch:*) Bash(git checkout:*) Bash(git log:*) "
                        "Bash(git show:*) Bash(git diff:*) Bash(ls:*) Read Grep Glob"],
                       cwd=READER, capture_output=True, text=True)
    return r.stdout.strip()


def git(*a):
    return subprocess.run(["git", *a], cwd=WORK, capture_output=True, text=True).stdout


def waiting_for(text):
    """The sign-off rn stops at, read from its last commit: what rn says to the user is translated,
    while the decision line in the record keeps `waiting for #N <name>` in the artifact language."""
    body = git("log", "-1", "--format=%B")
    m = re.search(r"waiting for #(\d+) ([^\n]*sign-off)", body)
    return m.group(2) if m else None


def checked_tasks():
    out = git("ls-files", ".rn")
    n = 0
    for f in out.split():
        if f.endswith("steering.md"):
            n += len(re.findall(r"^### \[x\] #", open(os.path.join(WORK, f)).read(), re.M))
    return n


DESIGN_DONE = None


def second_task_editing():
    dirty = git("status", "--porcelain", "--", "src", "test")
    return DESIGN_DONE is not None and checked_tasks() >= DESIGN_DONE + 1 and bool(dirty.strip())


def account(resume=False):
    global DESIGN_DONE
    part = ACCOUNT_PART
    if resume:
        log("harness", "Resumed after an interruption (harness or usage limit): /clear, then /rn:up")
        msg, sid, _ = rn_turn("/rn:up")
    else:
        msg, sid, _ = rn_turn("/rn:on move src/account to TypeScript")
    plan_feedback_given = resume
    design_cleared = False
    paused = False
    for _ in range(MAX_TURNS):
        w = waiting_for(msg)
        if re.search(r"── approved → finished", git("log", "-1", "--format=%B")):
            log("harness", "Session finished.")
            return
        if w == "Plan sign-off" and not plan_feedback_given:
            plan_feedback_given = True
            reply = '/rn:gm a user whose last name is null is shown "Ann null"'
        else:
            reply = stand_in(part, msg)
            if w:
                log(f"second stand-in, reading the pull request at {w}", pr_reader(part, w, msg))
        if w == "Design sign-off" and reply.strip().startswith("/rn:ty"):
            design_cleared = True
            DESIGN_DONE = checked_tasks() + 1
            log("harness", f"Design sign-off approved; tasks checked with it: {DESIGN_DONE}")
        watch = None
        if design_cleared and not paused:
            watch = second_task_editing
        msg, sid, killed = rn_turn(reply, sid, watch)
        if killed and not paused:
            paused = True
            msg, sid, _ = rn_turn("/rn:dn", sid)
            log("harness", "/clear")
            msg, sid, _ = rn_turn("/rn:up")
    log("harness", "Turn limit reached.")


if __name__ == "__main__":
    if sys.argv[1] == "account":
        for d in (WORK, READER):
            if not os.path.isdir(d):
                subprocess.run(["git", "clone", "-q", "https://github.com/lovaizu/rn-try.git", d],
                               check=True)
        account(resume=len(sys.argv) > 2 and sys.argv[2] == "resume")
