# Review, sound in its parts but tried late

A plugin that reviews a pull request with a reader for each concern. Its maker placed and bounded
its components well, and left its cases, its footprint, and its install to the end. It's a kept
case of the [plugin best practice](../best-practice.md): a deliverable with the verdict on each question that
someone who knows the user's work gives, so that an evaluator proves itself on it before anyone
trusts its verdicts.

## What the README promises

- `/review:pr <number>` reads the pull request's diff and reports findings on security, tests, and
  naming. Each finding points at its file and line.
- `/review:post` posts the findings the user kept as a review on the pull request.
- A review stopped halfway goes on from the concerns already read.
- It needs git and Python 3.9 or later.

## Files

`.claude-plugin/plugin.json`:

```json
{
  "name": "review",
  "version": "2.3.1",
  "description": "Reviews a pull request for security, tests, and naming, with a reader for each.",
  "author": { "name": "Example Team" },
  "repository": "https://github.com/example/review",
  "license": "Apache-2.0"
}
```

`skills/pr/SKILL.md` runs `scripts/diff.py`, which writes the diff to the system's temporary folder,
starts a reader for each concern, shows the user their findings, and has `diff.py` remove the diff
once the readers end. `skills/post/SKILL.md` carries
`disable-model-invocation: true`, and posts only the findings the user kept.

`agents/security.md`, `agents/tests.md`, and `agents/naming.md` each carry
`tools: Read, Grep, Glob` and a description like this one, of about 600 characters:

```markdown
---
description: Use proactively. An expert reviewer of security who reads every changed file ... (about 600 characters)
tools: Read, Grep, Glob
---
```

`hooks/hooks.json` holds one `SubagentStop` hook, which holds a reader's end until its findings
name a file and a line. It has no `onFailure`.

`scripts/diff.py` runs `gh pr diff`.

`evals/` holds three cases, each a request to review a pull request, each run once with the plugin.

`CHANGELOG.md`:

```markdown
## [2.3.1] - 2026-09-14

### Fixed

- Findings on a renamed file now point at its new path, so the line you open is the one meant.
```

## How the maintainer worked

1. The maintainer built the scripts, the skills, and the readers, and tried them on their own
   pull requests.
2. Once the plugin worked, they wrote three cases from the requests it handled well, and ran each
   once with the plugin.
3. They released from their own machine, where `gh` held their sign-in.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | no | The cases came after the plugin, each runs once and only with it, and none is a request the plugin must pass over. |
| Q2 | yes | A script gets the diff, a hook holds the form of a reader's end, and each concern has a reader of its own, as each reads many files to report a few lines. |
| Q3 | yes | Posting is the user's: `post` takes only their call, and posts only what they kept. |
| Q4 | yes | Each reader can only read, and `post` acts only on the user's call. |
| Q5 | no | The `SubagentStop` hook has no `onFailure`, so a reader ends unchecked when its script fails. |
| Q6 | no | Three descriptions of about 600 characters stay in every session's context, and "use proactively" sends Claude to the readers on any change. |
| Q7 | yes | The diff lives in the system's temporary folder until the readers end, and the plugin keeps nothing else. |
| Q8 | no | The findings live only in the conversation, so a stopped review reads every concern again. |
| Q9 | no | `diff.py` needs `gh`, signed in, which the README never names, and no install on a fresh machine came before the release. |
| Q10 | yes | It needs no other plugin and copies no code. |
| Q11 | yes | A fix raised the patch part, with a line that says what the user gains. |
| Q12 | no | A user without `gh` meets an error at the first step, and a review stopped halfway costs a full rerun. |
