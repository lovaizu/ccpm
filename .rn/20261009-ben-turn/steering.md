---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/57
status: running
artifact-language: English; the documents under review are Japanese until they are put into English before merge
conversation-language: Japanese
readme: ben/README.md, turn/README.md
design: dev/ben/design.md, dev/turn/design.md
verification: ben's scenes
---

# Goal

A builder delivers every plugin the same way, from its purpose to its release, following best
practice and meeting the purpose simply. ben holds that way and checks that users get what each
README promises; turn carries one task for a plugin that has AI make something. pith, writ and rn are
rebuilt on them afterwards (#52, #53, #54).

# Acceptance criteria

## Attractive quality

- A1: A builder delivers a plugin with ben alone: its README tells them everything from the purpose
  to the release, and Claude Code, with ben installed, works the same way with no rule file in the
  repository.
- A2: A builder judges a change by what happened to the user, from ben's result alone.
- A3: A plugin hands one task to turn and decides its next move from the returned record without
  reading the work.

## Must-be quality

- M1: Each part follows official best practice or says why it does not, and keeps nothing its
  purpose does not need.
- M2: Each document has been used by a first user who does not know the discussion, and every More
  is settled.
- M3: `claude plugin validate --strict` passes for each plugin and for the marketplace, and CI passes.

# Assumptions

- Fact, decided by the user: the scope's people and roles. The user installs a plugin from the
  marketplace and uses it. The builder decides the purpose, approves the README and design, merges,
  and decides what ships. Claude Code does the work as the builder decided and follows ben's way. The
  marketplace holds several plugins with their list, tests, scenes and CI. A plugin is what is
  delivered, its folder copied whole to the user. ben holds the way to deliver and the checking tool.
  turn is what a plugin that has AI make something stands on. writ and pith write documents and have
  a first user check them. rn records and carries the builder's work across sessions. GitHub holds
  issues, pull requests, CI, tags and releases. Official docs and plugins are the source of best
  practice.
- Fact, decided by the user: ben's README holds everything to deliver a plugin: a marketplace of
  several plugins, test files kept out of the plugin, how a plugin is built, how it is tested and
  checked and with what, what is needed, and how it is released. ben reaches Claude Code through its
  own skill, and `.claude/rules/plugin.md` goes.
- Fact, decided by the user: a scene that needs GitHub runs in a private practice repository, which
  ben asks the builder for and records in the scene; here it is `lovaizu/rn-try`.
- Fact, decided by the user: what the user read is counted in characters.
- Fact, decided by the user: turn's maker, first user and learner are agents apart from the
  conductor, so no one checks their own work and each stays on its one piece of work without
  drifting.
- Fact, decided by the user: the name ben; `BEN_PYTHON` or `~/.ben/bin/python`; `/ben:check <plugin>`
  writes a scene and `/ben:check <scene file>` checks again; a scene lives in the checked plugin's
  git repository.
- Fact, checked in the official docs: `claude plugin eval` runs a single turn, has no user answering
  the plugin's questions, and does not compare with an earlier version, so ben does not run on it.
- Fact, decided by the user: rn is disabled while it is rebuilt.

# Rules

- The documents stay in Japanese while under review and are put into English before merge.
- Implementation comes only from the approved documents; a shortfall is traced through the record to
  its cause and the cause is fixed.

# Tasks

### [x] #1: Plan sign-off
### [ ] #3: ben holds plugin delivery

Purpose: ben's README and design hold everything to deliver a plugin, laid out from the scope's
people, roles and dependencies, so nothing else is needed.

Serves: A1, M1

Completion criteria:

- Attractive quality: ben's README covers each item the user listed, and the design gives the scope's
  people, roles and dependencies with ben's skill for Claude Code.
- Must-be quality: `.claude/rules/plugin.md` is gone and nothing it held is lost.

### [ ] #4: First users read the four documents

Purpose: each document is read as its reader would, by someone who does not know the discussion. writ is being rebuilt and is
not run; its essentials files in `writ/references/essentials/` are handed to a first-user agent
that does not know the discussion, and the conductor checks each Good and More in the document.

Serves: M2

Completion criteria:

- Attractive quality: every question of the essentials files has a Good or a settled More.
- Must-be quality: the edits made after the first reading are covered.

### [ ] #2: Design sign-off

# Not yet specified

- The minimal implementation of ben and turn from the approved documents, checked with ben.
- English before merge, registration in the marketplace and the root README, and release.
