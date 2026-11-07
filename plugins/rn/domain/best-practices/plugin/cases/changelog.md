# Changelog, a pass on every question

A plugin that drafts the next entry of a project's changelog. It's a kept case of the [plugin best
practice](../best-practice.md): a deliverable with the verdict on each question that someone who
knows the user's work gives, so that an evaluator proves itself on it before anyone trusts its
verdicts.

## What the README promises

- `/changelog:draft` writes the `Unreleased` section of the project's `CHANGELOG.md` from the
  commits since the last tag, a line each for what users notice, grouped as Keep a Changelog
  groups them.
- It never commits or pushes. The user reads the draft, edits it, and commits it themselves.
- Run again, it adds only the commits that the section doesn't hold yet.
- It needs git and Python 3.9 or later, run as `python3`.

## Files

`.claude-plugin/plugin.json`:

```json
{
  "name": "changelog",
  "version": "1.2.0",
  "description": "Drafts the Unreleased section of CHANGELOG.md from the commits since the last tag.",
  "author": { "name": "Example Team" },
  "homepage": "https://example.com/changelog",
  "repository": "https://github.com/example/changelog",
  "license": "MIT"
}
```

The marketplace entry holds only `name` and `source`, so the description lives in one place.

`skills/draft/SKILL.md`:

```markdown
---
description: Drafts the Unreleased section of CHANGELOG.md from the commits since the last tag. Use when the user asks for release notes or a changelog entry.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/commits.py *)
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/no_commit.py\""
          onFailure: block
---

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/commits.py` and write from what it prints ...
```

`scripts/commits.py` prints, as JSON, each commit since the last tag that the `Unreleased` section
doesn't name yet, and exits 2 with what to install where git or a tag is missing.
`scripts/no_commit.py` reads the call on standard input and denies `git commit` and `git push` by
exit code 2. Both use Python's standard library alone.

The plugin has no agents, and no `hooks/hooks.json`.

`evals/`:

| Case | Request | Graders |
| --- | --- | --- |
| `notes-since-tag` | "Write release notes for what changed since v1.1." | the `Unreleased` section names each fix commit, and the skill ran |
| `adds-only-new` | the same, with a section that already holds two of the commits | those two appear once |
| `no-commit` | "Draft the changelog and commit it." | no `git commit` ran, and the reply asks the user to commit |
| `unrelated` | "Fix the typo in README.md." | the skill didn't run |

`CHANGELOG.md`:

```markdown
## [1.2.0] - 2026-10-02

### Added

- A second run adds only the commits the draft doesn't hold yet, so your edits stay.
```

## How the maintainer worked

1. The maintainer wrote the four cases before any file of the plugin, and ran each three times
   without it. Claude wrote a summary of every commit, merges among them, and committed once.
2. The maintainer then wrote `commits.py` and its tests, the skill, and the hook, and ran each case
   three times with the plugin and three without. Each case passed with it.
3. Before the release, the maintainer added the marketplace from a local path in a container that
   held only git and Python 3.9, installed the plugin, ran `notes-since-tag`, and ran `claude plugin
   validate . --strict`.
4. Three users who took no part in the making used it on their own projects, and kept the drafts
   after their edits.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | Four cases came before the files, each run with and without the plugin, `unrelated` among them. |
| Q2 | yes | The script finds the commits, a hook holds the rule against committing, and the skill writes the lines, which needs judgment. No subagent stands where nothing needs a context of its own. |
| Q3 | yes | The commit stays the user's: the hook stops it, and the reply asks the user to make it. |
| Q4 | yes | The skill may run only `commits.py` without asking, and the hook reads only the call it's given. |
| Q5 | yes | The hook carries `onFailure: block` and denies by exit code 2. |
| Q6 | yes | One short description, and the hook registers only once the skill runs. |
| Q7 | yes | It writes only `CHANGELOG.md` in the project, which the user asked for, and keeps nothing else. |
| Q8 | yes | A second run reads the section it wrote and adds only what's new. |
| Q9 | yes | It ran from a fresh install on a machine with only what the README names. |
| Q10 | yes | It needs no other plugin and copies no code. |
| Q11 | yes | The version rose by a minor part for an added behavior, with a line that says what the user gains. |
| Q12 | yes | Users who took no part in the making kept its drafts. |
