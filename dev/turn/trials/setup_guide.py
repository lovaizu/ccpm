"""Trial: a calling plugin has turn write a setup guide for an app whose start script is not
executable and whose log folder is not in git, pitfalls a maker who only reads the code can miss.

Runs the caller through `claude -p` in a new repository, then has a newcomer who knows nothing use
the guide once in a fresh copy. Prints the JSONL paths to read.
Usage: python3 setup_guide.py <new directory>
"""
import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TURN = os.path.join(HERE, "..", "..", "..", "turn")
CALLER = os.path.join(HERE, "caller")
APP = '''import os

with open(os.path.join("var", "app.log"), "a") as log:
    log.write("start\\n")
print("app started")
'''


def sh(cwd, *args, **kw):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, **kw)


def repo(path):
    os.makedirs(path)
    for name, text in {"app.py": APP, "start.sh": '#!/bin/sh\nexec python3 app.py "$@"\n',
                       ".gitignore": "var/\n.caller/\n", "README.md": "# app\n"}.items():
        with open(os.path.join(path, name), "w") as f:
            f.write(text)
    sh(path, "git", "init", "-q")
    sh(path, "git", "add", "-A")
    sh(path, "git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "app")


def claude(cwd, prompt, *dirs):
    args = ["claude", "-p", prompt, "--model", "opus", "--permission-mode", "bypassPermissions"]
    for d in dirs:
        args += ["--plugin-dir", d]
    return sh(cwd, *args, timeout=3600).stdout


def jsonl(cwd):
    slug = "".join(c if c.isalnum() else "-" for c in os.path.realpath(cwd))
    return sorted(glob.glob(os.path.expanduser(f"~/.claude/projects/{slug}/*.jsonl")))


def main(out):
    if os.path.exists(out):
        sys.exit(f"{out} exists; give a new directory")
    work = os.path.join(out, "work")
    repo(work)
    print("caller:", claude(work, "/caller:guide", TURN, CALLER))
    fresh = os.path.join(out, "fresh")
    sh(out, "git", "clone", "-q", work, fresh)
    shutil.copy(os.path.join(work, "SETUP.md"), fresh)
    print("newcomer:", claude(fresh, "あなたは今日入った新人です。SETUP.md だけを見て、上から順に実行して"
                                     "アプリを起動してください。各手順で何をして何が表示されたか、つまずいた所はどこかを報告してください。"))
    for p in jsonl(work) + jsonl(fresh):
        print("jsonl:", p)


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]))
