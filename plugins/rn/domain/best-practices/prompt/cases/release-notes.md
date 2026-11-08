# Release notes, open to every request

A skill of Claude Code that writes the entry of a project's next release in its `CHANGELOG.md`, with
a script that drafts the entry and checks it. Its body and its evals are sound. Its description, its
tools, and its trials fall short. It's a kept case of the
[prompt best practice](../best-practice.md): a prompt with the verdict on each question that someone
who knows the work of the AI that runs it gives, so that an evaluator proves itself on it before
anyone trusts its verdicts.

## Where it runs

The maintainers of a library run it in their main conversation of Claude Code before each release.
Some run Opus, and some run Sonnet. `scripts/notes.py` has tests of its own, and a release runs its
`draft` and `check` commands. A skill's `allowed-tools` approves the tools it names ahead, and
withholds none. The project has no hook or deny rule.

## Prompt

`SKILL.md`:

````markdown
---
name: release-notes
description: Helps with releases.
allowed-tools: Bash(git *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/notes.py *)
---

# Release notes

You write the entry of the next release in this repository's `CHANGELOG.md`, for the people who
upgrade: each change they'd notice, in their words, so that they can tell from the entry alone
whether the upgrade asks anything of them. A commit that changes nothing they'd notice, such as a
test or a refactor, stays out. You don't tag, publish, or push. The maintainer does that once they've
read the entry.

The entry is done when `python3 ${CLAUDE_SKILL_DIR}/scripts/notes.py check CHANGELOG.md` exits 0,
which checks its form, its version, and its date, and each change since the last tag that a user
would notice has its line.

## Steps

1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/notes.py draft`. It reads the commits since the last
   tag, picks the next version by their types, and writes a draft entry at the top of
   `CHANGELOG.md`, one line for each commit.
2. Rewrite the draft's lines for the people who upgrade, as the rules below say.
3. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/notes.py check CHANGELOG.md`, mend what it names, and
   run it again until it exits 0.

## Rules

- Write each line as what the user can now do or must now do, not what the code does, as a user
  reads the entry to decide whether to upgrade.
- Put a change that asks the user to act, such as a renamed option, under **Breaking**, with what to
  do, as a user who misses it finds their setup broken.
- Where a commit's message doesn't say what changed for users, read its diff with `git show`.
- Where you can't tell whether a change breaks anything, keep it under **Breaking** and say so in
  your reply, as the maintainer decides it.

## Examples

<example>
Draft: `fix(export): keep tzinfo in to_csv`
Line: Exports to CSV now keep each time's time zone.
</example>

<example>
Draft: `feat(cli)!: rename --out to --output`
Line, under Breaking: The option `--out` is now `--output`. Change it in your scripts.
</example>

<example>
Draft: `test: cover empty input`
Line: none, as the user notices no change.
</example>

## Your reply

Open with one line: the version, the check's result as it printed it, and `Tag v<version> and
publish?` Then the entry, and each commit you left out with why.
````

`evals/evals.json` holds six tasks, each the repository at a past release's tag with its commits
since the one before. Five are real releases. The sixth holds only tests and refactors, and its
entry must say there's no change for users. `notes.py check` grades each entry's form, a check of
the file grades whether each commit the maintainers marked as visible has its line, and a judge
grades whether each line says what the user can now do. The judge gave the maintainers' verdict on
12 kept entries, 7 good and 5 not, before anyone used it.

## How the maker tried it

1. The maker ran the six tasks without the skill and kept the entries, which listed commit messages
   and missed the renamed option of one release.
2. The maker wrote the skill, ran each task once on Opus, and saw all six pass.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | The body says the entry is for the people who upgrade, leaves tagging and pushing out, and ends at the check's exit code. |
| Q2 | yes | It names the file, the script and what each command does, and `git show` for a message that says too little. |
| Q3 | yes | Each rule carries its reason, and the rule for a doubtful break says what to do when the AI can't tell. |
| Q4 | yes | Three examples differ: a fix, a breaking change, and a commit that gets no line, each in one format. |
| Q5 | yes | Three steps, each one action with what shows it done, in the order the result needs: the draft, the rewrite, the check. |
| Q6 | yes | The script picks the version and the date and checks the form, and the AI runs it until it passes. |
| Q7 | no | `Bash(git *)` approves every git command, `git push` among them, where the task needs only `git log` and `git show`. |
| Q8 | no | Nothing but the words holds the rule against tagging, publishing, and pushing, and no test tries it. |
| Q9 | yes | The tag, the publication, and a doubtful break go back to the maintainer, and the AI settles each line itself. |
| Q10 | yes | The reply gives the entry, the check's result, and each commit left out with why. |
| Q11 | yes | The first line holds the version, the check's result, and the one decision, worded so that yes takes it. |
| Q12 | yes | The check's result comes as the script printed it, and each commit left out comes with its reason. |
| Q13 | no | "Helps with releases" says neither what the skill does nor when, so the host can pick it for a request to cut a release, which its body doesn't do. |
| Q14 | yes | Each rule stands once, and "the entry" names one thing throughout. |
| Q15 | yes | The body holds only what changes the entry, and the script runs without the AI reading it. |
| Q16 | yes | Six tasks from real releases, one where no line should appear, graded by code where it can tell and by a judge proven on kept entries. |
| Q17 | no | Each task ran once, on Opus alone, with none held back, though the maintainers run the skill on Sonnet too. |
