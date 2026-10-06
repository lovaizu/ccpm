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

Make pith the one place where work is checked by having it used (the first user, the comparison with
the aim, the result file's form), while each caller keeps the viewpoints for its own kinds of work,
split out of writ into a plugin of its own (issue #35), with writ and rn both checking through it.
Today the same skeleton (a first user who does not know how the work was made, viewpoint files, Good
and More against the aim) lives in writ as pith and again inside rn, and the two grow apart; with one
home, an improvement to how work is checked is made once and reaches both, and anyone can check any
work by use without installing a plugin for writing documents.

# Acceptance criteria

## Attractive quality

- A1: Installing pith alone, without writ, gives `/pith:up`, which checks any work (a document, a
  prompt, code, tests) by a first user's use, first writing the viewpoints for a kind of work that has
  none, such as code or tests.
- A2: writ and rn both check their work through pith, so a change to how work is checked is made in
  pith once and reaches both. (The user's words: pith is the most basic function of an AI agent, and
  rn moves onto it in this session; the gain is put in the conductor's words, agreed in conversation.)

## Must-be quality

- M1: `/writ:up`'s golden paths (writing a new document, fixing an existing one) give no less than
  before.
- M2: An rn session's golden path (plan, design, tasks, deliverable, each checked before its sign-off)
  gives no less than before.
- M3: `/writ:pith` is removed, and whoever called it finds the same check as `/pith:up`, installed
  with writ.
- M4: No copy of pith's parts remains in writ or rn, and each part they share has exactly one home.
- M5: Each plugin keeps `.claude/rules/plugin.md`: tests that run every line in CI, trials, a README
  stating Python 3.9 or later, a CHANGELOG entry, both `claude plugin validate --strict` runs passing,
  and a listing in `.claude-plugin/marketplace.json` and the root `README.md`.

# Assumptions

- Fact, official docs (plugins/dependencies): a dependency installs with the plugin that declares it;
  a bare name follows the copy its marketplace provides, and a declared version range picks the
  highest `<plugin>--v<version>` tag in it; for a plugin at a relative path, as here, no matching tag
  falls back to the marketplace's copy.
- Fact, official docs: a dependency is described as "one whose MCP server or skill it calls", and a
  plugin's agents are named `<plugin>:<agent>`; no path variable is given for a dependency's directory.
- Fact, tried on Claude Code 2.1.291: a plugin's skill calls a dependency's skill with the Skill tool,
  and that skill starts its own plugin's agent and reads a file under its own root; the caller cannot
  name a file inside the dependency, since no path variable is given for it.
- Fact, official docs (skills, sub-agents) and tried on 2.1.291 with fork mode on: in an interactive
  session every agent the Agent tool starts runs in the background, nested ones too (#44); a forked
  skill with `background: false` makes the caller wait for its result, and the agent it started ran in
  the foreground. rn's own generator and writ agents stay outside pith, and #44 stays rn's own for
  them.
- Fact, checked in the repository: rn 0.9.0 depends on writ and has its README, design document, and
  verification document written by `writ:up`, which checks them with pith
  (`rn/references/conduct.md:107`, `writ/skills/up/SKILL.md:56`). Its own checks of the plan, a task
  result, and the deliverable use its own first user (`rn/agents/first-user.md`) and viewpoint files
  (`rn/references/essentials/`).
- Fact, decided by the user: moving rn onto pith is done in this session, not in a later one.

# Rules

- Releasing pith and writ (version bump, tags, GitHub Release) waits for an explicit release
  instruction, as `.claude/rules/plugin.md` says.
- Files are moved with `git mv`, so their history follows.
- A check through pith starts a first user only for the first use and for each fixed attractive-quality
  More, and whatever a script can decide, such as the result file's form, is checked by script
  (`.claude/rules/plugin.md` § Check); this closes #37, whose third pith run only settles the result
  file.

# Tasks

### [x] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- How writ and rn reach pith's skill, agents, and files through a dependency, and where the result
  file is written.
- Which of rn's parts move to pith, and which stay rn's own (such as its viewpoints for a plan, a
  design, and a task result).
- The two open points of the result file's form: whether a new field may be added, and whether the
  `→ fixed:` / `→ let go:` / `→ to the user:` marks are part of it.
- Whether rn depends on pith directly or through writ, which it keeps for its documents.
- Whether writ and rn declare a version range on pith or a bare name, given that a release waits for
  an instruction.
- How writ's and rn's designs (`writ/docs/design.md`, `rn/docs/design.md`) point to pith's.
