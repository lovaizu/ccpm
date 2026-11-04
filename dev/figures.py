"""Every figure's style kept once, in dev/images/figures.css, run as `python3 dev/figures.py
write|check` from the top of the repository. A figure is shown by `<img>`, which reads no file
beside it, so each SVG git holds carries a copy of the style in its own `<style>`: `write` puts the
copy in each, and `check`, run by dev/check.sh, fails on any figure whose copy is left behind."""

from __future__ import annotations

import re
import subprocess
import sys

STYLE = "dev/images/figures.css"
BLOCK = re.compile(r"(<style>\n)(.*?)(\n\s*</style>)", re.DOTALL)


def figures() -> list[str]:
    """Each SVG git holds."""
    listed = subprocess.run(
        ["git", "ls-files", "*.svg"], capture_output=True, text=True, check=True
    ).stdout
    return listed.split()


def styled(svg: str, style: str) -> str:
    """The figure with the style as its own, indented under its `<style>`."""
    indented = "\n".join("    " + line if line else line for line in style.rstrip("\n").split("\n"))
    return BLOCK.sub(lambda m: m.group(1) + indented + m.group(3), svg, count=1)


def main(argv: list[str]) -> int:
    if argv not in (["write"], ["check"]):
        print("usage: figures.py write|check", file=sys.stderr)
        return 2
    with open(STYLE, encoding="utf-8") as f:
        style = f.read()
    behind = []
    for path in figures():
        with open(path, encoding="utf-8") as f:
            svg = f.read()
        if not BLOCK.search(svg):
            behind.append(f"{path}: no <style> to hold {STYLE}")
            continue
        made = styled(svg, style)
        if made == svg:
            continue
        if argv == ["write"]:
            with open(path, "w", encoding="utf-8") as f:
                f.write(made)
        else:
            behind.append(f"{path}: its style is not {STYLE}; run `python3 dev/figures.py write`")
    for line in behind:
        print(f"figures.py: {line}", file=sys.stderr)
    return 1 if behind else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
