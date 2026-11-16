"""step.py, the command by which a role or the skill gives a Step's Mark, run as
`script_calls.step_command` gives it: a command of its own, which the guard checks at its call and
whose Mark the guard adds at its PostToolUse, so that the script itself only exits 0.

Takes: the role or skill and the Step's number, as its two arguments, which it doesn't read, as the
guard read them from the command at its call.
Gives: 0, with no words, as the guard let the run through only where it took the Mark.
Changes: nothing; the guard adds the Mark at the PostToolUse.
Refuses: nothing.
Carries: S6 `SA->>SP: step.py <role> <n>` and `SP-->>SA: exits 0`; S5's Note that the skill's runs
of step.py go as S6 draws.
"""

raise SystemExit(0)
