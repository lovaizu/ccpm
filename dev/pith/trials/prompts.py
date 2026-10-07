#!/usr/bin/env python3
"""Check a plugin's prompts with pith, each by the essentials for a prompt (or for an essentials
file), as `.claude/rules/plugin.md` asks of every plugin. Each plugin lists its prompts, their
receivers and aims in `dev/<plugin>/trials/prompts.json`. Runs in a copy of the repository, so the
working tree is left alone, and leaves each short result in `<workdir>/<name>.md`.

    python3 dev/pith/trials/prompts.py <plugin> <workdir> [<name>...]
"""
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SETTINGS = json.dumps({"enabledPlugins": {"rn@ccpm": False, "writ@ccpm": False, "pith@ccpm": False}})
AT_ONCE = 3


def check(copy, plugin, item, workdir):
    essentials = "essentials.md" if item.get("essentials") else "prompt.md"
    request = (f"/pith:up Check {item['path']} with pith's {essentials}. "
               f"Its receiver and purpose: {item['receiver']} "
               f"To run it as its receiver would, load the plugins with "
               f"`claude -p --plugin-dir rn --plugin-dir writ --plugin-dir pith` from this "
               f"repository's root, since each depends on the next. It runs on Opus and Sonnet. "
               f"The aim: {item['aim']} Write the result file to .pith/open/ as {item['name']}.")
    out = subprocess.run(["claude", "-p", request, "--model", "opus", "--output-format", "json",
                          "--plugin-dir", os.path.join(copy, "pith"), "--permission-mode", "auto",
                          "--settings", SETTINGS],
                         cwd=copy, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    try:
        result = json.loads(out.stdout).get("result", "")
    except ValueError:
        result = out.stdout[-3000:] + out.stderr[-1000:]
    with open(os.path.join(workdir, item["name"] + ".md"), "w") as f:
        f.write(f"# {item['path']}\n\n{result}\n")
    return item["name"]


def main():
    plugin, workdir = sys.argv[1], os.path.abspath(sys.argv[2])
    names = set(sys.argv[3:])
    with open(os.path.join(ROOT, "dev", plugin, "trials", "prompts.json")) as f:
        items = [i for i in json.load(f) if not names or i["name"] in names]
    os.makedirs(workdir, exist_ok=True)
    copies = []
    for n in range(min(AT_ONCE, len(items))):
        copy = os.path.join(workdir, f"copy{n}")
        if not os.path.exists(copy):
            subprocess.run(["git", "clone", "-q", ROOT, copy], check=True)
            for d in ("rn", "writ", "pith", ".claude"):
                shutil.rmtree(os.path.join(copy, d), ignore_errors=True)
                shutil.copytree(os.path.join(ROOT, d), os.path.join(copy, d))
        copies.append(copy)
    with ThreadPoolExecutor(AT_ONCE) as pool:
        jobs = [pool.submit(check, copies[k % len(copies)], plugin, item, workdir)
                for k, item in enumerate(items)]
        for job in jobs:
            print(job.result(), flush=True)


if __name__ == "__main__":
    main()
