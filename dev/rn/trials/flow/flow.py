"""Tries rn's conductor over the whole course, from `/rn:up <what they want>` to the pull request
marked ready, as `dev/rn/architecture.md` Verification gives it: the real skills, scripts, learner
and its lanes, in a fresh clone of lovaizu/playground, with turn's turn:up stood in for by `up.md`
and `stand.py` of this folder, and the user by answers set by what each reply of rn holds, on the
smallest request that reaches each move.

    python3 dev/rn/trials/flow/flow.py <new folder>

The new folder holds the copies of rn and turn as they are when the trial starts, the clone, left
there to read, and what Claude Code printed for each message, `<n>.jsonl`. Each message is a
`claude -p` call: `/rn:ty` and `/rn:gm` go on the conversation of the reply they answer, and the
`/rn:up` after the feedback is kept starts a fresh one; a run whose reply offers nothing and keeps
no move is stuck, and ends. Whether the run passes, failed or stopped, the session's branch is
deleted from the playground and its pull request closed; an issue the conductor would open is kept
in `issues.txt` instead, as no trial opens one where people work.

Prints each conversation's session ID, each message sent and the last lines of each reply; the
commits on the session's branch with the files each changed, its trailers and whether it replaced
`state.json`; whether the default branch is as it was; the learner's records, its stops among them,
and the `learnt/` files; the pull request's state at the end; the minutes and the cost."""

import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, "dev", "lane"))

import trying

USAGE = "usage: python3 dev/rn/trials/flow/flow.py <new folder>"
PLAYGROUND = "lovaizu/playground"
# The stand-in user's messages, by what the reply they answer holds.
REQUEST = "/rn:up add a line greeting new contributors to the README"
FEEDBACK = "/rn:gm the greeting should name the CONTRIBUTING file too"
APPROVE = "/rn:ty"
GO_ON = "/rn:up"
RECOMMENDED = "a"
# The stand-in user's yes to a question with no options, such as whether to open an issue shown.
YES = "yes"
MOST = 60
# The minutes a message waits for turn's stand-in, started in the background, as turn's trials do.
WAIT = 60
# The last lines of each reply printed.
SHOWN = 12


def answer(
    reply: str, last: str, moved: bool, ready: bool, sent_back: bool
) -> "tuple[str, bool] | None":
    """The stand-in user's next message to the reply, with whether it starts a fresh conversation,
    known by what the conductor kept rather than by its words, which are in the conversation
    language: None where the pull request is marked ready, which ends the run, or where the reply
    offers no option `a.` and the branch has not moved since the message before, which leaves the
    run stuck. `last` holds the messages of the commits the reply's move kept, the learner's lessons
    kept after them among them: a sign-off's proposal holds its `Rn-Sign-off:` trailer, the plan's sent back the first time, sent_back False, and approved
    after; kept feedback its `Rn-Answer: feedback` trailer, gone on with in a fresh conversation. A
    reply offering no option `a.` is answered yes, and any other the recommended option."""
    lines = [line.strip(" *#>`\u25cf").lower() for line in reply.splitlines()]
    offers = any(line.startswith("a. ") for line in lines)
    if ready or not (offers or moved):
        return None
    trailers = [line for line in last.splitlines() if line.startswith("Rn-")]
    if moved and "Rn-Sign-off: plan" in trailers:
        return (APPROVE if sent_back else FEEDBACK), False
    if moved and any(t.startswith("Rn-Sign-off:") for t in trailers):
        return APPROVE, False
    if moved and any(t.startswith("Rn-Answer: feedback") for t in trailers):
        return GO_ON, True
    return (RECOMMENDED if offers else YES), False


def kept(clone: str, before: str = "") -> "tuple[str, str, bool]":
    """The clone's HEAD, the messages of the commits since before, and whether the pull request of
    its branch is marked ready, none before the session starts."""
    head = run("git", "rev-parse", "HEAD", cwd=clone)
    last = run("git", "log", "--format=%B", f"{before}..HEAD", cwd=clone) if before else ""
    branch = run("git", "branch", "--show-current", cwd=clone)
    view = run("gh", "pr", "view", branch, "--repo", PLAYGROUND, "--json", "isDraft", cwd=clone)
    ready = bool(view) and json.loads(view).get("isDraft") is False
    return head, last, ready


def run(*args: str, cwd: "str | None" = None) -> str:
    """What the command printed, or "" where it failed, its error printed, so a step of the report
    or the cleanup that fails leaves the others to run."""
    done = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=False)
    if done.returncode:
        print(f"{' '.join(args[:3])} ... failed: {done.stderr.strip()}")
    return done.stdout.strip()


