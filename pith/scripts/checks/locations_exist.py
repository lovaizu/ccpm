"""Every Good and More has a location whose file exists and whose line or range is within it."""

import os
from typing import List

from parse import LOCATION_PARTS, Result, read_text


def check(result: Result, essentials_paths: List[str]) -> List[str]:
    problems = []
    for section in result.sections:
        for item in section.items:
            where = "{}:{}: {}".format(result.path, item.line, item.kind)
            location = item.location
            if location is None:
                problems.append("{} has no location `path:line`".format(where))
                continue
            parts = LOCATION_PARTS.match(location)
            if parts is None:
                problems.append("{} location `{}` is not `path:line` or `path:a-b`".format(
                    where, location))
                continue
            path, first = parts.group(1), int(parts.group(2))
            last = int(parts.group(3)) if parts.group(3) else first
            if not os.path.isfile(path):
                problems.append("{} location `{}`: no such file".format(where, location))
                continue
            count = len(read_text(path).splitlines())
            if not 1 <= first <= last <= count:
                problems.append("{} location `{}`: outside the file's {} lines".format(
                    where, location, count))
    return problems
