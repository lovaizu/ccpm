# Deploy, a fail on every question

A plugin that builds a service and deploys it, built the way a maker builds one in their own
session and ships it as it stands. It's a kept case of the [plugin best
practice](../best-practice.md): a deliverable with the verdict on each question that someone who
knows the user's work gives, so that an evaluator proves itself on it before anyone trusts its
verdicts.

## What the README promises

- `/deploy:ship` runs the tests, builds the service, and deploys it to staging.
- It deploys to production only once the user says so.
- A deploy stopped halfway goes on from its last step when the user calls it again.

## Files

`.claude-plugin/plugin.json`:

```json
{
  "name": "deploy",
  "version": "1.0.0",
  "dependencies": ["secrets"]
}
```

The marketplace entry holds the plugin's only description, which differs from the README's.

`skills/ship/SKILL.md`:

```markdown
---
description: A complete, end-to-end deployment assistant for every stage of shipping ... (900 characters)
---

Have the deployer agent run the tests and build. If the tests pass, deploy to production.
```

`agents/deployer.md`:

```markdown
---
name: deployer
description: Deploys services. Use proactively whenever code changes.
---

Never run `rm -rf`. Ask the user which environment to deploy to. Keep track of the steps done.
Read `${CLAUDE_PLUGIN_ROOT}/../shared/env.sh` for the settings.
```

`hooks/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "sh \"${CLAUDE_PLUGIN_ROOT}/scripts/check.sh\"" }] }
    ],
    "PostToolUse": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/lint.js\"" }] }
    ]
  }
}
```

`scripts/check.sh` exits 1 to deny a command that deletes a folder. `scripts/vault.py` is a copy of
the `secrets` plugin's own module. The deployer writes its log to
`${CLAUDE_PLUGIN_ROOT}/logs/deploy.log`.

The plugin has no `evals/`.

`CHANGELOG.md`:

```markdown
## 1.0.0

- Updated stuff
- Merge branch 'main' into fix-retry
```

## How the maintainer worked

1. The maintainer wrote each file in their own session and tried `/deploy:ship` there twice.
2. They pushed each later change to the marketplace with `version` left at 1.0.0.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | no | No case of real use exists, and no run without the plugin shows what it adds. |
| Q2 | no | The rule against `rm -rf` rests on the deployer's prompt, and the steps it keeps track of rest on its attention, where a hook and a script would hold them. |
| Q3 | no | The skill deploys to production on its own judgment once the tests pass, and the deployer, a subagent, has no `AskUserQuestion` to ask the user which environment. |
| Q4 | no | The deployer names no `tools`, so it inherits every tool of the session. |
| Q5 | no | The hook denies by exit code 1, a non-blocking error, and has no `onFailure`, so the command it should stop runs. |
| Q6 | no | A description of 900 characters and "use proactively" stay in every session's context, and `lint.js` starts on every tool call of every session. |
| Q7 | no | The log in `${CLAUDE_PLUGIN_ROOT}` goes with the next update. |
| Q8 | no | The steps done live only in the deployer's conversation, so a new session starts the deploy over. |
| Q9 | no | `../shared/env.sh` lies outside the plugin, so an install doesn't copy it, and the README never names Node.js, which `lint.js` needs. |
| Q10 | no | `secrets` carries no range of versions, and `vault.py` copies its code. |
| Q11 | no | Each change reached the marketplace under 1.0.0, so users who update get none of them, and the changelog lists commits. |
| Q12 | no | A user on a fresh machine meets a deploy that fails on the missing settings, or reaches production unasked. |
