# Where the design stood when paused

## Agreed with the user in this talk

- rn 0.9.0 does harm: the README's steps are not given in use (the user is not heard, must watch
  over the work, cannot decide from a proposal, waits hours in the design stage). It came from
  adding a step or a hook for each fault, and from never using it as the README's story runs.
- Judge from the purpose and what rn should be, never patch a remark. The sources to judge from are
  `rn/README.md` as on `main`, the viewpoints (`rn/references/essentials/`), and
  `.claude/rules/plugin.md`, with the user's earlier decisions (steering.md Facts; rn names no
  model). The design document is written from these, not a source.
- Three axes: instruct by purpose and intent, not procedure (#31's aim, which 0.9.0 missed); a first
  user only for what use shows (a task result, the deliverable, a document read as its reader would);
  attractive quality first, must-be quality after, fixed where it stands in the way on the golden
  path.
- Rebuild, not fix: discard `rn/references/conduct.md` and the hooks, and write them again small
  from the sources. Keep the README, the record's form (`rn/references/steering.md`), the agent
  definitions, and the viewpoints, with `report.md` dropped and the conductor's Question and
  Proposal sections rewritten as the form a maker writes to.
- Decided by the user (in `/rn:dn`): rebuild writ and pith together with rn; pith becomes a plugin
  of its own; release the three together. The sessions on PR #40 (split pith) and PR #42 (#36) were
  told by the user to stop; their work is material for this rebuild.
- Checked by running the README's story end to end in one session on the practice repository,
  beside rn 0.9.0's run of the same request, step by step.
- The plan (steering.md) goes back through the Plan sign-off: its goal still reads as closing issues
  one by one, and A5 reads as must-be quality.
- `01-notes-design.md` (the design worked out from the README's steps) stands as the first draft;
  `03-report-readme.md` and `05-report-design.md` are pith's checks of the README and the design
  document as they are. The writ rewrites of the README and the design document made from the
  earlier per-issue notes were discarded, uncommitted.

## Open: whether to go on with rn

- The user asked whether this work can go on without rn, since rn 0.9.0's own faults stop it: its
  hooks blocked messages to the other two sessions (#43), send the conductor on at every wait
  (#44), and split every commit and push.
- Answer to give: yes. rn's hooks are those of the installed `rn@ccpm` plugin and act wherever
  `.rn/` exists, so disabling the plugin while rebuilding (`/plugin disable rn@ccpm`) lets the work
  go on as plain Claude Code on this branch and PR #50; the new rn is tried with
  `claude --plugin-dir` on the practice repository. Still to decide with the user: whether to do
  so, and where the plan is kept meanwhile (this steering.md as a plain document is the default).
