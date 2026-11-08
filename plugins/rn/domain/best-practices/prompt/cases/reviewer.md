# Reviewer, right but heavy

A subagent of Claude Code that reviews a change before its pull request opens. Its tools, its guard,
and its trials hold, and it finds what it should on every run. Its body shouts, walks a judgment
through numbered steps, checks by eye what a linter checks, holds a whole style guide, and puts its
verdict last. It's a kept case of the [prompt best practice](../best-practice.md): a prompt with the
verdict on each question that someone who knows the work of the AI that runs it gives, so that an
evaluator proves itself on it before anyone trusts its verdicts.

## Where it runs

A person runs it by name in their main conversation, on Opus or Sonnet, and reads its reply as it
comes back. The repository runs `ruff` on each pull request, with a line limit of 100 and the order
of imports among its rules. `scripts/git-read.py` lets through only `git diff`, `git log`, and
`git show`, and blocks any other command with a message that names those three. Its tests give it
each of the three and a `git push`, and see the push blocked and the others let through.

## Prompt

`agents/reviewer.md`:

````markdown
---
name: reviewer
description: Reviews the change on the current branch for bugs and for this repository's style before a pull request opens, and reports each finding with its file and line. Use when the person asks for a review of their change, or before they open a pull request.
tools: Read, Grep, Glob, Bash
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: python3 scripts/git-read.py
---

You review the change on this branch, `git diff main...HEAD`, so that its author can fix what's
wrong before anyone else reads it. You're done once you've read every changed hunk and reported
each finding. Don't fix anything, as the author decides what to change.

YOU MUST FOLLOW EVERY STEP. NEVER SKIP A STEP.

1. Run `git diff main...HEAD`.
2. List the changed files.
3. Read each changed hunk of the first file.
4. Check each name against the style guide below.
5. Check each line's length. NO LINE MAY PASS 100 CHARACTERS.
6. Check the order of the imports.
7. Check each changed function for a bug: an input it mishandles, a case it misses, or a call that
   can fail unhandled.
8. Check each new function for a test.
9. Repeat 3 to 8 for each other file.
10. Write the findings.
11. Read the findings again.
12. Reply.

CRITICAL: ALWAYS QUOTE THE LINE OF EACH FINDING.

<examples>
<example>
Finding: src/export.py:41, a bug. `rows[0]` fails on an empty export, which the caller allows.
Quote: `first = rows[0]`
</example>
<example>
Finding: src/cli.py:12, the style guide's names. `tmp` holds the output path, so `output_path`.
Quote: `tmp = args.out`
</example>
<example>
Finding: none in tests/test_export.py. The new test covers the empty export.
</example>
</examples>

Reply with each file you read, in order. Then each finding, as the examples show. Then what you
didn't review and why. Last, your verdict: ready, or what to fix first.

# Style guide

[The 240 lines of docs/style.md, pasted here whole: names, comments, errors, logging, tests, and
the layout of modules.]
````

The evals hold 24 diffs from past reviews, each with the findings the maintainers kept, half of them
with none. Code grades whether each kept finding's file and line appear, and a judge grades whether
each other finding is real. The judge gave the maintainers' verdict on 30 kept findings, real and
not, before anyone used it.

## How it ran held back

12 diffs kept apart from the making ran five times each on each of Opus and Sonnet. Every run reported
each kept finding of each diff and reported nothing on the diffs that held none.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | The body says the review is for the author before others read it, puts fixing out of it, and ends once the reviewer has read every hunk and reported each finding. |
| Q2 | yes | It names the command that gives the change, and the style guide lies in the prompt itself. |
| Q3 | no | Only the rule against fixing gives its reason. The rules in capitals give none, so a case such as a long URL in a comment, which the 100-character rule never foresaw, gets no ground to judge from. |
| Q4 | yes | Three examples differ: a bug, a name, and a file with no finding, in one format. |
| Q5 | no | Twelve numbered steps lead a review whose order doesn't matter, and the capitals bind every run to them. |
| Q6 | no | It checks each line's length and the order of the imports by eye, where `ruff` gives the one right answer. |
| Q7 | yes | It has no tool that writes, and Bash only through the guard. |
| Q8 | yes | The guard holds Bash to three git commands that only read, and its tests see a push blocked and the three let through. |
| Q9 | yes | Each fix goes back to the author, and the reviewer settles each finding itself. |
| Q10 | yes | The person can act on each finding by its file and line, and the reply says what went unreviewed. |
| Q11 | no | The reply opens with the files read, and the verdict, which is what the person decides from, comes last. |
| Q12 | yes | Each finding quotes the line it rests on, and the reply says what the reviewer didn't review. |
| Q13 | yes | The description says what it does and when, in the words a person asks with. |
| Q14 | yes | Each instruction stands once, and none pulls against another. |
| Q15 | no | The whole style guide loads on every run, though most changes bear on only a few of its sections, and it could lie in a file the body links. |
| Q16 | yes | 24 diffs from past reviews, half with no finding, graded by code where it can tell and by a judge proven on kept findings. |
| Q17 | yes | On the held-back diffs, every run on both models found what the maintainers found, and nothing on the diffs that held none. |
