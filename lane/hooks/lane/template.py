"""A Markdown template, and a written file held to it: the keys the template's frontmatter names must
be in the file's, each with its value, and the template's headings must be among the file's, in
order and at their level, other headings and body text free between them; text in `<...>`, in a
value or a heading, is free, any text but none, and the rest is taken as written. A heading is an
ATX heading, `#` to `######` and a space, outside a code fence; frontmatter is read as lines of
`key: value` alone, a value plain or quoted, and anything else in it, such as a block scalar, a
nested mapping or a value over several lines, is refused rather than guessed."""

from __future__ import annotations

import re
from typing import NamedTuple

# What opens and closes frontmatter, on a line of its own at the top of the file.
MARK = "---"
# A part of a template that is free.
FREE = re.compile(r"<[^<>]+>")
# A line of frontmatter: a plain key, a colon, and the value after a blank, if any.
KEY_LINE = re.compile(r"(?P<key>[A-Za-z0-9_][A-Za-z0-9_.-]*):(?:[ \t]+(?P<value>.*))?")
# A value's first character that makes it what the reader does not read: a block scalar, an
# anchor, an alias or a tag.
UNREAD = ("|", ">", "&", "*", "!")
# A comment ending a plain value, after a blank.
COMMENT = re.compile(r"[ \t]#.*")
# An ATX heading, up to three blanks in: its marks, and its text after a blank, if any.
HEADING = re.compile(r" {0,3}(?P<marks>#{1,6})(?:[ \t]+(?P<text>.*))?")
# The marks that may close a heading's text, after a blank.
CLOSING = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
# A line opening a code fence, up to three blanks in: three or more of one mark, a backtick or a
# tilde.
FENCE = re.compile(r" {0,3}(?P<fence>(?P<mark>[`~])(?P=mark){2,})")


class Template(NamedTuple):
    """What a template asks: each frontmatter key with its value as written, and each heading as
    its level and its text as written, in order."""

    keys: list[tuple[str, str]]
    headings: list[tuple[int, str]]


def read(text: str) -> Template:
    """The template the text holds; stops with ValueError where its frontmatter cannot be read, or
    where it asks nothing, holding no heading and no frontmatter key."""
    lines = text.splitlines()
    found = keys(lines) or {}
    asked = Template(
        [(k, v) for k, (_, v) in found.items()],
        [(level, said) for _, level, said in headings(lines, body(lines))],
    )
    if not asked.keys and not asked.headings:
        raise ValueError("holds no heading and no frontmatter key, so it would check nothing")
    return asked


def closing(lines: list[str]) -> int | None:
    """Where the frontmatter the lines open with closes; None where they open with none."""
    if lines[:1] != [MARK]:
        return None
    if MARK not in lines[1:]:
        raise ValueError(f'line 1: expected frontmatter closed by "{MARK}", found none')
    return lines.index(MARK, 1)


def body(lines: list[str]) -> int:
    """Where the body begins, after the frontmatter, if any, closed."""
    try:
        end = closing(lines)
    except ValueError:
        return 0
    return 0 if end is None else end + 1


def keys(lines: list[str]) -> dict[str, tuple[int, str]] | None:
    """Each key of the frontmatter the lines open with, with its line and its value as text; None
    where they open with none. Stops with ValueError naming the line where it cannot be read."""
    end = closing(lines)
    if end is None:
        return None
    found: dict[str, tuple[int, str]] = {}
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY_LINE.fullmatch(line)
        value = text_of((m["value"] or "").strip()) if m else None
        if m is None or value is None:
            raise ValueError(
                f'line {number}: expected a "key: value" line lane reads, found "{line}"'
            )
        if m["key"] in found:
            raise ValueError(f'line {number}: expected each key once, found "{m["key"]}" again')
        found[m["key"]] = (number, value)
    return found


def text_of(value: str) -> str | None:
    """The text of a value as written on its line: quotes and a comment taken off; None where it
    is what the reader does not read."""
    if value.startswith(UNREAD):
        return None
    quote = value[:1]
    if quote in ("'", '"'):
        inner = value[1:-1]
        # In single quotes a quote is written twice; in double quotes a backslash begins an escape,
        # which is left unread as a lone quote is.
        single = quote == "'"  # pragma: no mutate
        bare = inner.replace("''", "") if single else inner.replace("\\", '"')
        if len(value) < 2 or not value.endswith(quote) or quote in bare:
            return None
        return inner.replace("''", "'") if single else inner
    plain = COMMENT.sub("", value).rstrip()
    # A colon and a blank in a plain value would begin a nested mapping.
    return None if ": " in plain else plain


def headings(lines: list[str], start: int) -> list[tuple[int, int, str]]:
    """Each ATX heading outside a code fence from the line at start on, as its line in the file,
    its level and its text, closing marks taken off."""
    found = []
    # The line that would close the fence open, None where none is.
    close = None
    for number, line in enumerate(lines[start:], start=start + 1):
        if close:
            close = None if close.fullmatch(line) else close
            continue
        opened = FENCE.match(line)
        if opened:
            fence, mark = map(re.escape, opened.group("fence", "mark"))
            close = re.compile(rf" {{0,3}}{fence}{mark}*[ \t]*")
            continue
        m = HEADING.fullmatch(line)
        if m:
            found.append((number, len(m["marks"]), CLOSING.sub("", m["text"] or "").strip()))
    return found


def fits(asked: str, said: str) -> bool:
    """Whether the text said holds to the text asked, each free part of it any text but none."""
    plain = FREE.split(asked)
    return re.fullmatch(".+".join(map(re.escape, plain)), said) is not None


def held(asked: Template, text: str) -> str:
    """The point the written text is out of the template by, at its line, what was expected and
    what was found; "" where it holds."""
    lines = text.splitlines()
    try:
        return keys_held(asked, lines) or headings_held(asked, lines)
    except ValueError as unread:
        return str(unread)


def keys_held(asked: Template, lines: list[str]) -> str:
    """The point the file's frontmatter is out of the template's keys by; "" where it holds."""
    if not asked.keys:
        return ""
    if lines[:1] != [MARK]:
        first = f'"{lines[0]}"' if lines else "an empty file"
        return f'line 1: expected frontmatter opened by "{MARK}", found {first}'
    found = keys(lines) or {}
    for key, value in asked.keys:
        if key not in found:
            return f'line 1: expected the frontmatter key "{key}", found none'
        number, said = found[key]
        if not fits(value, said):
            return f'line {number}: expected "{key}: {value}", found "{key}: {said}"'
    return ""


def headings_held(asked: Template, lines: list[str]) -> str:
    """The point the file's headings are out of the template's by; "" where they hold."""
    written = headings(lines, body(lines))
    line = body(lines) + 1
    for level, said in asked.headings:
        at_level = [w for w in written if w[1] == level]  # pragma: no mutate
        same = [w for w in at_level if fits(said, w[2])]
        if not same:
            near = [w for w in written if fits(said, w[2])]
            found = f'"{"#" * near[0][1]} {near[0][2]}" at line {near[0][0]}' if near else "none"
            return f'from line {line}: expected the heading "{"#" * level} {said}", found {found}'
        # The first that holds, so each heading after it has the most left to be found among.
        written = written[written.index(same[0]) + 1 :]
        line = same[0][0] + 1
    return ""
