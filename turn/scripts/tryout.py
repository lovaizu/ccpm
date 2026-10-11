"""Makes and deletes the copy the first user tries the deliverable in, and the turn's work folder.

    python3 tryout.py make <deliverable>   prints the copy's folder
    python3 tryout.py work <session id>    prints the session's work folder, empty
    python3 tryout.py drop <folder>

The copy is a fresh clone of the repository in a temporary folder, with only the deliverable added:
the state the receiver starts from.
"""
import os
import shutil
import subprocess
import sys
import tempfile

PREFIX = "turn-try-"


def top():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return os.path.realpath(r.stdout.strip()) if r.returncode == 0 else ""


def make(deliverable):
    repo = top()
    if not repo:
        return "not inside a git repository", 1
    source = os.path.join(repo, deliverable)
    if not os.path.exists(source):
        return f"deliverable {deliverable} does not exist", 1
    folder = tempfile.mkdtemp(prefix=PREFIX)
    subprocess.run(["git", "clone", "-q", repo, folder], check=True)
    target = os.path.join(folder, deliverable)
    if os.path.isdir(source):
        shutil.copytree(source, target, dirs_exist_ok=True)
    else:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(source, target)
    return folder, 0


def work_folder(session):
    """Where a turn in this session keeps its work; the hooks find it here."""
    return os.path.join(tempfile.gettempdir(), PREFIX + session)


def work(session):
    folder = work_folder(session)
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    return folder, 0


def drop(folder):
    """Deletes folder only when it is a folder this script made."""
    path = os.path.realpath(folder)
    temp = os.path.realpath(tempfile.gettempdir())
    if os.path.dirname(path) != temp or not os.path.basename(path).startswith(PREFIX):
        return f"{folder} is not a folder made by turn; nothing deleted", 1
    shutil.rmtree(path)
    return "", 0


def main(argv):
    if len(argv) == 3 and argv[1] == "work":
        text, code = work(argv[2])
    elif len(argv) == 3 and argv[1] in ("make", "drop"):
        text, code = (make if argv[1] == "make" else drop)(argv[2])
    else:
        print(__doc__.strip())
        return 2
    if text:
        print(text)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
