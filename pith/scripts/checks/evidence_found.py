"""Every Good and More has evidence, and each quote is really in the work or in the report."""

import os
from typing import List

from parse import LOCATION_PARTS, Result, collapse, read_text


def check(result: Result, essentials_paths: List[str]) -> List[str]:
    problems = []
    for section in result.sections:
        report = collapse(section.report)
        for item in section.items:
            where = "{}:{}: {}".format(result.path, item.line, item.kind)
            if not item.evidence:
                problems.append("{} has no evidence".format(where))
            for evidence in item.evidence:
                at = "{}:{}: evidence ({})".format(result.path, evidence.line, evidence.kind)
                quote = evidence.quote
                if quote is None or not collapse(quote):
                    problems.append('{} is not a quote in "..."'.format(at))
                    continue
                if evidence.kind == "report":
                    if collapse(quote) not in report:
                        problems.append("{} not found in the section's Report".format(at))
                    continue
                parts = LOCATION_PARTS.match(item.location or "")
                if parts is None or not os.path.isfile(parts.group(1)):
                    problems.append("{} has no located file to look in".format(at))
                    continue
                if collapse(quote) not in collapse(read_text(parts.group(1))):
                    problems.append("{} not found in {}".format(at, parts.group(1)))
    return problems
