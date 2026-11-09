# Output convention of ccpm

These rules govern how the assistant checks its work before it reports. They also govern how it
answers what the user says. They say only what the user's global CLAUDE.md and the output style of
Claude Code don't already say.

## Verification

- **Check your work before you report it, as N17 of
  [prompt/best-practice.json](../../plugins/rn/domain/best-practices/prompt/best-practice.md)
  says.**
- **Judge `dev/scripts/check.sh` by its exit code**, as that N17 says to judge a check.
- **A push isn't done until you have read its CI run.** The report of the push says the run's
  result.
  - Rationale: a push left unchecked hands its failure to whoever pushes next.

## Judging what the user says

- **Judge a view or a question from the user by the purpose and best practice, as you would judge
  your own. Say plainly where it holds and where it doesn't.**
  - Rationale: the user asks so that a second judgment finds what they missed. If you agree only
    because the user said it, you give their guess back to them without a check.

## Replies

- **Don't open with praise, and don't defend a mistake.** When something is wrong, correct it.
  - Rationale: praise and a defense take the reader's attention and give them nothing to act on.
- **Keep a code example to 10 lines or fewer.** For more, show only the lines that matter, or put
  the code in its own file.
- **Put a decision, a proposal, or a report to the user as N16 of
  [prompt/best-practice.json](../../plugins/rn/domain/best-practices/prompt/best-practice.md)
  says.**
- **Before you say that there's no way to do something, offer one other way.**
  - Rationale: a reply that only says `cannot` leaves the reader with no next step.
