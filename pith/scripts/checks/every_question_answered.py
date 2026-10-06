"""Every question of every essentials file has its section with at least one Good or More."""

from typing import List

from parse import Result, collapse, heading_for, parse_questions


def check(result: Result, essentials_paths: List[str]) -> List[str]:
    sections = {collapse(section.heading): section for section in result.sections}
    problems = []
    for essentials in essentials_paths:
        for question in parse_questions(essentials):
            heading = heading_for(essentials, question)
            section = sections.get(collapse(heading))
            if section is None:
                problems.append("{}: no section `## {}`".format(result.path, heading))
            elif not section.items:
                problems.append("{}:{}: no Good or More under `## {}`".format(
                    result.path, section.line, heading))
    return problems
