---
name: on
description: Start an rn work session — draw the goal out with the user one point at a time, write the plan up to the first decision as steering.md on a draft PR, have it evaluated, and stop for the user's sign-off. Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

Turns what the user wants into a plan they agree with, on record in git, so the work can run
without them until a decision is theirs. Runs under the conductor's role:
`${CLAUDE_PLUGIN_ROOT}/references/conductor.md`.

## Steps

1. **Draw the goal out of the user.** Start from `$ARGUMENTS` or the message, and from what the
   repository shows. Tell the user your reading one point at a time — what they want, why they want
   it, how they would know it is done, the approach — and move to the next point only when they
   agree with this one. Ask in plain words, not a list of options, and look up what the repository
   can answer instead of asking. Go on until the aim they had not put into words and the approach
   are both agreed.
2. **Name the session.** `.rn/{yyyymmdd}-{slug}/steering.md`, the slug a short kebab-case name for
   what the work produces. Use a name the user gave; otherwise propose one with the plan.
3. **Write the plan** from the template in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, reading
   What each part is for, and check that each task's Purpose traces to an Acceptance criterion and
   the criteria to the Goal as agreed. `rn` is `version` in
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; `issue` is the issue the user named, if any.
4. **Put it on record.** Uncommitted changes in the tree are the user's → ask whether to set them
   aside first, so they do not land in the session. Create the session's branch from the default
   branch. Commit `chore: start session — {slug}`, push, and open a draft PR whose body is
   `See [steering](https://github.com/{owner}/{repo}/blob/{branch}/.rn/{yyyymmdd}-{slug}/steering.md).`
   Write its URL in the `pr` field, commit and push. If a push or the PR fails, say so and go on in
   the conversation.
5. **Run the session to its first decision** as in Running the session to its next decision in
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md` — task #1, the Plan sign-off.
