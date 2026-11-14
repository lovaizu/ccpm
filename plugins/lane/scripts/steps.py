"""Decides where a plugin's Roles and Steps lie and how each Step reads without the text that Lane
laid: the numbered list under `## Steps` of the skill's SKILL.md, of each subagent's file in
`agents/`, of each file of the plugin that a body names by `${CLAUDE_PLUGIN_ROOT}/`, and, for each
skill, of the SKILL.md of each command that its Route waits for or goes after."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from domain.laid_set import Laid


@dataclass(frozen=True)
class Step:
    """One step as the user wrote it, the data model's Step: the role, its number, the file in the
    plugin's folder that holds it, its words, and each laid sentence that the user changed, which
    Lane keeps as the user's own words."""

    role: str
    number: int
    file: str
    words: str
    kept: tuple[str, ...] = ()


@dataclass(frozen=True)
class Role:
    """A skill or a subagent of the plugin, the data model's Role: its name, whether it's a
    skill, the file of its entry, and its Steps in order."""

    name: str
    skill: bool
    entry: str
    steps: tuple[Step, ...] = field(default_factory=tuple)


def roles(plugin_root: str, laid: Laid, commands: Mapping[str, str] | None = None) -> list[Role]:
    """Each skill of the plugin and each of its subagents with their Steps, each Step without the
    sentences that the Laid names where it still holds them word for word, and with each it holds
    changed kept as the user's, each skill's Steps from its own file, from each file its body names,
    and from the SKILL.md of each command that `commands` gives it, by the command's name, such as
    `{"approve": "write"}`; a command so given is no skill of its own. Raises Fault, naming the file
    and the line, with the plugin's maker to fix it, where the plugin has no skill, or where a Role
    has no numbered list under `## Steps`."""
    raise NotImplementedError("steps.roles")


def files_of(role: Role) -> tuple[str, ...]:
    """Each file that holds a Step of the role, once each."""
    raise NotImplementedError("steps.files_of")


def fingerprint(found: Sequence[Role]) -> str:
    """A text that changes whenever a Step's words, a Role, or a file that holds one changes, by
    which `lay.py write` sees that the Steps changed since `lay.py print` showed a Proposal."""
    raise NotImplementedError("steps.fingerprint")
