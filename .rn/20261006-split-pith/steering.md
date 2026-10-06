---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/40
status: running
artifact-language: English
conversation-language: Japanese
readme: pith/README.md
design: pith/docs/design.md
verification: pith/docs/verification.md
---

# Goal

Make pith the one place where work is checked by having it used, split out of writ into a plugin of
its own (issue #35), with writ and rn both checking through it. Today the same skeleton (a first user
who does not know how the work was made, viewpoint files, Good and More against the aim) lives in
writ as pith and again inside rn, and the two grow apart; with one home, an improvement to how work
is checked is made once and reaches both, and anyone can check any work by use without installing a
plugin for writing documents.

# Acceptance criteria

## Attractive quality

- A1: Installing pith alone, without writ, gives `/pith:up`, which checks any work (a document, a
  prompt, code, tests) by a first user's use and writes the result file.
- A2: writ and rn both check their work through pith, so a change to how work is checked is made in
  pith once and reaches both.

## Must-be quality

- M1: `/writ:up`'s golden paths (writing a new document, fixing an existing one) give no less than
  before.
- M2: An rn session's golden path (plan, design, tasks, deliverable, each checked before its sign-off)
  gives no less than before.
- M3: No copy of pith's parts remains in writ or rn, and each part they share has exactly one home.
- M4: Each plugin keeps `.claude/rules/plugin.md`: tests that run every line in CI, trials, a README
  stating Python 3.9 or later, a CHANGELOG entry, both `claude plugin validate --strict` runs passing,
  and a listing in `.claude-plugin/marketplace.json` and the root `README.md`.

# Assumptions

- Fact, official docs: `plugin.json` `dependencies` resolve a bare name against the same marketplace,
  install automatically, and pick the highest `<plugin>--v<version>` tag in the range; with no
  matching tag, the marketplace's current copy is used.
- Assumption: a plugin can call a dependency's skill and start its agents, and reach its files; the
  official docs give no path variable for a dependency's directory and do not document calling
  another plugin's skill or agent.
- Fact, checked in the repository: rn 0.9.0 does not call pith; it checks with its own first user
  (`rn/agents/first-user.md`) and viewpoint files (`rn/references/essentials/`), and depends on writ.
- Fact, decided by the user: moving rn onto pith is done in this session, not in a later one.

# Rules

- Releasing pith and writ (version bump, tags, GitHub Release) waits for an explicit release
  instruction, as `.claude/rules/plugin.md` says.
- Files are moved with `git mv`, so their history follows.

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- How writ and rn reach pith's skill, agents, and files through a dependency, and where the result
  file is written.
- Which of rn's parts move to pith, and which stay rn's own (such as its viewpoints for a plan, a
  design, and a task result).
- The two open points of the result file's form: whether a new field may be added, and whether the
  `→ fixed:` / `→ let go:` / `→ to the user:` marks are part of it.
- How writ's and rn's designs (`writ/docs/design.md`, `rn/docs/design.md`) point to pith's.
