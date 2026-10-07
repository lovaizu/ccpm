#!/usr/bin/env python3
"""Ask for a plugin's job in the user's own words, without naming a command, and report which skills
started, so a description that the user's words do not reach shows.

    python3 dev/writ/trials/chosen.py <workdir> "<what the user asks>"
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from run import PITH, SETTINGS, TRIALS, WRIT, git


def main():
    workdir, words = Path(sys.argv[1]).resolve(), sys.argv[2]
    if workdir.exists():
        sys.exit(f"{workdir} exists; give a new workdir")
    repo = workdir / "repo"
    shutil.copytree(TRIALS / "fixture", repo)
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Initial commit")
    cmd = ["claude", "-p", words, "--model", "opus", "--output-format", "stream-json", "--verbose",
           "--max-turns", "6", "--plugin-dir", str(WRIT), "--plugin-dir", str(PITH),
           "--permission-mode", "auto", "--settings", SETTINGS]
    out = subprocess.run(cmd, cwd=repo, stdin=subprocess.DEVNULL, capture_output=True, text=True).stdout
    started = []
    for line in out.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        for part in (event.get("message") or {}).get("content") or []:
            if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == "Skill":
                started.append(part["input"].get("skill"))
    report = f"# Asked in the user's words\n\n{words}\n\nSkills started: {started or 'none'}\n"
    (workdir / "chosen.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
