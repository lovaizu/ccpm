#!/usr/bin/env python3
"""Drive one verification session of rn with a stand-in user (scratch harness for task #6)."""
import json, os, re, subprocess, sys, time, signal

HERE = os.path.dirname(os.path.abspath(__file__))
RN = "/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/rebuild-rn/rn"
WRIT = os.path.join(HERE, "writ-src", "writ")
WORK = os.path.join(HERE, "work-coupon")
LOG = os.path.join(HERE, "transcript-coupon.md")
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


def git(*a):
    return subprocess.run(["git", *a], cwd=WORK, capture_output=True, text=True).stdout


def waiting_for(text):
    m = re.search(r"waiting for #(\d+) ([^\n]*sign-off)", text)
    return m.group(2) if m else None


def second_task_editing():
    msgs = git("log", "-30", "--format=%B")
    first_done = re.search(r"#3 [^\n]*── [^\n]*purpose fulfilled", msgs)
    dirty = git("status", "--porcelain", "--", "src", "test")
    return bool(first_done) and bool(dirty.strip())


def move_names_under_profile():
    hand = os.path.join(HERE, "hand")
    subprocess.run(["rm", "-rf", hand])
    subprocess.run(["git", "clone", "-q", "https://github.com/lovaizu/rn-try.git", hand])
    acc = os.path.join(hand, "src/account/account.js")
    open(acc, "w").write(
        "export function displayName(user) {\n"
        "  return user.profile.nickname || `${user.profile.firstName} ${user.profile.lastName}`;\n}\n")
    t = os.path.join(hand, "test/account.test.ts")
    s = open(t).read()
    s = s.replace('displayName({ nickname: "Kiki", firstName: "Kiyo", lastName: "Ito" })',
                  'displayName({ profile: { nickname: "Kiki", firstName: "Kiyo", lastName: "Ito" } })')
    s = s.replace('displayName({ firstName: "Kiyo", lastName: "Ito" })',
                  'displayName({ profile: { firstName: "Kiyo", lastName: "Ito" } })')
    open(t, "w").write(s)
    subprocess.run(["git", "-C", hand, "commit", "-qam",
                    "account: keep a user's names under profile"])
    subprocess.run(["git", "-C", hand, "push", "-q", "origin", "main"])
    subprocess.run(["rm", "-rf", hand])
    log("harness", "Committed on main by hand: a user's names moved under profile, with the tests.")


def account(resume=False):
    part = ACCOUNT_PART
    if resume:
        log("harness", "Resumed after the harness was interrupted: /clear, then /rn:up")
        msg, sid, _ = rn_turn("/rn:up")
    else:
        msg, sid, _ = rn_turn("/rn:on move src/account to TypeScript")
    plan_feedback_given = resume
    design_cleared = resume
    paused = False
    for _ in range(MAX_TURNS):
        w = waiting_for(msg)
        if "pull request is ready" in msg.lower() or re.search(r"── approved → finished", msg):
            log("harness", "Session finished.")
            return
        if w == "Plan sign-off" and not plan_feedback_given:
            plan_feedback_given = True
            reply = '/rn:gm a user whose last name is null is shown "Ann null"'
        elif w == "Design sign-off" and not design_cleared:
            design_cleared = True
            move_names_under_profile()
            log("harness", "/clear without answering the Design sign-off")
            msg, sid, _ = rn_turn("/rn:up")
            continue
        else:
            reply = stand_in(part, msg)
        watch = None
        if design_cleared and not paused and reply.strip().lower().startswith(("go on", "続け")):
            watch = second_task_editing
        msg, sid, killed = rn_turn(reply, sid, watch)
        if killed and not paused:
            paused = True
            msg, sid, _ = rn_turn("/rn:dn", sid)
            log("harness", "/clear")
            msg, sid, _ = rn_turn("/rn:up")
    log("harness", "Turn limit reached.")


COUPON_PART = """You are the user of a small shop backend, talking with a tool called rn in Japanese.
You started a session to make every coupon a discount, so no coupon makes an order cost more than it
would without one; you approved its plan and design earlier, and now resume it with /rn:up.
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


def coupon():
    msg, sid, _ = rn_turn("/rn:up")
    for _ in range(MAX_TURNS):
        if waiting_for(msg) == "Deliverable sign-off":
            log("harness", "Stopped at the Deliverable sign-off for the scene's check.")
            return
        msg, sid, _ = rn_turn(stand_in(COUPON_PART, msg), sid)
    log("harness", "Turn limit reached.")


coupon()
