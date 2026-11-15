"""Decides record.py's command line: which command each call names, what it takes, what it prints,
and the exit code by which a role or the guard reads its result: 0 where it did what it names, 1
with what's wrong, and 2 with why it couldn't run, or with the usage."""

from __future__ import annotations

import os

from fault import Wrong

from record import template

USAGE = """\
usage: record.py add <record> <of> <id> <gave>
       record.py check <role> <result> [<cut>]
       record.py template <kind> <document>
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


def main(argv: list[str], cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `record.py` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`:

    - `add <record> <of> <id> <gave>` adds the entry to the record; 1 where the ID is neither a
      step's number nor a practice's ID, or `gave` is empty.
    - `check <role> <result> [<cut>]` gives 0 where rn's check finds no fault in the role's end, 1
      with each fault, and 2 where it can't check.
    - `template <kind> <document>` gives 0 where the document, by its path from `cwd`, holds the
      template of its kind among rn's best practices and nothing beside it, printing nothing, and
      1 with each place where it leaves it, one to a line as `<document>:<line>: <what>`, between
      a line before them on why the template holds and one after them on when to change the
      template; or 1 where the kind has no Markdown template, or the document is missing or isn't
      UTF-8 text.

    2 with the usage where the arguments are none of these."""
    if argv[:1] == ["template"]:
        if len(argv) != 3:
            return 2, "", USAGE
        try:
            return _template(argv[1], argv[2], cwd, plugin_root)
        except Wrong as wrong:
            return 1, "", f"record.py: {wrong}\n"
    raise NotImplementedError("command.main")


def _template(kind: str, document: str, cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """The result of `record.py template` on the document against the kind's template."""
    path = template.of_kind(plugin_root, kind)
    with open(path, encoding="utf-8") as file:
        form = file.read()
    found = template.faults(form, _read(os.path.join(cwd, document), document, kind))
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
