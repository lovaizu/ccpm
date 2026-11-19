"""How Lane's unit cases write each sentence that Lane gives the AI, as Lane's
plugins/lane/docs/rules-and-adapters.md words it, for the sentences that more than one interface's
cases hold: the step's sentence of each rule type, by the step, the values of its rule, and the
role, `log:writer` unless given."""

from __future__ import annotations

from rule_types.words import listed


def at(step: str, role: str = "log:writer") -> str:
    return f"You're at the step `{step}` of {role}"


def writes_only(step: str, paths: list[str], written: str, role: str = "log:writer") -> str:
    return (
        f"{at(step, role)}, which writes only {listed(paths)}.\nWrite there instead of {written}."
    )


def never_reads(step: str, paths: list[str], file: str) -> str:
    return f"{at(step)}, which never reads {listed(paths)}.\nLeave {file} unread."


def runs_only(step: str, named: list[str]) -> str:
    runs = f"only {listed(named)}" if named else "no command"
    return (
        f"{at(step)}, which runs {runs}.\nRun only those here, and the rest at a step that names"
        " them."
    )


def comes_before(due: str, step: str, role: str = "log:writer") -> str:
    return (
        f"{at(due, role)}, which comes before `{step}`.\n"
        f"Do `{due}` and mark it done with lane-step {due} first."
    )


def ends_before(step: str, role: str = "log:writer") -> str:
    return (
        f"You end before the step `{step}` of {role} is done.\n"
        f"Do it and mark it done with lane-step {step}."
    )


def reads_whole_of(step: str, paths: list[str], unread: list[str]) -> str:
    return (
        f"{at(step)}, which reads whole {listed(paths)}.\n"
        f"Read {listed(unread)} before you mark it done."
    )


def checklist_of(step: str, left: list[str]) -> str:
    return (
        f"{at(step)}, whose checklist isn't done: {listed(left)}.\n"
        f"Do each and mark it done with lane-item {step} <item> first."
    )


def no_result(step: str, results: list[str], role: str = "log:writer") -> str:
    return (
        f"You end the step `{step}` of {role} with no result it may give.\n"
        f"Give {listed(results)} with lane-result first."
    )


def work_undone(step: str, ends: list[str]) -> str:
    return (
        f"{at(step)}, whose work isn't done.\n"
        f"Do it and mark it done with lane-step {step}; give {listed(ends)} with lane-result only"
        " where you can't go on."
    )


def check_fails(step: str, said: str, role: str = "log:writer") -> str:
    return f"You end the step `{step}` of {role}, which its check doesn't pass:\n{said}"
