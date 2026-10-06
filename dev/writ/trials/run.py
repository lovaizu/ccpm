"""Run writ in a scene as its user would, and leave what happened for the conductor to read.

    python3 dev/writ/trials/run.py play <scene> <workdir>     set the scene up and run writ once
    python3 dev/writ/trials/run.py judge <scene> <workdir>    the user decides from writ's report, then the document
    python3 dev/writ/trials/run.py read <scene> <workdir>     a reader reads the finished document once
    python3 dev/writ/trials/run.py compare <scene> <workdir>  a reader compares it with the version before

Everything lands in <workdir>/<scene>/. A run takes many minutes.
"""
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

from scenes import SCENES

TRIALS = Path(__file__).resolve().parent
REPO = TRIALS.parents[2]
WRIT = REPO / "writ"
PITH = REPO / "pith"
# Installed copies would answer in place of the plugins under test.
SETTINGS = '{"enabledPlugins":{"writ@ccpm":false,"rn@ccpm":false,"pith@ccpm":false}}'
ROLES = TRIALS / "roles"


def claude(message, cwd, extra):
    cmd = ["claude", "-p", message, "--model", "opus", "--output-format", "json", *extra]
    t0 = time.time()
    out = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    minutes = (time.time() - t0) / 60
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        sys.exit(f"claude did not return JSON (exit {out.returncode}):\n{out.stderr or out.stdout}")
    claude.session = data.get("session_id")
    return data.get("result", ""), minutes


MAX_TURNS = 8
STAND_IN = """You are the user who asked a writing tool for a document with these words:

{opening}

You know only what those words say. Reply to what the tool just said as that user would, in the
language it wrote in: answer what it asks from what you know, say you do not know what you do not,
and agree to a proposal or plan that fits what you said. Output only your reply.

The tool just said:

{said}"""


def done(repo):
    """The tool has finished once a check has left its result file."""
    return any(path.read_text(errors="replace").startswith("# Check:")
               for path in repo.glob(".*/open/*-report-*.md"))


def writ_talk(opening, repo):
    """Run writ as its user would: the stand-in answers until a result file is left, or turns run out.
    Returns what writ said last, the minutes it took, and the user's turns."""
    said, minutes = writ(opening, repo)
    talk = [("you", opening), ("writ", said)]
    while not done(repo) and len(talk) < 2 * MAX_TURNS:
        sid = claude.session
        reply, _ = claude(STAND_IN.format(opening=opening, said=said), repo.parent, [])
        talk.append(("you", reply))
        more, m = claude(reply, repo, writ_args() + ["--resume", sid])
        said, minutes = more, minutes + m
        talk.append(("writ", said))
    return said, minutes, talk


def writ_args():
    return ["--plugin-dir", str(WRIT), "--plugin-dir", str(PITH), "--permission-mode", "auto",
            "--settings", SETTINGS]


def writ(message, repo):
    # A check asked of pith runs with pith alone, as a user who never installed writ has it.
    dirs = [] if message.startswith("/pith:") else ["--plugin-dir", str(WRIT)]
    return claude(message, repo, [*dirs, "--plugin-dir", str(PITH), "--permission-mode", "auto",
                                  "--settings", SETTINGS])


def reader(message, cwd):
    return claude(message, cwd, ["--tools", "Read,Grep,Glob"])


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def setup(name, scene_dir):
    repo = scene_dir / "repo"
    if scene_dir.exists():
        sys.exit(f"{scene_dir} exists; give a new workdir")
    if SCENES[name]["source"] == "fixture":
        shutil.copytree(TRIALS / "fixture", repo)
    else:
        repo.mkdir(parents=True)
        archive = subprocess.run(["git", "archive", "HEAD"], cwd=REPO, check=True, capture_output=True)
        subprocess.run(["tar", "-x"], cwd=repo, input=archive.stdout, check=True)
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Initial commit")
    return repo


