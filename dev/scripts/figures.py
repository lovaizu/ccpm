"""Keeps every figure's look in one place, dev/images/figures.css: its colors in light and dark, its
lines, and its fonts. Run it from the top of the repository as
`python3 dev/scripts/figures.py write|check`.

A page shows a figure through `<img>`, which reads no other file, so each SVG that git holds, and
each Japanese copy of one in .review/ja, carries a copy of the style in its own `<style>`. `write`
puts the copy in each figure. `check`, which dev/scripts/check.sh runs, fails on any figure whose
copy lags behind, and on any figure that sets a font or a color of its own, as the figure would
then look unlike the rest."""

from __future__ import annotations

import os
import re
import subprocess
import sys

STYLE = "dev/images/figures.css"
BLOCK = re.compile(r"(<style>\n)(.*?)(\n\s*</style>)", re.DOTALL)
COPIES = ".review/ja"
OWN = re.compile(r"\s(style|fill|stroke|color|font-[a-z]+)=")


def figures() -> list[str]:
    """Each SVG git holds, and each Japanese copy of one, which git ignores."""
    listed = subprocess.run(
        ["git", "ls-files", "*.svg"], capture_output=True, text=True, check=True
    ).stdout.split()
    for folder, _, names in os.walk(COPIES):
        listed += [os.path.join(folder, name) for name in sorted(names) if name.endswith(".svg")]
    return listed


def own_looks(path: str, svg: str) -> list[str]:
    """Each line of the figure outside its `<style>` that sets a font or a color of its own."""
    outside = BLOCK.sub(lambda m: m.group(1) + "\n" * m.group(2).count("\n") + m.group(3), svg)
    return [
        f"{path}:{number}: sets its own {found.group(1)}; give it a class of {STYLE}"
        for number, line in enumerate(outside.split("\n"), 1)
        for found in OWN.finditer(line)
    ]


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
        behind += own_looks(path, svg)
        made = styled(svg, style)
        if made == svg:
            continue
        if argv == ["write"]:
            with open(path, "w", encoding="utf-8") as f:
                f.write(made)
        else:
            behind.append(
                f"{path}: its style is not {STYLE}; run `python3 dev/scripts/figures.py write`"
            )
    for line in behind:
        print(f"figures.py: {line}", file=sys.stderr)
    return 1 if behind else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
