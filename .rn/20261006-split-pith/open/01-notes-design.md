# Design points for pith, and for writ and rn on it

pith is cut out of writ as it works today; what changes is only what the split, rn's move onto pith
(A2), and #37 need.

Sources: pith's parts of `writ/README.md` and `writ/docs/design.md`, `writ/skills/pith/`,
`writ/agents/`, `writ/references/`, `writ/hooks/`, `rn/docs/design.md` ("The first user uses the work
before the user does"), `rn/agents/first-user.md`, `rn/references/essentials/report.md`, issues #35,
#37, #44.

## What moves to pith

- Everything pith uses today moves to `pith/` with `git mv`, unchanged but for its names: the skill
  (`/writ:pith` becomes `/pith:up`), its result-file form and check script, the first user and the
  hook that keeps it from git history and conversation records, the generator, the essentials files
  (`doc.md`, `readme.md`, `design.md`, `prompt.md`, `essentials.md`), `style.md`, and `lint/`.
  Tests and trials move to `dev/pith/`.

    Each of these is used by pith, and M4 gives each shared part one home; pith alone needs them all
    to check a document or a prompt and to write essentials (A1, M3).

- writ keeps `/writ:up` and the hook that runs its agents in the foreground. It starts
  `pith:generator`, and learns where pith's essentials files, `style.md`, and `lint/` are from a small
  skill of pith's, `pith:where`, that returns its own directory.

    A plugin cannot name a file inside another plugin; a skill's `${CLAUDE_PLUGIN_ROOT}` is its own
    plugin's directory. Tried on Claude Code 2.1.291: a plugin's skill called a dependency's skill
    that returned that directory, and read a file there.

- rn keeps its viewpoint files (`plan.md`, `design.md`, `task-result.md`, `deliverable.md`,
  `conductor.md`). Its own first user (`rn/agents/first-user.md`), `report.md`, and the hooks that
  keep that first user to its report (`first_user_reads.py`, `first_user_writes.py`) are removed.

## How writ and rn call pith

- writ and rn each declare pith as a dependency with `^0.1.0`, resolved against `pith--v<version>`
  tags (#35); until pith is released, the marketplace's copy is used, which satisfies it. rn declares
  pith directly, since it calls `/pith:up` itself.
- `/pith:up` runs with `context: fork` and `background: false`, so the caller waits for its result.

    In an interactive session every agent runs in the background, nested ones too (#44); a forked
    skill waits only with `background: false`. Tried on 2.1.291: a call through such a skill waited
    for the agent it started.

- rn calls `/pith:up` for every check it makes today (the plan, the design, a task result, the
  deliverable, a question, a proposal), handing: the work, its viewpoint file as the essentials, the
  receiver and purpose, with the paths the receiver holds when using the work (`steering.md`, the
  approved documents, feedback), `steering.md`'s goal and criteria as the aim, and its session's
  `open/{NN}-report-{about}.md` as the result file. rn's conductor checks each Good and More at its
  place and decides each More, as today.
- writ:up hands `/pith:up` its result file at `.writ/open/`, as today. Called directly, pith writes
  to `.pith/open/`, and an essentials file it writes for a kind with none to `.pith/essentials/`.

## The result file

- Its form does not change. The two open points of #35: no field is added now; the marks that end
  each More (`→ fixed:`, `→ let go:`, `→ to the user:`) belong to the commit that clears the file, as
  `.claude/rules/plugin.md` states, not to the file's form.

## A first user only where use shows something (#37)

- A check starts a first user once for the work, and once more for each fixed More of attractive
  quality, on that question alone. The caller settles the result file itself (a fixed More becomes
  its Good, a left one gets `Left because:`), and a hook of pith's runs the form check on every write
  to a result file.

    pith's third run existed only because only pith wrote the file, to keep its form.

## How writ's and rn's designs point to pith

- `writ/docs/design.md` and `rn/docs/design.md` link pith's design for how a check runs, and keep
  only what they hand pith and what they do with its result.

## Scenes for the verification document

- A1, pith alone (writ not installed): `/pith:up` on the pull-request review prompt with a hole
  (`dev/writ/trials/fixture/.github/prompts/pr-review.md`, aim as in the existing trial) gives a More
  at the hole with what happened in use as its evidence; on code with no essentials file
  (`cli/src/export.js` in the same fixture), it writes an essentials file for code first, then checks
  with it.
- A2: one `/writ:up` run and one rn check (a plan used against `plan.md`) each start
  `pith:first-user` and leave a result file that passes pith's form check.
- Machine checks: no first user, result-form script, or essentials file of pith's outside `pith/`
  (M4); each plugin's tests with every line run, and both `claude plugin validate --strict` runs (M5).