def play(name, scene_dir):
    scene = SCENES[name]
    repo = setup(name, scene_dir)
    if scene["opening"].startswith("/pith:"):
        reply, minutes = writ(scene["opening"], repo)
        talk = []
    else:
        reply, minutes, talk = writ_talk(scene["opening"], repo)
    (scene_dir / "report.md").write_text(reply)
    (scene_dir / "talk.md").write_text("".join(f"## {who}\n\n{text}\n\n" for who, text in talk))
    (scene_dir / "play.md").write_text(
        f"# {name}\n\nBenefits: {', '.join(scene['benefits'])}\nLook at: {scene['look']}\n\n"
        f"## Request\n\n{scene['opening']}\n\n## writ ({minutes:.1f} min, {len(talk) // 2} user turns)\n\n{reply}\n\n"
        "## The scene at the end\n\n```\n" + git(repo, "status", "--short")
        + git(repo, "log", "--oneline") + "```\n\n" + changed_only_target(name, repo))
    print(scene_dir / "play.md")


def changed_only_target(name, repo):
    """Only the target work and the result files in open/ may differ from the scene as set up."""
    first = git(repo, "rev-list", "--max-parents=0", "HEAD").strip()
    changed = set((git(repo, "diff", "--name-only", first) + git(repo, "ls-files", "--others", "--exclude-standard")).split())
    others = sorted(p for p in changed if not p.startswith((".writ/open/", ".pith/")))
    target = SCENES[name]["target"]
    passed = others == [target] or others == [] if target else len(others) <= 1
    return f"Changed besides `.writ/open/`: {others or 'nothing'} — {'as expected' if passed else 'MORE THAN THE TARGET WORK'}\n"


def judge(name, scene_dir):
    repo = scene_dir / "repo"
    prompt = (ROLES / "judge.md").read_text().format(
        reader=SCENES[name]["reader"], doc=target(name, repo), report=(scene_dir / "report.md").read_text())
    answer, _ = reader(prompt, repo)
    (scene_dir / "judge.md").write_text(f"# {name}: judged from the report\n\n{answer}\n")
    print(scene_dir / "judge.md")


def target(name, repo):
    path = SCENES[name]["target"]
    if path:
        return path
    first = git(repo, "rev-list", "--max-parents=0", "HEAD").strip()
    added = git(repo, "diff", "--name-only", "--diff-filter=A", first) + git(repo, "ls-files", "--others", "--exclude-standard")
    docs = [p for p in set(added.split()) if p.endswith(".md") and not p.startswith(".writ/")]
    if len(docs) != 1:
        sys.exit(f"cannot tell the document writ wrote: {docs}")
    return docs[0]


def read(name, scene_dir):
    repo, out = scene_dir / "repo", scene_dir / "read"
    doc = target(name, repo)
    out.mkdir()
    shutil.copy(repo / doc, out / Path(doc).name)
    prompt = (ROLES / "reader.md").read_text().format(reader=SCENES[name]["reader"], doc=Path(doc).name)
    report, _ = reader(prompt, out)
    (scene_dir / "read.md").write_text(f"# {name}: {doc}, read once\n\n{report}\n")
    print(scene_dir / "read.md")


def compare(name, scene_dir):
    repo, out = scene_dir / "repo", scene_dir / "compare"
    doc = target(name, repo)
    first = git(repo, "rev-list", "--max-parents=0", "HEAD").strip()
    versions = {"before": git(repo, "show", f"{first}:{doc}"), "after": (repo / doc).read_text()}
    order = random.sample(["before", "after"], 2)
    out.mkdir()
    for label, version in zip("XY", order):
        (out / f"{label}.md").write_text(versions[version])
    prompt = (ROLES / "compare.md").read_text().format(reader=SCENES[name]["reader"])
    report, _ = reader(prompt, out)
    (scene_dir / "compare.md").write_text(
        f"# {name}: {doc}, before and after\n\nX is {order[0]}, Y is {order[1]}.\n\n{report}\n")
    print(scene_dir / "compare.md")


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("play", "judge", "read", "compare") or sys.argv[2] not in SCENES:
        sys.exit(__doc__ + "\nScenes: " + ", ".join(SCENES))
    command, name, workdir = sys.argv[1:]
    {"play": play, "judge": judge, "read": read, "compare": compare}[command](name, Path(workdir).resolve() / name)
