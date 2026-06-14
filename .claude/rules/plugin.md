# Plugin authoring rules (ccpm)

Source: based on facts confirmed in the official docs (plugins-reference / plugin-marketplaces / skills at code.claude.com/docs).

## Version number

- **Write `version` in exactly one place: `plugin.json`.** Do not put `version` in `marketplace.json`.
  - Resolution order is `plugin.json` → marketplace entry → git commit SHA. **When both are set, `plugin.json` wins**, so a `version` in the marketplace entry is redundant and meaningless.
  - The top-level `version` in the marketplace is "manifest metadata" and is not used to detect updates for users.
- **Always set `version` in `plugin.json`** (semver, e.g. `0.1.0`).
  - `claude plugin validate --strict` warns and then fails when `version` is unset.
- **What it means (from the user's side):** pinning a version means users receive an update **only when you bump it**. Raise the version with each release.
  - Omitting it makes every commit a new release (the commit-SHA strategy, suited to active development), but to pass `--strict` this repo's policy is to keep `version` in `plugin.json`.

### How much to bump (semver increment)

Decide the increment by the largest change in the release, judged from the user's side:

- **major** (`1.0.0` → `2.0.0`) — a breaking change: an existing command/skill is removed or renamed, or its inputs/behavior change in a way that breaks current usage. While still on `0.x`, breaking changes go in **minor** instead (pre-1.0 has no stability promise).
- **minor** (`0.1.0` → `0.2.0`) — user-visible behavior changes or a new command/skill/feature is added, without breaking existing usage.
- **patch** (`0.1.0` → `0.1.1`) — no behavior change: typo/wording fixes, docs, internal refactors.

## CHANGELOG

- **Keep `CHANGELOG.md` in the plugin root**, in [Keep a Changelog](https://keepachangelog.com) format: reverse-chronological, a `## [Unreleased]` section on top, then one `## [x.y.z] - YYYY-MM-DD` section per release. Group lines under `Added` / `Changed` / `Fixed` / `Removed`, using only the ones that apply.
- **Write an entry for every user-impacting change** — a new, changed, or removed behavior of a command or skill, or of what the user reads and approves.
  - **Skip noise**: typo fixes, refactors, internal docs, pure formatting — anything a user would not notice gets no entry.
- **How to write each entry** — one line that states *what changed* and *the benefit to the user*, in terms a user understands (not commit or implementation language). Keep it concise: `<what changed> — <why it helps the user>`.
- **Where the entry goes:**
  - No release instruction → add the line under `## [Unreleased]` (the pending next release).
  - A release instruction (cutting a version) → rename `## [Unreleased]` to the chosen `## [x.y.z] - YYYY-MM-DD`, bump `version` in `plugin.json` to match, and open a fresh empty `## [Unreleased]`. On this repo `main` is the release channel, so cut the version when shipping to `main`.

## Validation gate

- Structural validation must pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate <marketplace-root> --strict`.
- Confirm behavior headlessly: `claude -p "/<plugin>:<skill>" --plugin-dir <plugin-path>` (skill namespace = plugin name).
