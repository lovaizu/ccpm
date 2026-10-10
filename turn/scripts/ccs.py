"""The record (CCS) as YAML parts of `- kind: "value"` lines, read and written without a YAML
library, since turn runs on the standard library only."""
import json
import re

PART = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$")
ITEM = re.compile(r"^\s+- ([^:]+): (.*)$")
NEEDED = (("focal_entities", "work"), ("focal_entities", "receiver"),
          ("goal_orientation", "acceptance"), ("goal_orientation", "use"),
          ("constraints", "language"))


class Bad(Exception):
    """A line not in the record's form."""


def read(path):
    with open(path) as f:
        return f.read()


def load(text):
    """The parts in their order, each a list of (kind, value)."""
    parts, cur = [], None
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = PART.match(line)
        if m:
            cur = (m.group(1), [])
            parts.append(cur)
            continue
        m = ITEM.match(line)
        if not m or cur is None:
            raise Bad(f"line {n} is neither `part:` nor `  - kind: \"value\"`: {line}")
        value = m.group(2).strip()
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                raise Bad(f"line {n} has a value not closed as one quoted string: {line}")
        cur[1].append((m.group(1).strip(), value))
    return parts


def dump(parts):
    out = []
    for name, items in parts:
        out.append(f"{name}:")
        out += [f"  - {k}: {json.dumps(v, ensure_ascii=False)}" for k, v in items]
    return "\n".join(out) + "\n"


def values(parts, part, kind):
    return [v for name, items in parts if name == part for k, v in items if k == kind]


def missing(parts):
    """What turn cannot start without, as `part.kind`."""
    return [f"{p}.{k}" for p, k in NEEDED if not any(str(v).strip() for v in values(parts, p, k))]
