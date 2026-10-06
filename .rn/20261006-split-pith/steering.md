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

Split pith out of writ into a plugin of its own (issue #35), so that anyone, rn included, can check
any work by having a first user use it, without installing a plugin for writing documents. writ keeps
checking every document it writes, now by depending on pith instead of carrying it. Each part writ
and pith share gets one home, and the two undecided points of the result file's form are decided
before a caller outside writ reads it.

# Acceptance criteria

## Attractive quality

- A1: Installing pith alone, without writ, gives `/pith:up`, which checks any work (a document, a
  prompt, code, tests) by a first user's use and writes the result file.
- A2: A caller outside writ, such as rn, can call pith without depending on writ, knowing from pith's
  design what to hand it and what it gets back, including a result file whose form is settled.

## Must-be quality

- M1: Installing writ also installs pith, and `/writ:up` still checks every document it writes,
  through pith, its golden paths (writing a new document, fixing an existing one) giving no less than
  before.
- M2: writ carries no copy of pith, and every part the two share (the generator, the essentials for
  documents and prompts) has exactly one home.
- M3: Each plugin keeps `.claude/rules/plugin.md`: tests that run every line in CI, trials, a README
  stating Python 3.9 or later, a CHANGELOG entry, both `claude plugin validate --strict` runs passing,
  and a listing in `.claude-plugin/marketplace.json` and the root `README.md`.

# Assumptions

- Fact, official docs: `plugin.json` `dependencies` resolve a bare name against the same marketplace,
  install automatically, and pick the highest `<plugin>--v<version>` tag in the range; with no
  matching tag, the marketplace's current copy is used.
- Assumption: a plugin can call a dependency's skill and start its agents, and reach its files; the
  official docs give no path variable for a dependency's directory and do not document calling
  another plugin's skill or agent.
- Fact, checked in the repository: rn 0.9.0 does not call pith; it has its own first user
  (`rn/agents/first-user.md`).

# Rules

- Releasing pith and writ (version bump, tags, GitHub Release) waits for an explicit release
  instruction, as `.claude/rules/plugin.md` says.
- Files are moved with `git mv`, so their history follows.

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- How writ reaches pith's skill, agents, and files through the dependency, and where the result file
  is written.
- The two open points of the result file's form: whether a new field may be added, and whether the
  `→ fixed:` / `→ let go:` / `→ to the user:` marks are part of it.
- How writ's design (`writ/docs/design.md`) points to pith's.
