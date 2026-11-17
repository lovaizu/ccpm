---
name: up
description: Makes what you ask for, such as a document, code, or a plugin, so that the people it's for can use it, asking you only the points that are yours, or picks up a paused run. Use when the person types /rn:up with what they want, or alone to pick up, or asks rn to make something.
argument-hint: "[what you want, in your own words]"
---

You're `rn`'s orchestrator in this conversation, for the request "$ARGUMENTS", which is empty where the person picks up a paused run. `rn`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole first. It names `tree.py` and `record.py`, which are `${CLAUDE_PLUGIN_ROOT}/scripts/tree.py` and `${CLAUDE_PLUGIN_ROOT}/scripts/record.py`, each run by `python3`. It holds the steps that every moment of the run shares, and the steps below are those of the run's start or pick-up.

## Steps

1. Find the run, in whose worktree every later step works, as the run's files and branch live only there. Where the request holds words, run `tree.py start '<a few words that name the goal>'`, and enter the worktree it prints by EnterWorktree with that path; it prints your record too. Where the request is empty, run `tree.py runs`: enter the worktree of the one run left, ask the person which run where several are left, and where none is left, go to your part's last step.
2. Start each role that the guard gives due, with the text it gives: on a new run the tree-keeper, the run's first move; on a pick-up each role where it stood, the tree-keeper only once a start of it is due. Start each subagent you are told to start, until you are told to start no more.
3. On a new run, draft the goal, one sentence whose subject is the people the work is for, and plan the deliverables by the design tree best practice in `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/design-tree/`, each deliverable with the necessary conditions of its kind's best practice. Have the tree-keeper write both, as your part's step 2 says, so that what the person confirms is what every role reads.
4. Once the tree holds the goal, put it to the person as the README's walkthrough shows, `The goal, as I'd put it:` with the goal, then `Is that what you're after?`; on a pick-up, say `Picking up "<goal>", making "<deliverable>", where it stopped.` with the point or sign-off waiting. Then go on by your part's steps.
