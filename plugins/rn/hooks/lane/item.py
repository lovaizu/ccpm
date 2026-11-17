"""item.py, the command by which a role or the skill gives the Mark of an Item of the Step due, run
as `script_calls.item_command` gives it: a command of its own, which the guard checks at its call
and whose Mark the guard adds at its PostToolUse, so that the script itself only exits 0.

Takes: the role or skill and the Item's ID, as its two arguments, which it doesn't read, as the
guard read them from the command at its call.
Gives: 0, with no words, as the guard let the run through only where the adapter gave the Item for
the Step due.
Changes: nothing; the guard adds the Mark at the PostToolUse.
Refuses: nothing.
Carries: S5 `SA->>IP: item.py <role> <id>` and `IP-->>SA: exits 0`; S4's Note that the skill's
runs of item.py go as S5 draws.
"""

raise SystemExit(0)
