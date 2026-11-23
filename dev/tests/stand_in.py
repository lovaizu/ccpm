"""What the plugins' doubles share: the writer of a stand-in program, such as `claude` or `gh`,
which a case puts first on the PATH of a program that runs apart, so that the program reaches the
double in place of the real thing. Each double keeps its own answers, and calls this writer for the
program."""

from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))


def program(bin_folder: str, name: str, double: str, answer: str) -> str:
    """Writes the program `name` into the bin folder, and gives the bin folder.

    The program imports the double, the Python file at the absolute path `double`, and prints what
    `answer` gives, a call of the double's module by its name, such as
    `gh_double.answer(['gh', *sys.argv[1:]], '/tmp/state', os.getcwd())`, whose first three values
    are the exit code, stdout, and stderr, with `os` and `sys` imported for it. It then exits with
    that code.
    """
    os.makedirs(bin_folder, exist_ok=True)
    path = os.path.join(bin_folder, name)
    module = os.path.splitext(os.path.basename(double))[0]
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "import sys\n"
            # The double imports this file's module too, so both folders go on the path.
            f"sys.path[:0] = [{os.path.dirname(double)!r}, {HERE!r}]\n"
            f"import {module}\n"
            f"code, out, err = ({answer})[:3]\n"
            "sys.stdout.write(out)\n"
            "sys.stderr.write(err)\n"
            "sys.exit(code)\n"
        )
    os.chmod(path, 0o755)
    return bin_folder
