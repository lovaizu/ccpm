# Slug brief, pointed at the practice

A brief that a main conversation of Claude Code wrote for a subagent, to build a command in
JavaScript by a specification. It points at the code best practice and holds none of its order, so
its maker wrote the code before the tests. What the subagent made is the code best practice's case
[Slug, tested late](../../code/cases/slug.md). It's a kept case of the
[prompt best practice](../best-practice.md): a prompt with the verdict on each question that someone
who knows the work of the AI that runs it gives, so that an evaluator proves itself on it before
anyone trusts its verdicts. A question whose practice excludes a prompt of this kind has the verdict
n/a.

## Where it runs

The main conversation started a general-purpose subagent, which has every tool, with the brief
below as its whole prompt, and ran it once. A subagent starts with none of the conversation that
started it. Earlier in that conversation, the person and the AI had agreed to put the command in
`bin/`, beside the project's other commands.

## Prompt

```text
Build the slug command. Specification:

- `slug <title>` prints the slug of the title and exits 0.
- A slug holds the title's letters from a to z and digits from 0 to 9, in lower case, with each
  run of anything else as one hyphen and no hyphen at either end.
- A slug is at most 50 characters, with no hyphen at its end after the cut.
- A title with no letter or digit, or any number of arguments other than one, prints what to fix
  on standard error, and the command exits 2.

Use Node.js 18 and no packages. Put it beside the other commands, as we said.

Write it by plugins/rn/domain/best-practices/code/best-practice.json, as .claude/rules/dev.md
step 6 says.

Never install anything.

Report when done.
```

## How it ran

1. The subagent read the specification and skimmed the code best practice's goal and first
   questions.
2. It wrote `tools/slug.mjs` and `tools/cli.mjs`, ran the command by hand, then wrote the tests and
   saw them pass.
3. It reported "Done. slug and its tests are in tools/, all tests pass."

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | no | "Report when done" names no end the command serves and no check of done, so the subagent stopped once its tests passed. |
| Q2 | no | The place of the files rests on a conversation the subagent never saw, so it guessed `tools/`. |
| Q3 | no | "Never install anything" gives no reason, so the subagent can't tell whether a test runner fetched for one run counts. |
| Q4 | n/a | The specification holds the cases, and the task has no form to show by example. |
| Q5 | no | Writing the tests before the code is an order the result needs, yet it lives only behind a pointer to two files, and the brief gives no step for it. |
| Q6 | no | The brief names no command whose result shows the work right, such as `node --test`, so the subagent judged its own work by hand. |
| Q7 | no | A general-purpose subagent has every tool, `git push` and the web among them, where the task needs only files and Node.js. |
| Q8 | no | Nothing holds the tests first, so the one order the brief meant to keep rests on the subagent's reading of a pointer. |
| Q9 | no | The brief says nothing of what goes back, so the subagent settled the place of the files itself, a choice already the caller's. |
| Q10 | no | "Report when done" asks for no form, so the caller learns neither the files made nor what the subagent left undone. |
| Q11 | n/a | The subagent reports to the main conversation, an AI, and puts nothing to a person. |
| Q12 | no | Nothing asks what the subagent checked, and "all tests pass" rests on tests that leave the boundaries untried. |
| Q13 | n/a | Its caller starts it by its text, and no host chooses it. |
| Q14 | yes | Each instruction stands once, and none pulls against another. |
| Q15 | yes | The brief is short, and each line bears on the task. |
| Q16 | n/a | A brief for one run has no suite, and its caller checks the result. |
| Q17 | no | Its one run wrote the code before the tests, the order the brief meant to hold. |
