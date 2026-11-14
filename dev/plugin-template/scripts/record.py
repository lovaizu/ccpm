"""What a role or the orchestrator runs to record its work, and what the guard runs to check the
record, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record.py <command> <args>`:

- `add <record> <of> <id> <gave>` adds to the file `<record>` the step `<id>` of the prompt `<of>`,
  such as `generator 3`, or the practice `<id>` of the best practice `<of>`, such as `code N6.2`,
  with what it left or gave, in the form of domain/record.schema.json.
- `check <record> <role>` reads the record against the steps of the role's prompt and the
  practices of the best practice it works by: each step in order, and each practice within the
  step that takes it, <the step that takes the practices marked While deciding, and the one that
  takes those marked While making>.

Each gives 0 where it finds no problem, 1 with each problem it finds, and 2 with why where it
can't check. The guard passes a role's end only where `check` gives 0, and gives the role what
`check` says where it doesn't.

DELETE_TEMPLATE_COMMENT: each other command of the plugin takes this form: the command as its steps
name it, and what it gives, so that a role reads the result by its exit code. <the step that
takes...>: the steps of the plugin's prompts that take each kind of practice. The code of each
command lies in domain/, apart from Claude Code. It needs only Python 3.9 and the standard library,
as python3 is wherever git is."""

from __future__ import annotations

import sys

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record.py add <record> <of> <id> <gave>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record.py check <record> <role>"
)


def main(argv: list[str]) -> int:
    """Runs the command on its arguments, and gives the exit code that the module names."""
    if (argv[:1], len(argv)) not in ((["add"], 5), (["check"], 3)):
        print(USAGE, file=sys.stderr)
        return 2
    # Until the plugin's code does the command, it can't check, so it passes nothing.
    print(f"record.py {argv[0]}: <the command's code in domain/> isn't made yet", file=sys.stderr)
    return 2


# Run as the command, and not when a test imports it.
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
