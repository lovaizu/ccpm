"""Tries rn's orchestrator over the whole course, from `/rn:up <what they want>` to the pull request
marked ready, as a unit test of its prompts: the real skills and scripts, in a fresh clone of
lovaizu/playground, with turn's turn:up stood in for by `up.md` and `stand.py` of this folder,
making each work from its CCS, and the user by answers set by what each reply of rn holds and what
its steering holds as the last commit keeps it, on the smallest request that reaches each move.

    python3 dev/rn/trials/flow/flow.py <new folder>

The new folder holds the copies of rn and turn as they are when the trial starts, the clone, left
there to read, and what Claude Code printed for each message, `<n>.jsonl`. Each message is a
`claude -p` call: `/rn:ty`, `/rn:gm` and each answer go on the conversation of the reply they
answer, and the `/rn:up` after the feedback is kept starts a fresh one; a run whose reply offers
nothing and keeps no move is stuck, and ends. Whether the run passes, failed or stopped, the
session's branch is deleted from the playground and its pull request closed; an issue rn would open
is kept in `issues.txt` instead, as no trial opens one where people work.

Prints each conversation's session ID, each message sent and the last lines of each reply; the
commits on the session's branch with the files each changed, the steering's stage, sign-off and Next
where it rewrote the steering, and the calls to turn it kept; each call to turn with its work, its
stage and whether turn returned it; the learnings the steering holds; whether the default branch is
as it was; the agents each conversation started; the pull request's state at the end; the minutes
and the cost."""

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
# What rn writes: the steering's value where no sign-off waits, its headings read here, and the
# folder of the calls to turn beside it, each a CCS and, once turn returned it, a result.
NONE = "none"
STEERING = "/steering.md"
NEXT = "## Next"
LEARNINGS = "## Learnings"
TURN = "turn"
CCS = "-ccs.json"
RESULT = "-result.json"
MOST = 60
# The minutes a message waits for turn's stand-in, started in the background, as turn's trials do.
WAIT = 60
# The last lines of each reply printed.
SHOWN = 12


def answer(
    reply: str, keys: "dict[str, str]", sent: str, moved: bool, ready: bool, sent_back: bool
) -> "tuple[str, bool] | None":
    """The stand-in user's next message to the reply, with whether it starts a fresh conversation,
    known by what rn kept rather than by its words, which are in the conversation language: None
    where the pull request is marked ready, which ends the run, or where the reply offers no option
    `a.` and the branch has not moved since the message before, which leaves the run stuck. `keys`
    is the front matter of the steering as the last commit holds it, none before the session
    starts: a sign-off waiting, the plan's is sent back the first time, sent_back False, and
    approved after, and any other approved; the feedback sent and kept, no sign-off waiting since,
    is gone on with in a fresh conversation. A reply offering no option `a.` is answered yes, and
    any other the recommended option."""
    lines = [line.strip(" *#>`\u25cf").lower() for line in reply.splitlines()]
    offers = any(line.startswith("a. ") for line in lines)
    if ready or not (offers or moved):
        return None
    signoff = keys.get("signoff", NONE)
    if signoff == "plan":
        return (APPROVE if sent_back else FEEDBACK), False
    if signoff != NONE:
        return APPROVE, False
    if moved and sent == FEEDBACK:
        return GO_ON, True
    return (RECOMMENDED if offers else YES), False


def front(text: str) -> "dict[str, str]":
    """The `key: value` lines of the front matter the text opens with; none where it opens with
    none."""
    lines = text.splitlines()
    if lines[:1] != ["---"]:
        return {}
    keys = {}
    for line in lines[1:]:
        if line == "---":
            break
        key, _, value = line.partition(": ")
        keys[key] = value
    return keys


def under(text: str, heading: str) -> str:
    """The lines under the `##` heading of the text, up to the next, without the blank ones around
    them; "" where it has no such heading."""
    lines = text.splitlines()
    if heading not in lines:
        return ""
    rest = lines[lines.index(heading) + 1 :]
    below = rest[: next((n for n, line in enumerate(rest) if line.startswith("## ")), len(rest))]
    return "\n".join(below).strip("\n")


def steering_of(clone: str, default: str, ref: str) -> "tuple[str, str]":
    """The path of the session's steering, as the branch at ref changed it from the default branch,
    and its text there; "" for each where the branch holds no session."""
    listed = run("git", "diff", "--name-only", f"origin/{default}...{ref}", "--", ".rn", cwd=clone)
    path = next((p for p in listed.splitlines() if p.endswith(STEERING)), "")
    return path, run("git", "show", f"{ref}:{path}", cwd=clone) if path else ""


