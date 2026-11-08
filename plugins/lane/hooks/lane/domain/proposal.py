"""Decides whether `lay.py` can lay a proposal: held to the proposal's JSON Schema, each lane able
to stand, and each lane checked against the files of the plugin it's for.

A proposal lies at `.lane/<yyyymmdd>-<plugin>/<plugin>.json` at the root of the repository the
plugin is in, and names the plugin's folder from that root.
"""

from __future__ import annotations

import json
import os
from typing import NamedTuple

import command
import laid
import plugin
import schema
import step


class Refused(ValueError):
    """A proposal that `lay.py` can't lay, with each fault found."""

    def __init__(self, faults: list[str]) -> None:
        super().__init__("; ".join(faults))
        self.faults = faults


class Checked(NamedTuple):
    """A proposal that `lay.py` can lay."""

    # The proposal's absolute path.
    path: str
    # The plugin's folder.
    root: str
    # The plugin's manifest.
    manifest: plugin.Manifest
    # The lanes and routes that the proposal gives.
    laid: laid.Laid
    # The part of each role with lanes, by its name.
    parts: dict[str, step.Part]


def checked(path: str) -> Checked:
    """The proposal at the path, once it's found able to stand.

    It raises Refused where the proposal lies outside a lane folder, isn't there, isn't JSON, is
    out of its form, or holds a lane that can't stand or that the plugin's files contradict.
    """
    path = os.path.abspath(path)
    folder = os.path.dirname(path)
    if os.path.basename(os.path.dirname(folder)) != ".lane":
        raise Refused(
            [
                (
                    f"{path} lies outside .lane/<yyyymmdd>-<plugin>/, where lay.py keeps a proposal"
                    " at the root of the repository the plugin is in"
                )
            ]
        )
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise Refused([f"{path} isn't there"]) from None
    except json.JSONDecodeError as why:
        raise Refused([f"{path} is no JSON: {why}"]) from None
    out = schema.held(laid.PROPOSAL, data)
    if out:
        raise Refused([f"{path} is out of its form: {out.told()}"])
    found = laid.parsed(data)
    faults = laid.faults(found)
    if faults:
        raise Refused(faults)
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(folder)), data["plugin"]))
    try:
        manifest = plugin.manifest(root)
        parts = {r.name: _part(root, r) for r in found.roles}
    except plugin.Fault as why:
        raise Refused([str(why)]) from None
    faults = _step_faults(found, parts) + _dependency_faults(found, manifest)
    faults += _shared_faults(root, found, parts)
    if faults:
        raise Refused(faults)
    return Checked(path, root, manifest, found, parts)


def _part(root: str, role: laid.Role) -> step.Part:
    """The role's part, which its entry names, the entry running the role in the background.

    It raises `plugin.Fault` where Lane can't read the entry or its part, or where the entry doesn't
    run the role in the background.
    """
    entry = plugin.subagent(root, role.name)
    if not entry.background:
        raise plugin.Fault(
            f"{entry.path} doesn't set `background: true`, which a role with lanes sets"
        )
    return step.part(root, entry)


def _step_faults(found: laid.Laid, parts: dict[str, step.Part]) -> list[str]:
    """Each lane on a step that its role's numbered list doesn't hold."""
    faults = []
    for role in found.roles:
        part = parts[role.name]
        numbers = {s.number for s in part.steps}
        for lane in role.lanes:
            if part.steps and lane.step not in numbers:
                faults.append(
                    f"step {lane.step} of {role.name}: {part.path} holds no step {lane.step}"
                )
    return faults


def _dependency_faults(found: laid.Laid, manifest: plugin.Manifest) -> list[str]:
    """Each dependency that a lane's command names and the manifest doesn't declare."""
    faults = []
    for role in found.roles:
        for lane in role.lanes:
            for name in dict.fromkeys(n for t in lane.takes for n in command.dependencies(t)):
                if name not in manifest.dependencies:
                    faults.append(
                        f"step {lane.step} of {role.name}: {lane.lane} names the dependency"
                        f" {name}, which the manifest of {manifest.name} doesn't declare"
                    )
    return faults


def _shared_faults(root: str, found: laid.Laid, parts: dict[str, step.Part]) -> list[str]:
    """Each step of a part that roles sharing it would lay different lanes on, the lanes laid
    before counted for each role that the proposal doesn't give."""
    try:
        before = [r for r in laid.read(root).roles if found.role(r.name) is None]
    except laid.Unlaid:
        before = []
    sharing: dict[str, list[laid.Role]] = {}
    for role in list(found.roles) + before:
        try:
            path = parts[role.name].path if role.name in parts else _part(root, role).path
        except plugin.Fault:
            continue
        sharing.setdefault(path, []).append(role)
    faults = []
    for path, roles in sharing.items():
        first = roles[0]
        for other in roles[1:]:
            steps = {lane.step for lane in first.lanes + other.lanes}
            for number in sorted(steps):
                if _on(first, number) != _on(other, number):
                    faults.append(
                        f"{first.name} and {other.name} share the part {path} and lay different"
                        f" lanes on step {number} of it"
                    )
    return faults


def _on(role: laid.Role, number: int) -> list[tuple[str, tuple[str, ...]]]:
    """The type and takes of each lane of the role on the step."""
    return [(lane.lane, lane.takes) for lane in role.lanes if lane.step == number]
