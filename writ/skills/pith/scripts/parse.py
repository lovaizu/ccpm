"""Read a result file and an essentials file into plain data for the checks (form: ../result-form.md)."""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

ITEM = re.compile(r"^- (Good|More):\s*(.*)$")
LOCATION = re.compile(r"^`([^`]+)`")
LOCATION_PARTS = re.compile(r"^(.+):(\d+)(?:-(\d+))?$")
EVIDENCE = re.compile(r"^\s+- Evidence \((work|report)\):\s*(.*)$")


def collapse(text: str) -> str:
    return " ".join(text.split())


@dataclass
class Evidence:
    kind: str  # "work" or "report"
    raw: str
    line: int

    @property
    def quote(self) -> Optional[str]:
        text = self.raw.strip()
        if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        return None


@dataclass
class Item:
    kind: str  # "Good" or "More"
    rest: str
    line: int
    evidence: List[Evidence] = field(default_factory=list)

    @property
    def location(self) -> Optional[str]:
        match = LOCATION.match(self.rest)
        return match.group(1) if match else None


@dataclass
class Section:
    heading: str
    line: int
    report: str = ""
    items: List[Item] = field(default_factory=list)


@dataclass
class Result:
    path: str
    sections: List[Section]


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_result(path: str) -> Result:
    sections: List[Section] = []
    section: Optional[Section] = None
    in_report = False
    report_lines: List[str] = []

    def close_report() -> None:
        if section is not None and report_lines:
            section.report = "\n".join(report_lines)

    for number, line in enumerate(read_text(path).splitlines(), start=1):
        if line.startswith("## "):
            close_report()
            section = Section(heading=line[3:].strip(), line=number)
            sections.append(section)
            in_report, report_lines = False, []
            continue
        if section is None:
            continue
        item = ITEM.match(line)
        if item:
            close_report()
            in_report, report_lines = False, []
            section.items.append(Item(kind=item.group(1), rest=item.group(2), line=number))
            continue
        evidence = EVIDENCE.match(line)
        if evidence and section.items:
            section.items[-1].evidence.append(
                Evidence(kind=evidence.group(1), raw=evidence.group(2), line=number))
            continue
        if line.startswith("Report:"):
            in_report, report_lines = True, [line[len("Report:"):]]
            continue
        if in_report:
            report_lines.append(line)
    close_report()
    return Result(path=path, sections=sections)


def parse_questions(path: str) -> List[str]:
    """Return the top-level `- ` list items of an essentials file, outside code fences."""
    questions: List[str] = []
    current: Optional[List[str]] = None
    fenced = False
    for line in read_text(path).splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            current = None
            continue
        if fenced:
            continue
        if line.startswith("- "):
            current = [line[2:]]
            questions.append("")
        elif current is not None and line.strip() and not line.startswith((" ", "\t", "#")):
            current.append(line)
        else:
            current = None
            continue
        questions[-1] = collapse(" ".join(current))
    return questions


def heading_for(essentials_path: str, question: str) -> str:
    return "{}: {}".format(os.path.basename(essentials_path), question)