def kept(clone: str, default: str) -> "tuple[str, dict[str, str], bool]":
    """The clone's HEAD, the front matter of the steering as it holds it, and whether the pull
    request of its branch is marked ready; none of either before the session starts."""
    head = run("git", "rev-parse", "HEAD", cwd=clone)
    keys = front(steering_of(clone, default, "HEAD")[1])
    branch = run("git", "branch", "--show-current", cwd=clone)
    ready = False
    if branch != default:
        view = run("gh", "pr", "view", branch, "--repo", PLAYGROUND, "--json", "isDraft", cwd=clone)
        ready = bool(view) and json.loads(view).get("isDraft") is False
    return head, keys, ready


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
    """The environment Claude Code runs in, with a `gh` first on PATH that keeps each issue rn would
    open in place/issues.txt, giving back an issue's URL as gh would, and runs gh for every other
    command."""
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
    plugins: "list[str]", clone: str, default: str, place: str, env: "dict[str, str]", talked: dict
) -> None:
    """The stand-in user's messages, each answering the reply before, until the pull request is
    marked ready, the run is stuck, or MOST are sent; keeps in talked each conversation's session
    ID, the cost and whether the run reached the end, as each message is answered, so a run that
    stops still reports them."""
    session = None
    message = REQUEST
    sent_back = False
    before = kept(clone, default)[0]
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
        head, keys, ready = kept(clone, default)
        given = answer(reply, keys, message, head != before, ready, sent_back)
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


def commits(clone: str, default: str, branch: str, steering: str) -> None:
    """Prints each commit on the branch since it left the default branch, oldest first, with the
    files it changed, the steering's stage, sign-off and Next where it rewrote the steering, and
    the files of the calls to turn it kept."""
    print(f"--- commits on {branch}")
    for commit in run(
        "git", "rev-list", "--reverse", f"origin/{default}..{branch}", cwd=clone
    ).split():
        body = run("git", "show", "-s", "--format=%B", commit, cwd=clone).splitlines()
        files = run("git", "show", "--name-only", "--format=", commit, cwd=clone).splitlines()
        print(commit[:8], body[0] if body else "")
        print("  files:", ", ".join(files) or "none")
        if steering in files:
            text = run("git", "show", f"{commit}:{steering}", cwd=clone)
            keys = front(text)
            print(
                f"  steering: stage {keys.get('stage')}, signoff {keys.get('signoff')}, Next:",
                " ".join(under(text, NEXT).split()),
            )
        else:
            print("  steering: as before")
        made = [os.path.basename(f) for f in files if f"/{TURN}/" in f]
        print("  calls to turn:", ", ".join(made) or "none")


def calls(clone: str, branch: str, steering: str) -> None:
    """Prints each call to turn the branch holds, in the order made, with the work its CCS names,
    the stage it was made in, and whether turn returned it, with the lessons of its result."""
    print(f"--- calls to turn on {branch}")
    place = os.path.join(os.path.dirname(steering), TURN)
    names = run("git", "ls-tree", "--name-only", branch, "--", f"{place}/", cwd=clone).split()
    for path in (p for p in names if p.endswith(CCS)):
        ccs = json.loads(run("git", "show", f"{branch}:{path}", cwd=clone) or "{}")
        named = {k: v for part in ccs.values() for e in part for k, v in e.items()}
        result = path[: -len(CCS)] + RESULT
        returned = "not returned"
        if result in names:
            lessons = json.loads(run("git", "show", f"{branch}:{result}", cwd=clone)).get("lessons")
            returned = f"returned, {len(lessons or [])} lessons"
        print(os.path.basename(path), named.get("work"), "in", named.get("stage"), returned)


def report(place: str, clone: str, default: str, before: str, talked: dict) -> None:
    """Prints what the run is judged by: the commits, the calls to turn and the learnings of each
    session's branch, the pull request's state, whether the default branch is as it was, the
    agents each conversation started, the issues kept, the minutes and the cost."""
    for branch in branches(clone, default):
        steering, text = steering_of(clone, default, branch)
        commits(clone, default, branch, steering)
        if steering:
            calls(clone, branch, steering)
            print(f"--- learnings in the steering\n{under(text, LEARNINGS) or 'none'}")
        state = run("gh", "pr", "view", branch, "--repo", PLAYGROUND, "--json", "url,state,isDraft")
        print("pull request at the end:", state or "none")
    after = run("git", "ls-remote", "origin", f"refs/heads/{default}", cwd=clone).split("\t")[0]
    print(f"{default} on the playground:", "as it was" if after == before else f"MOVED to {after}")
    for session in talked["sessions"]:
        for record in sorted(trying.agents(session)):
            with open(record.replace(".jsonl", ".meta.json"), encoding="utf-8") as f:
                print("agent:", json.load(f).get("agentType"), record)
    issues = os.path.join(place, "issues.txt")
    if os.path.exists(issues):
        with open(issues, encoding="utf-8") as f:
            print(f"--- issues rn would have opened\n{f.read()}")
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
    # rn's commits are made by rn.py's git, which needs a name on a machine with none.
    run("git", "config", "user.name", "trial", cwd=clone)
    run("git", "config", "user.email", "trial@example.invalid", cwd=clone)
    default = run("git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD", cwd=clone)
    default = default.partition("/")[2]
    before = run("git", "rev-parse", f"origin/{default}", cwd=clone)
    talked = {"sessions": [], "cost": {}, "ended": False, "start": time.time()}
    try:
        converse(plugins, clone, default, place, env, talked)
    finally:
        try:
            report(place, clone, default, before, talked)
        finally:
            clean(clone, default)
    return 0 if talked["ended"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
