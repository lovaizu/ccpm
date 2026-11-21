"""Checks that each plugin of plugins/ works from its own folder. Run it from the top of the
repository as `python3 dev/scripts/standalone.py check`.

Claude Code copies only a plugin's folder when it installs the plugin, so a link, a path, or a file
link that leads out of the folder finds nothing there, as dev/plugin-development-guide.md says of a
folder that holds all the plugin needs. Only a symbolic link into a plugin that it depends on comes
with the install. A plugin may use another plugin only where its plugin.json names that plugin in
`dependencies`, and two plugins never depend on each other, as neither could then change or install
alone. Each plugin carries the repository's
LICENSE, so a person given the folder alone has its license."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

from practices import FENCE, KEPT, LINK, texts

PLUGINS = "plugins"
# A path to a plugin's folder, as a link or a URL names it.
OTHER = re.compile(r"(?:^|/)plugins/([a-z0-9-]+)/")


def held(folder: str) -> list[str]:
    """Each file git holds under the folder."""
    listed = subprocess.run(
        ["git", "ls-files", folder], capture_output=True, text=True, check=True
    ).stdout
    return listed.split()


def outside(plugin: str, start: str, target: str) -> str | None:
    """The target's path from the top, where a relative target from the start leads out of the
    plugin's folder."""
    reached = os.path.normpath(os.path.join(os.path.dirname(start), target.split("#")[0]))
    return reached if not (reached + "/").startswith(plugin + "/") else None


def dependencies(plugin: str) -> list[str]:
    """The names of the plugins the plugin's plugin.json names in `dependencies`."""
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        named = json.load(f).get("dependencies", [])
    return [(each["name"] if isinstance(each, dict) else each).split("@")[0] for each in named]


def faults_of(plugin: str, uses: list[str]) -> list[str]:
    """Each place in the plugin's folder that needs a file outside it or a plugin it doesn't
    depend on, and each fault of its LICENSE."""
    found = []
    for path in held(plugin):
        if os.path.islink(path):
            found += link_faults(plugin, path, uses)
            continue
        if path.endswith(".json"):
            found += json_faults(plugin, path)
        if path.endswith((".md", ".json")):
            found += text_faults(plugin, path, uses)
    return found + license_faults(plugin)


def link_faults(plugin: str, path: str, uses: list[str]) -> list[str]:
    """The fault of a symbolic link that leads out of the plugin, unless into a plugin it depends
    on, which comes with the install, as Code kept once of dev/plugin-development-guide.md says."""
    gone = outside(plugin, path, os.readlink(path))
    into = OTHER.match(gone + "/") if gone else None
    if gone and not (into and into.group(1) in uses):
        return [f"{path}: links to {gone}, outside the plugin"]
    return []


def json_faults(plugin: str, path: str) -> list[str]:
    """Each string of the JSON file that names a relative path out of the plugin."""
    with open(path, encoding="utf-8") as f:
        named = [value for value in texts(json.load(f)) if value.startswith(".")]
    gone = [outside(plugin, path, value) for value in named]
    return [f"{path}: names {each}, outside the plugin" for each in gone if each]


def text_faults(plugin: str, path: str, uses: list[str]) -> list[str]:
    """Each line of the file, outside its code blocks, that links out of the plugin, where the file
    is Markdown, or names a plugin that it doesn't depend on."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # The code blocks, at the odd places, link nothing.
    bare = "".join(
        p if n % 2 == 0 else "\n" * p.count("\n") for n, p in enumerate(FENCE.split(text))
    )
    found = []
    for number, line in enumerate(bare.split("\n"), 1):
        if path.endswith(".md"):
            targets = [link.group(3) for link in LINK.finditer(line)]
            gone = [outside(plugin, path, t) for t in targets if not KEPT.match(t)]
            found += [
                f"{path}:{number}: links to {each}, outside the plugin" for each in gone if each
            ]
        for other in OTHER.findall(line):
            if other != os.path.basename(plugin) and other not in uses:
                found.append(
                    f"{path}:{number}: uses {other}, which {plugin}/.claude-plugin/plugin.json"
                    " doesn't name in dependencies"
                )
    return found


def license_faults(plugin: str) -> list[str]:
    """The fault of the plugin's LICENSE, where it's missing or differs from the repository's."""
    licensed = os.path.join(plugin, "LICENSE")
    if not os.path.isfile(licensed):
        return [f"{licensed}: missing; copy the repository's LICENSE there"]
    with open("LICENSE", "rb") as top, open(licensed, "rb") as own:
        if top.read() != own.read():
            return [f"{licensed}: differs from the repository's LICENSE"]
    return []


def main(argv: list[str]) -> int:
    if argv != ["check"]:
        print("usage: standalone.py check", file=sys.stderr)
        return 2
    plugins = sorted(
        os.path.join(PLUGINS, name)
        for name in os.listdir(PLUGINS)
        if os.path.isfile(os.path.join(PLUGINS, name, ".claude-plugin", "plugin.json"))
    )
    uses = {os.path.basename(p): dependencies(p) for p in plugins}
    found = []
    for name, used in sorted(uses.items()):
        for other in used:
            if name < other and name in uses.get(other, []):
                found.append(f"{name} and {other} depend on each other; keep one direction")
    for plugin in plugins:
        found += faults_of(plugin, uses[os.path.basename(plugin)])
    for line in found:
        print(f"standalone.py: {line}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
