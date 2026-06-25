# rn — design notes

The intent behind the rn procedures. **Not read at runtime** — the skill and reference files are pure
procedure; this file is for whoever maintains them and needs to judge whether a step is still right
when requirements change. One note per step or decision, keyed to the procedure it explains.

## dn (`/rn:dn` — suspend)

- **Step 1 fallback searches commit history** — a suspend may run in a fresh conversation that never
  saw the path; the `Status: paused` marker is what distinguishes a suspended session from a finished
  one.
- **Step 3 puts resume context in `Notes`** — a suspend has to survive a new conversation and a
  context compaction; the next `/rn:up` resumes from `Notes` alone, so anything not written there is
  lost.
- **Step 4 forbids `complete task #` in the message** — that exact substring is the single
  task-completion marker `/rn:up` matches in `git log`; a suspend is not a completion, so the marker
  must not appear on a suspend commit. (`wip:` prefix flags an unfinished task for the reader.)
- **Step 5 never deletes an untracked file** — a misclassified delete destroys user work
  irreversibly. Gitignore is reversible and enough to get the tree clean, so deletion is only ever the
  user's explicit choice.
- **Step 5 gitignores recurring artifacts instead of removing them** — a `.gitignore` rule hides the
  path from `git status` and stops it re-dirtying the tree on a later run, without touching the file.
- **Step 5 records the literal `git status --porcelain` string** — step 7 decides "is this path
  already deferred?" by matching against `Notes`; a paraphrase would not match.
- **Steps 5–7 bound the gitignore retry per path, and persist the marker in `Notes`** — `/rn:dn`
  exists to cross the context boundary, so the "retry a wrong rule at most once" bound must hold from
  persisted state, not agent memory; otherwise a compaction mid-suspend could let the verify loop
  re-fix the same path forever. Each path ends either gitignored-away or recorded-deferred, so the
  flow always terminates.
- **Step 6 makes one commit per pass and never force-pushes** — keeps the branch history clean and
  recoverable, and the user reviews it on the PR.
- **Step 7 reaches a terminal state, never wedges** — the user runs `/rn:dn` precisely to stop and
  leave; an unresolved path is recorded and the suspend completes rather than blocking on the
  departing user.
- **Step 8 reports the last push's status** — step 6 may run twice; a stale "unpushed" warning from
  an earlier pass would mislead the user into thinking safe work is at risk, or vice versa.
