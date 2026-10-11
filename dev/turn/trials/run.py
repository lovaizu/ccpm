"""Run turn from a small calling plugin as its user would, and leave what happened to be read.

    python3 dev/turn/trials/run.py play <workdir>              set up the repository and run /setup:guide
    python3 dev/turn/trials/run.py answer <workdir> <answer>   answer the question /setup:guide asked
    python3 dev/turn/trials/run.py receive <workdir>           a new team member uses SETUP.md once

Everything lands in <workdir>. Read every conversation and agent record (JSONL) of each run to judge.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TRIALS = Path(__file__).resolve().parent
REPO = TRIALS.parents[2]
PLUGINS = ["--plugin-dir", str(REPO / "turn"), "--plugin-dir", str(TRIALS / "setup-plugin")]


def claude(message, cwd, extra, name, workdir):
    cmd = ["claude", "-p", message, "--model", "opus", "--output-format", "json", *extra]
    t0 = time.time()
    out = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    try:
        result = json.loads(out.stdout)
    except ValueError:
        sys.exit(f"claude did not return JSON (exit {out.returncode}):\n{out.stderr or out.stdout}")
    result["minutes"] = round((time.time() - t0) / 60, 1)
    (workdir / f"{name}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"{name}: session {result.get('session_id')}, {result['minutes']} min\n{result.get('result')}")
    return result


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.name=trial", "-c", "user.email=trial@example.com", *args],
                   cwd=cwd, check=True, capture_output=True)


def play(workdir):
    repo = workdir / "repo"
    shutil.copytree(TRIALS / "fixture", repo)
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "tasks app")
    # The team member writing the guide has run the app before, so var/ exists only here.
    subprocess.run([sys.executable, "scripts/init_data.py"], cwd=repo, check=True, capture_output=True)
    claude("/setup:guide", repo, [*PLUGINS, "--permission-mode", "auto"], "play", workdir)


def answer(workdir, text):
    session = json.loads((workdir / "play.json").read_text())["session_id"]
    claude(text, workdir / "repo", [*PLUGINS, "--permission-mode", "auto", "--resume", session],
           "answer", workdir)


def receive(workdir):
    copy = Path(tempfile.mkdtemp(prefix="turn-receive-"))
    try:
        subprocess.run(["git", "clone", "-q", str(workdir / "repo"), str(copy / "repo")], check=True)
        shutil.copy2(workdir / "repo" / "SETUP.md", copy / "repo" / "SETUP.md")
        message = ("You joined the team today. Get the app running by following SETUP.md in this folder, "
                   "from the top, without asking anyone. Report each step you took and what it showed, "
                   "where you got stuck, and whether the app ran. When the guide sends you to a person for "
                   "something, take it that they gave you what the guide says they give; for a secret, "
                   "the value trial-token. Stay inside this folder.")
        claude(message, copy / "repo", ["--permission-mode", "auto"], "receive", workdir)
    finally:
        shutil.rmtree(copy)


def main(argv):
    if len(argv) < 3 or argv[1] not in ("play", "answer", "receive") or (argv[1] == "answer") != (len(argv) == 4):
        print(__doc__.strip())
        return 2
    workdir = Path(argv[2]).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    if argv[1] == "play":
        play(workdir)
    elif argv[1] == "answer":
        answer(workdir, argv[3])
    else:
        receive(workdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
