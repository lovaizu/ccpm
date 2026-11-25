"""Decides template's command line: what it takes, what it prints, and the exit code by which
whoever ran it reads its result: 0 where the document holds its template, 1 with what's wrong, and
2 with the usage."""

from __future__ import annotations

import os

from fault import Answer, Wrong, answered

from template import check
from template.language import ENGLISH

USAGE = """\
usage: template <kind> <document> [<language>]
"""

# What the reader of the faults is to do with them, as the purpose is a document of the vital few,
# not a fit to the template.
_BEFORE = (
    "rn's template check: the template holds only the vital few. Cut each place below as trivia,"
    " or put its vital point in the template's form."
)
_AFTER = (
    "Where the form would lose what the document's people need, keep it, and propose a change to"
    " the template."
)


def main(argv: list[str], cwd: str, plugin_root: str) -> Answer:
    """The exit code, stdout, and stderr of `template` with the arguments, from the folder
    `cwd`, with rn's folder at `plugin_root`.

    `<kind> <document> [<language>]` gives 0 where the document, by its path from `cwd`, holds the
    template of its kind among rn's best practices and nothing beside it, in its language, such as
    Japanese, as `template.check.faults` holds it, English where none is given, printing nothing,
    and 1 with each place where it leaves it, one to a line as `<document>:<line>: <what>`, between
    a line before them on why the template holds and one after them on when to change the
    template; or 1 where
    the kind has no Markdown template, the document is missing or isn't UTF-8 text, or the
    language is blank.

    2 with the usage where the arguments are other than a kind, a document, and a language or
    none."""
    if len(argv) not in (2, 3):
        return 2, "", USAGE
    language = argv[2] if len(argv) == 3 else ENGLISH
    return answered("template", lambda: _template(argv[0], argv[1], language, cwd, plugin_root))


def _template(kind: str, document: str, language: str, cwd: str, plugin_root: str) -> Answer:
    """The result of `template` on the document in its language against the kind's
    template."""
    path = check.of_kind(plugin_root, kind)
    with open(path, encoding="utf-8") as file:
        form = file.read()
    found = check.faults(form, _read(os.path.join(cwd, document), document, kind), language)
    if not found:
        return 0, "", ""
    said = "".join(f"{document}:{each.line}: {each.what}\n" for each in found)
    return 1, "", f"{_BEFORE}\n{said}{_AFTER}\n"


def _read(path: str, named: str, kind: str) -> str:
    """The text of the document at the path, which the call names as `named`. Raises Wrong where
    it isn't there or isn't UTF-8 text."""
    try:
        with open(path, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise Wrong(f"{named}: no such file to check against the template of {kind}") from None
    except UnicodeDecodeError:
        raise Wrong(f"{named}: isn't UTF-8 text, which the check of a template reads") from None
