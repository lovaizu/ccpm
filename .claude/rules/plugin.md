# Plugin authoring rules (ccpm)

Source: based on facts confirmed in the official docs (plugins-reference / plugin-marketplaces / skills at code.claude.com/docs).

## Version number

- **Write `version` in exactly one place: `plugin.json`.** Do not put `version` in `marketplace.json`.
  - Resolution order is `plugin.json` → marketplace entry → git commit SHA. **When both are set, `plugin.json` wins**, so a `version` in the marketplace entry is redundant and meaningless.
  - The top-level `version` in the marketplace is "manifest metadata" and is not used to detect updates for users.
- **Always set `version` in `plugin.json`** (semver, e.g. `0.1.0`).
  - `claude plugin validate --strict` warns and then fails when `version` is unset.
- **What it means (from the user's side):** pinning a version means users receive an update **only when you bump it**.
- **Bump only on an explicit release instruction.** There is no automatic bump — not even on merge to `main`. Without an instruction, user-facing changes wait under CHANGELOG's `## [Unreleased]` and `plugin.json` stays put; the version rises only when the user says to cut a release.
  - Omitting it makes every commit a new release (the commit-SHA strategy, suited to active development), but to pass `--strict` this repo's policy is to keep `version` in `plugin.json`.

### How much to bump (semver increment)

Decide the increment by the largest change in the release, judged from the user's side:

- **major** (`1.0.0` → `2.0.0`) — a breaking change: an existing command/skill is removed or renamed, or its inputs/behavior change in a way that breaks current usage. While still on `0.x`, breaking changes go in **minor** instead (pre-1.0 has no stability promise).
- **minor** (`0.1.0` → `0.2.0`) — user-visible behavior changes or a new command/skill/feature is added, without breaking existing usage.
- **patch** (`0.1.0` → `0.1.1`) — no behavior change: typo/wording fixes, docs, internal refactors.

## CHANGELOG

- **Keep `CHANGELOG.md` in the plugin root**, in [Keep a Changelog](https://keepachangelog.com) format: reverse-chronological, a `## [Unreleased]` section on top **while changes are pending** (absent in a freshly released changelog), then one `## [x.y.z] - YYYY-MM-DD` section per release. Group lines under `Added` / `Changed` / `Fixed` / `Removed`, using only the ones that apply.
- **Write an entry for every user-impacting change** — a new, changed, or removed behavior of a command or skill, or of what the user reads and approves.
  - **Skip noise**: typo fixes, refactors, internal docs, pure formatting — anything a user would not notice gets no entry.
- **How to write each entry** — one line that states *what changed* and *the benefit to the user*, in terms a user understands (not commit or implementation language). Keep it concise: `<what changed> — <why it helps the user>`.
- **Where the entry goes:**
  - No release instruction → add the line under `## [Unreleased]` (the pending next release), creating that `## [Unreleased]` section at the top if the previous action was a release and it is absent.
  - A release instruction (cutting a version) → rename `## [Unreleased]` to the chosen `## [x.y.z] - YYYY-MM-DD` and bump `version` in `plugin.json` to match. **Do not leave an empty `## [Unreleased]` heading behind** — a released changelog starts at its latest version section; the `## [Unreleased]` section is re-created at the top only when the next user-facing change lands. Merging to `main` does not by itself bump the version — the bump happens only on this instruction.

## Release procedure (who does what)

On a release instruction, the assistant does every step **except the merge** — the merge to `main` is
the user's, because `main` is protected and only the user holds the privileges to clear its required
review. The order:

1. **Assistant** — bump `version` in `plugin.json` and finalize `CHANGELOG.md` (rename `## [Unreleased]`
   to the chosen `## [x.y.z] - YYYY-MM-DD`, leaving no empty `## [Unreleased]` behind), commit, and **push**.
2. **Assistant** — **request the user to merge** the PR to `main`. The assistant **never merges to
   `main` itself** and never uses `--admin` to bypass branch protection.
3. **User** — merges the PR to `main` and tells the assistant it is merged.
4. **Assistant** — once told the merge is done, **tags `main` and publishes the GitHub Release** as
   below (this part stays the assistant's).

## Tags and GitHub Releases

- **Tag each release on `main`** as `<plugin>--v<version>` (e.g. `rn--v0.2.0`), created with `claude plugin tag --push` from the plugin directory. This is Claude Code's own form: a plugin that depends on another with a version range resolves it against these tags, and the plugin-name prefix lets each plugin in this marketplace version independently. The command also validates the plugin and refuses a tag that already exists.
- **Publish a GitHub Release** for that tag, using the CHANGELOG's matching section as the notes.
- **Read release timing from tags / Releases, not from merge commits.** The merge to `main` delivers the code; the tag records which commit is which version, and when.

## Validation gate

- Structural validation must pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate <marketplace-root> --strict`.
- Confirm behavior headlessly: `claude -p "/<plugin>:<skill>" --plugin-dir <plugin-path>` (skill namespace = plugin name).
