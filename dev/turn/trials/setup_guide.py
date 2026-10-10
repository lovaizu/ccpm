"""Trial: a calling plugin has turn write a setup guide, through the checks in dev/turn/design.md.

The app's start script is not executable and its log folder is not in git, pitfalls a maker who only
reads the code can miss; the token it needs is the user's to give; the user has an uncommitted
change of their own. The runner answers the gap as the user, then has a newcomer who knows nothing
use the committed guide once in a fresh clone. Prints what to read.
Usage: python3 setup_guide.py <new directory> | --newcomer <directory of an earlier run>
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TURN = os.path.join(HERE, "..", "..", "..", "turn")
CALLER = os.path.join(HERE, "caller")
APP = '''import os
import sys

if not os.environ.get("APP_TOKEN"):
    sys.exit("APP_TOKEN is not set")
with open(os.path.join("var", "app.log"), "a") as log:
    log.write("start\\n")
print("app started")
'''
OPS = "# 運用\n\nAPP_TOKEN は環境ごとに別の値です。開発用の値は運用担当が決めて渡します。\n"
ANSWER = "開発用の APP_TOKEN は dev-token で、手順書にそのまま書いてよい"


def sh(cwd, *args, **kw):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, **kw)


def repo(path):
    os.makedirs(os.path.join(path, "docs"))
    files = {"app.py": APP, "start.sh": '#!/bin/sh\nexec python3 app.py "$@"\n',
             ".gitignore": "var/\n.caller/\n", "README.md": "# app\n", "docs/ops.md": OPS}
    for name, text in files.items():
        with open(os.path.join(path, name), "w") as f:
            f.write(text)
    sh(path, "git", "init", "-q")
    sh(path, "git", "add", "-A")
    sh(path, "git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "app")
    with open(os.path.join(path, "README.md"), "a") as f:
        f.write("作業中のメモ\n")


def claude(cwd, prompt, *dirs):
    args = ["claude", "-p", prompt, "--model", "opus", "--permission-mode", "bypassPermissions"]
    for d in dirs:
        args += ["--plugin-dir", d]
    return sh(cwd, *args, timeout=3600).stdout


def answered(work, src, dst):
    """The record as the caller writes it after asking the user: the returned one with the answer."""
    out, part = [], None
    for line in open(os.path.join(work, src)).read().splitlines():
        if not line.startswith(" "):
            part = line
        if part in ("episodic_trace:", "predictive_cue:", "uncertainty_signal:"):
            continue
        out.append(line)
        if line == "constraints:":
            out.append(f'  - answer: "{ANSWER}"')
    with open(os.path.join(work, dst), "w") as f:
        f.write("\n".join(out) + "\n")


def newcomer(out, work):
    """A newcomer who knows nothing uses the guide once, in a fresh clone with the guide as returned."""
    fresh = os.path.join(out, "fresh")
    sh(out, "git", "clone", "-q", work, fresh)
    shutil.copy(os.path.join(work, "SETUP.md"), fresh)
    print("newcomer:", claude(fresh, "あなたは今日入った新人です。SETUP.md だけを見て、上から順に実行して"
                                     "アプリを起動してください。各手順で何をして何が表示されたか、つまずいた所はどこかを報告してください。"))
    return fresh


def slug(path):
    return "".join(c if c.isalnum() else "-" for c in os.path.realpath(path))


def main(out):
    if os.path.exists(out):
        sys.exit(f"{out} exists; give a new directory")
    work = os.path.join(out, "work")
    repo(work)
    before = set(os.listdir(tempfile.gettempdir()))
    print("caller 1:", claude(work, "/caller:guide", TURN, CALLER))
    if 'next: "ask the user"' in open(os.path.join(work, ".caller/2.yaml")).read():
        answered(work, ".caller/2.yaml", ".caller/3.yaml")
        print("caller 2:", claude(work, "/caller:guide .caller/3.yaml .caller/4.yaml", TURN, CALLER))
    print("left in the temporary folder:", sorted(set(os.listdir(tempfile.gettempdir())) - before))
    print("git status:", sh(work, "git", "status", "--short").stdout)
    print("git log:", sh(work, "git", "log", "--oneline").stdout)
    fresh = newcomer(out, work)
    for p in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))):
        if os.path.basename(os.path.dirname(p)) in (slug(work), slug(fresh)):
            print("jsonl:", p)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--newcomer"]:
        newcomer(os.path.abspath(sys.argv[2]), os.path.join(os.path.abspath(sys.argv[2]), "work"))
    else:
        main(os.path.abspath(sys.argv[1]))
