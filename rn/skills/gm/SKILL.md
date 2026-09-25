---
name: gm
description: Ask for changes to what an rn session stopped for — the plan, a design choice, or the finished work — from the feedback given, or from the review comments on the pull request; record it and stop. It commits and pushes, so run it only on an explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Good, more

The user wants more from what the session stopped for. Record their feedback whole, in their words, so
the revision answers what they asked, not a summary of it, and stop.

Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The feedback is `$ARGUMENTS`;
without it, the unresolved review threads on the pull request, each with its location and URL. Only
GraphQL tells which are resolved:

```
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{isResolved path line comments(first:20){nodes{url body}}}}}}}' -F o={owner} -F r={repo} -F n={number}
```

Add it to `Feedback`, commit, and push. Then say, in the user's language:

```
● Recorded: {n} points on {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
```