def copies(place: str) -> "list[str]":
    """Copies of turn and rn in place, as installing makes them, each link the file it points to,
    with turn's turn:up replaced by the stand-in and its lanes, which hold the real one's steps,
    left out; gives their folders."""
    plugins = []
    for name in ("turn", "rn"):
        plugins.append(os.path.join(place, name))
        ignored = shutil.ignore_patterns("__pycache__")
        shutil.copytree(os.path.join(ROOT, name), plugins[-1], ignore=ignored)
    turn = plugins[0]
    shutil.copyfile(os.path.join(HERE, "up.md"), os.path.join(turn, "agents", "up.md"))
    shutil.copyfile(os.path.join(HERE, "stand.py"), os.path.join(turn, "scripts", "stand.py"))
    path = os.path.join(turn, "hooks", "hooks.json")
    with open(path, encoding="utf-8") as f:
        hooks = json.load(f)
    hooks["hooks"] = {
        event: [e for e in lanes if not any(" turn:up " in h["command"] for h in e["hooks"])]
        for event, lanes in hooks["hooks"].items()
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(hooks, f, indent=2)
    return plugins


def kept_issues(place: str) -> "dict[str, str]":
    """The environment Claude Code runs in, with a `gh` first on PATH that keeps each issue the
    conductor would open in place/issues.txt, giving back an issue's URL as gh would, and runs gh
    for every other command."""
    folder = os.path.join(place, "bin")
    os.makedirs(folder)
    shim = os.path.join(folder, "gh")
    real = shutil.which("gh") or "gh"
    with open(shim, "w", encoding="utf-8") as f:
        f.write(
            "#!/bin/sh\n"
            'if [ "$1" = issue ] && [ "$2" = create ]; then\n'
            f"  printf '%s\\n' \"$*\" >> '{os.path.join(place, 'issues.txt')}'\n"
            "  echo https://github.com/lovaizu/ccpm/issues/0\n"
            "  exit 0\n"
            "fi\n"
            f"exec '{real}' \"$@\"\n"
        )
    os.chmod(shim, 0o755)
    return {"PATH": f"{folder}{os.pathsep}{os.environ['PATH']}"}


def converse(
    plugins: "list[str]", clone: str, place: str, env: "dict[str, str]", talked: dict
) -> None:
    """The stand-in user's messages, each answering the reply before, until a reply says the pull
    request is marked ready, the run is stuck, or MOST are sent; keeps in talked each conversation's session ID, the
    cost and whether the run reached the end, as each message is answered, so a run that stops
    still reports them."""
    session = None
    message = REQUEST
    sent_back = False
    before = kept(clone)[0]
    for n in range(1, MOST + 1):
        print(f"--- message {n}, {'on ' + session if session else 'a fresh conversation'}")
        print("sent:", message)
        end = trying.claude(
            message,
            plugins,
            cwd=clone,
            wait=WAIT,
            record=os.path.join(place, f"{n}.jsonl"),
            env=env,
            resume=session,
        )
        session = end["session_id"]
        if session not in talked["sessions"]:
            talked["sessions"].append(session)
        # A conversation gone on with gives the cost of the whole conversation so far.
        talked["cost"][session] = end.get("total_cost_usd") or 0
        reply = end.get("result") or ""
        print("session:", session)
        print("reply ends:\n" + "\n".join(reply.splitlines()[-SHOWN:]))
        head, last, ready = kept(clone, before)
        given = answer(reply, last, head != before, ready, sent_back)
        before = head
        if given is None:
            talked["ended"] = ready
            print(
                "the pull request is ready" if ready else "stuck: no option offered, no move kept"
            )
            return
        message, fresh = given
        sent_back = sent_back or message == FEEDBACK
        session = None if fresh else session
    print(f"stopped: {MOST} messages sent, and no reply said the pull request is ready to merge")


def branches(clone: str, default: str) -> "list[str]":
    """Each branch of the clone but the default one: the session's, as rn.py start made it."""
    listed = run("git", "for-each-ref", "--format=%(refname:short)", "refs/heads", cwd=clone)
    return [b for b in listed.splitlines() if b != default]


def commits(clone: str, default: str, branch: str) -> None:
    """Prints each commit on the branch since it left the default branch, oldest first, with the
    files it changed, its trailers, and whether it replaced `state.json`, a proposal's apart; then
    each `learnt/` file of the session as the branch holds it."""
    print(f"--- commits on {branch}")
    learnt = []
    for commit in run(
        "git", "rev-list", "--reverse", f"origin/{default}..{branch}", cwd=clone
    ).split():
        body = run("git", "show", "-s", "--format=%B", commit, cwd=clone).splitlines()
        files = run("git", "show", "--name-only", "--format=", commit, cwd=clone).splitlines()
        trailers = [line for line in body if line.startswith("Rn-")]
        proposal = any(t.startswith("Rn-Sign-off:") for t in trailers)
        state = any(f.endswith("/state.json") for f in files)
        print(commit[:8], body[0] if body else "")
        print("  files:", ", ".join(files) or "none")
        print("  trailers:", ", ".join(trailers) or "none")
        print(
            "  state.json:", "a proposal" if proposal else ("replaced" if state else "NOT replaced")
        )
        learnt += [f for f in files if "/learnt/" in f and f not in learnt]
    for path in learnt:
        print(f"--- {path}\n{run('git', 'show', f'{branch}:{path}', cwd=clone)}")


def report(place: str, clone: str, default: str, before: str, talked: dict) -> None:
    """Prints what the run is judged by: the commits and lessons of each session's branch, whether
    the default branch is as it was, the learner's records, the pull request's state, the issues
    kept, the minutes and the cost."""
    for branch in branches(clone, default):
        commits(clone, default, branch)
        state = run("gh", "pr", "view", branch, "--repo", PLAYGROUND, "--json", "url,state,isDraft")
        print("pull request at the end:", state or "none")
    after = run("git", "ls-remote", "origin", f"refs/heads/{default}", cwd=clone).split("\t")[0]
    print(f"{default} on the playground:", "as it was" if after == before else f"MOVED to {after}")
    for session in talked["sessions"]:
        for record in sorted(trying.agents(session)):
            with open(record.replace(".jsonl", ".meta.json"), encoding="utf-8") as f:
                agent = json.load(f).get("agentType")
            if agent == "rn:learner":
                trying.show(record)
            else:
                print("agent:", agent, record)
    issues = os.path.join(place, "issues.txt")
    if os.path.exists(issues):
        with open(issues, encoding="utf-8") as f:
            print(f"--- issues the conductor would have opened\n{f.read()}")
    print("sessions:", ", ".join(talked["sessions"]))
    print(
        "minutes:",
        round((time.time() - talked["start"]) / 60, 1),
        "cost:",
        round(sum(talked["cost"].values()), 2),
    )
    print("reached ready to merge:", talked["ended"])


def clean(clone: str, default: str) -> None:
    """Closes each open pull request of each session's branch on the playground and deletes the
    branch there; each step that fails is printed, and the rest still run."""
    for branch in branches(clone, default):
        listed = run("gh", "pr", "list", "--repo", PLAYGROUND, "--head", branch, "--json", "number")
        for pr in json.loads(listed or "[]"):
            run("gh", "pr", "close", str(pr["number"]), "--repo", PLAYGROUND)
            print(f"closed pull request #{pr['number']}")
        if run("git", "ls-remote", "--heads", "origin", branch, cwd=clone):
            run("git", "push", "-q", "origin", "--delete", branch, cwd=clone)
            print(f"deleted {branch} on the playground")


def main(argv: "list[str]") -> int:
    """Runs the trial in the new folder argv names; prints the usage and gives 1 on any other
    arguments, or where the folder is there already."""
    if argv in (["-h"], ["--help"]):
        print(f"{__doc__}\n\n{USAGE}")
        return 0
    if len(argv) != 1 or os.path.exists(argv[0]):
        print(f"{USAGE}\nthe folder must be new")
        return 1
    place = os.path.abspath(argv[0])
    os.makedirs(place)
    plugins = copies(place)
    env = kept_issues(place)
    clone = os.path.join(place, "playground")
    subprocess.run(["gh", "repo", "clone", PLAYGROUND, clone, "--", "-q"], check=True)
    # The conductor's commits are made by rn.py's git, which needs a name on a machine with none.
    run("git", "config", "user.name", "trial", cwd=clone)
    run("git", "config", "user.email", "trial@example.invalid", cwd=clone)
    default = run("git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD", cwd=clone)
    default = default.partition("/")[2]
    before = run("git", "rev-parse", f"origin/{default}", cwd=clone)
    talked = {"sessions": [], "cost": {}, "ended": False, "start": time.time()}
    try:
        converse(plugins, clone, place, env, talked)
    finally:
        try:
            report(place, clone, default, before, talked)
        finally:
            clean(clone, default)
    return 0 if talked["ended"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
