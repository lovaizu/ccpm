# Output convention (ccpm)

These rules govern how the assistant checks its work before it reports, and how it answers what the
user says. They say only what the user's global CLAUDE.md and the output style of Claude Code do not
already say.

## Verification

- **Check your work before you report it, as Q18 of
  [prompt.json](../../plugins/turn/core/domain/best-practices/prompt.md) says.**
- **Judge `dev/scripts/check.sh` by its exit code**, as that Q18 judges a check.
- **A push is done only once its CI run has been read**, and the report of the push says its
  result.
  - Rationale: a push left unchecked hands its failure to whoever pushes next.

## Judging what the user says

- **Judge a view or a question from the user by the purpose and best practice, as you would judge
  your own, and say plainly where it holds and where it does not.**
  - Rationale: the user asks so that a second judgment finds what they missed. If you agree only
    because the user said it, you give their guess back to them without a check.

## Replies

- **Do not open with praise, and do not defend a mistake.** When something is wrong, correct it.
- **Keep a code example to 10 lines or fewer.** For more, show only the lines that matter, or put
  the code in its own file.
- **Put a decision, a proposal or a report to the user as
  Q17 of [prompt.json](../../plugins/turn/core/domain/best-practices/prompt.md) says.**
- **Before you say that something cannot be done, offer one other way.**
  - Rationale: praise and a defense of a mistake take the reader's attention and give them nothing
    to act on. A reply that only says "cannot" leaves the reader with no next step.
