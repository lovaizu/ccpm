# Design points for pith, and for writ and rn on it

Sources to draw from: pith's parts of `writ/README.md` and `writ/docs/design.md` ("Lay the fact of
use…", "Write essentials…", "The result file…", the roles principles), `writ/skills/pith/`,
`writ/agents/first-user.md`, `rn/docs/design.md` ("The first user uses the work before the user
does"), `rn/agents/first-user.md`, `rn/references/essentials/report.md`, issues #35, #37, #44.

## How writ and rn reach pith

- writ and rn each declare pith as a dependency and call it only through its skill, `pith:up`, with
  the Skill tool. pith's skill reaches its own agents and files through its own
  `${CLAUDE_PLUGIN_ROOT}`; no caller reads a file inside pith.

    The official docs give no path variable for a dependency's directory. Tried on Claude Code
    2.1.291: a skill of plugin A called plugin B's skill, which started B's agent and read a file under
    B's root; B was installed only as A's dependency.

- `pith:up` runs with `context: fork` and `background: false`, so the caller gets its result in the
  same turn and goes on only after it.

    In an interactive session every agent the Agent tool starts runs in the background, nested ones
    too, and a forked skill also runs in the background unless it sets `background: false` (official
    docs, skills and sub-agents). Tried on 2.1.291 with fork mode on: a top-level agent came back at
    once as launched in the background (the case of #44), while a call through a forked skill with
    `background: false` waited for the agent it started, which ran in the foreground. rn's checks go
    through pith, so they wait; rn's own generator and its `writ` agents stay outside pith, and #44
    stays rn's for them.

- Both writ and rn declare pith with a version range on the 0.x line (`^0.1.0`), resolved against
  `pith--v<version>` tags, as #35 asks. Until pith is released, no tag exists and the marketplace's
  copy is used, which satisfies the range.

    A breaking pith 0.2 then reaches writ and rn only once they widen the range after trying it.

- rn depends on pith directly, besides writ, since it calls `pith:up` itself.

## What lives where

- pith holds everything about checking a work by use: the skill (check a work; make an essentials
  file), the result file's form and the script that checks it, the first user and the hook that keeps
  it from how the work was made, its own generator for essentials files, and `essentials.md`.
- What a first user's report must give (`rn/references/essentials/report.md`) moves into pith's first
  user, since it is about checking, not about rn's work.
- Each caller keeps the viewpoints for its own kinds of work, as the goal says: writ keeps `doc.md`,
  `readme.md`, `design.md`, `prompt.md`; rn keeps `plan.md`, `design.md`, `task-result.md`,
  `deliverable.md`, `conductor.md`. Each hands their paths to pith.

    Each caller's generator aims for its viewpoints as the form to write to, and cannot reach a file
    inside pith.

- pith alone, given a kind of work with no essentials file, writes one first and then checks with it
  (A1). Called directly, it writes it to `.pith/essentials/<kind>.md` in the repository, so the next
  check of that kind reuses it.
- writ's generator writes documents only; pith's own generator writes essentials files.
- Removed: `/writ:pith`, `writ/agents/first-user.md`, writ's first-user hook, `rn/agents/first-user.md`
  and rn's hooks that keep the first user to its report (`first_user_reads.py`,
  `first_user_writes.py`). pith's hook covers what they held: git history, conversation records, and
  earlier reports and notes in any `open/`.
- Tests and trials move with their parts: `dev/pith/tests/`, `dev/pith/trials/`.

## What pith is handed, and what it returns

- Besides the work, its receiver and purpose, the aim, and the essentials files, pith takes the paths
  of what the receiver has in hand when using the work, and hands those to the first user. The aim
  itself still goes only to pith's conductor.

    rn's viewpoints are answered by a receiver who holds the goal and criteria, such as the user at a
    sign-off tracing each criterion through the design; without them rn would get less than today
    (M2).

- pith's conductor gives each Good and More against the written aim, naming the criterion it bears on
  when the aim gives criteria IDs. The caller checks each at its place, and decides fix, let go, or
  ask the user.

    For rn the aim is `steering.md`, which already holds everything the user decided; rn's proposals
    name a criterion ID on each Good and More.

- `/pith:up` checks with the essentials files the caller names, or else the one for the work's kind
  in the repository's `.pith/essentials/`, written first when there is none. It never picks up
  another plugin's essentials, writ installed or not: writ's essentials are reached by `/writ:up`,
  which names them to pith.

    pith cannot name a file inside another plugin, as no caller can name one inside pith.

- The README shows a few lines of a result file, so its reader sees which fixed More goes back to
  pith for a recheck (one of attractive quality) and which they settle in the file themselves.

- The result file is written where the caller names it: rn its session's
  `open/{NN}-report-{about}.md`, writ `.writ/open/`, and `.pith/open/` when called directly.

## The result file's form (the two open points of #35)

- A field may be added only as optional, leaving every existing label as it is. The first is the
  criterion ID after `Good` or `More` (`- Good A1:`).

    rn reads the file now; an optional field keeps every reader of the older form working.

- The marks that end each More when a file is cleared (`→ fixed:`, `→ let go:`, `→ to the user:`)
  are not part of pith's form: they belong to the commit that clears it, as `.claude/rules/plugin.md`
  states for every plugin.

## Running a first user only where use shows something (#37)

- In one check, pith starts a first user once for the work, and once more for each fixed More of
  attractive quality, on that question alone. Nothing else starts one.
- The caller settles the result file itself (fixed → its Good now, left → `Left because:`), and pith's
  hook runs the form check on every write to a result file.

    The only reason for pith's third run in #37 was that only pith wrote the file, to keep its form;
    a hook keeps the form however the file is written.

## How the other designs point to pith

- `writ/docs/design.md` and `rn/docs/design.md` link pith's design for how a check runs, and say only
  what they hand pith and what they do with its result.

## Scenes for the verification document

- A1, pith alone (writ not installed): `/pith:up` on the pull-request review prompt with a hole
  (`dev/writ/trials/fixture/.github/prompts/pr-review.md`, the aim as in the existing trial) gives a
  More pointing at the hole with what happened in use as its evidence; on code with no essentials
  file (`cli/src/export.js` in the same fixture, with its purpose and aim), it writes an essentials
  file for code first and then checks with it.
- A2: one `/writ:up` run and one rn check (a plan used against `plan.md`) each start
  `pith:first-user` and leave a result file that passes pith's form check.
- Machine checks: no first user, result-form script, or `essentials.md` outside `pith/` (M4); each
  plugin's tests with every line run, and both `claude plugin validate --strict` runs (M5).
